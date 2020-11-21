# -*- coding: utf-8 -*-

"""Measurement widget for the control application."""

import sys as _sys
import numpy as _np
import time as _time
import warnings as _warnings
import traceback as _traceback
import pyqtgraph as _pyqtgraph
from qtpy.QtWidgets import (
    QWidget as _QWidget,
    QMessageBox as _QMessageBox,
    QApplication as _QApplication,
    )
from qtpy.QtCore import (
    Qt as _Qt,
    QTimer as _QTimer
)
import qtpy.uic as _uic

from helmholtz.gui import utils as _utils
from helmholtz.gui.auxiliarywidgets import (
    ConfigurationWidget as _ConfigurationWidget
    )
import helmholtz.data.configuration as _configuration
import helmholtz.data.measurement as _measurement
from helmholtz.devices import (
    driver as _driver,
    integrator as _integrator,
)


class MeasurementWidget(_ConfigurationWidget):
    """Measurement widget class for the control application."""

    def __init__(self, parent=None):
        """Set up the ui."""
        uifile = _utils.get_ui_file(self)
        config = _configuration.MeasurementConfig()
        super().__init__(uifile, config, parent=parent)

        self.le_names = [
            'block_name',
        ]

        self.sbd_names = [
            'block_temperature',
            'block_volume',
            'block_dimension1',
            'block_dimension2',
            'block_dimension3',
            'block_mass',
            'density',
        ]

        self.cmb_names = [
            'main_component',
            'main_component_gain',
            'residual_component_gain',
        ]

        self.connect_signal_slots()
        self.load_last_db_entry()
        self.update_volume()

        self.stop = False
        self.block_volume = None
        self.gain_part1 = None
        self.gain_part2 = None
        self.offset_part1 = None
        self.offset_part2 = None
        self.integrated_voltage = []
        self.integrated_voltage_part1 = []
        self.integrated_voltage_part2 = []
        self.measurement_data = _measurement.MeasurementData()
        self.graphx = []
        self.graphy = []
        self.graphz = []

        self.legend = _pyqtgraph.LegendItem(offset=(70, 30))
        self.legend.setParentItem(self.ui.pw_graph.graphicsItem())
        self.legend.setAutoFillBackground(1)

    @property
    def global_motor_integrator_config(self):
        """Return the motor and encoder global configuration."""
        return _QApplication.instance().motor_integrator_config

    @property
    def global_measurement_config(self):
        """Return the global measurement configuration."""
        return _QApplication.instance().measurement_config

    @global_measurement_config.setter
    def global_measurement_config(self, value):
        _QApplication.instance().measurement_config = value

    def clear(self):
        """Clear."""
        self.stop = False
        self.block_volume = None
        self.gain_part1 = None
        self.gain_part2 = None
        self.offset_part1 = None
        self.offset_part2 = None
        self.integrated_voltage = []
        self.integrated_voltage_part1 = []
        self.integrated_voltage_part2 = []
        self.clear_results()

    def clear_results(self):
        self.ui.le_avg_mx.setText('')
        self.ui.le_avg_my.setText('')
        self.ui.le_avg_mz.setText('')
        self.ui.le_std_mx.setText('')
        self.ui.le_std_my.setText('')
        self.ui.le_std_mz.setText('')
        self.clear_graph()

    def clear_graph(self):
        """Clear plots."""
        self.ui.pw_graph.plotItem.curves.clear()
        self.ui.pw_graph.clear()
        self.graphx = []
        self.graphy = []
        self.graphz = []

    def connect_signal_slots(self):
        """Create signal/slot connections."""
        super().connect_signal_slots()
        self.ui.sbd_block_volume.valueChanged.connect(self.update_volume)
        self.ui.sbd_block_dimension1.valueChanged.connect(self.update_volume)
        self.ui.sbd_block_dimension2.valueChanged.connect(self.update_volume)
        self.ui.sbd_block_dimension3.valueChanged.connect(self.update_volume)
        self.ui.sbd_block_mass.valueChanged.connect(self.update_volume)
        self.ui.sbd_density.valueChanged.connect(self.update_volume)
        self.ui.rbt_volume.toggled.connect(self.update_volume_page)
        self.ui.rbt_size.toggled.connect(self.update_volume_page)
        self.ui.rbt_mass.toggled.connect(self.update_volume_page)
        self.ui.pbt_start_measurement.clicked.connect(self.start_measurement)
        self.ui.pbt_stop_measurement.clicked.connect(self.stop_measurement)

    def configure_graph(self, nr_curves):
        """Configure graph."""
        self.clear_graph()
        self.legend.removeItem('X')
        self.legend.removeItem('Y')
        self.legend.removeItem('Z')

        for idx in range(nr_curves):
            self.graphx.append(
                self.ui.pw_graph.plotItem.plot(
                    _np.array([]),
                    _np.array([]),
                    pen=(255, 0, 0),
                    symbol='o',
                    symbolPen=(255, 0, 0),
                    symbolSize=4,
                    symbolBrush=(255, 0, 0)))

            self.graphy.append(
                self.ui.pw_graph.plotItem.plot(
                    _np.array([]),
                    _np.array([]),
                    pen=(0, 255, 0),
                    symbol='o',
                    symbolPen=(0, 255, 0),
                    symbolSize=4,
                    symbolBrush=(0, 255, 0)))

            self.graphz.append(
                self.ui.pw_graph.plotItem.plot(
                    _np.array([]),
                    _np.array([]),
                    pen=(0, 0, 255),
                    symbol='o',
                    symbolPen=(0, 0, 255),
                    symbolSize=4,
                    symbolBrush=(0, 0, 255)))

        self.ui.pw_graph.setLabel('bottom', 'Integration Points')
        self.ui.pw_graph.setLabel('left', 'Integrated Voltage [V.s]')
        self.ui.pw_graph.showGrid(x=True, y=True)
        self.legend.addItem(self.graphx[0], 'X')
        self.legend.addItem(self.graphy[0], 'Y')
        self.legend.addItem(self.graphz[0], 'Z')

    def plot_integrated_voltage(self):
        """Plot integrated voltage values."""
        with _warnings.catch_warnings():
            _warnings.simplefilter("ignore")
            nc = self.integrated_voltage_part1.shape[1]
            for idx in range(nc):
                self.graphy[idx].setData(
                    self.integrated_voltage_part1[:, idx])
                self.graphz[idx].setData(
                    self.integrated_voltage_part2[:, idx])

    def homing(self):
        try:
            motor_config = self.global_motor_integrator_config
            wait = 0.1

            steps = int(int(motor_config.motor_resolution)*1.25)
            encoder_direction = motor_config.encoder_direction,
            driver_address = motor_config.driver_address

            _integrator.send_command(_integrator.commands.reset_counter)
            _time.sleep(wait)

            if not _driver.config_motor(
                    driver_address,
                    0,
                    motor_config.motor_direction,
                    motor_config.motor_resolution,
                    motor_config.motor_velocity,
                    motor_config.motor_acceleration,
                    steps):
                msg = 'Failed to send configuration to motor.'
                _QMessageBox.critical(
                    self, 'Failure', msg, _QMessageBox.Ok)
                return False

            _integrator.configure_homing(encoder_direction)

            if self.stop:
                return False

            _driver.move_motor(driver_address)
            _time.sleep(wait)
            while not _driver.ready(driver_address) and not self.stop:
                _time.sleep(wait)
                _QApplication.processEvents()

            return True

        except Exception:
            msg = 'Homing failed.'
            _QMessageBox.critical(self, 'Failure', msg, _QMessageBox.Ok)
            _traceback.print_exc(file=_sys.stdout)
            return False

    def configure_integrator(self, gain):
        try:
            meas_config = self.global_measurement_config
            motor_config = self.global_motor_integrator_config

            nr_intervals = meas_config.integration_points*meas_config.nr_turns
            interval_size = int(
                motor_config.encoder_resolution/meas_config.integration_points)

            return _integrator.configure_measurement(
                motor_config.integrator_channel,
                motor_config.encoder_resolution,
                motor_config.encoder_direction,
                meas_config.trigger,
                nr_intervals,
                interval_size,
                gain)

        except Exception:
            msg = 'Failed to configure integrator.'
            _QMessageBox.critical(self, 'Failure', msg, _QMessageBox.Ok)
            _traceback.print_exc(file=_sys.stdout)
            return False

    def configure_driver(self):
        try:
            meas_config = self.global_measurement_config
            motor_config = self.global_motor_integrator_config
            steps = (meas_config.nr_turns + 2)*motor_config.motor_resolution

            return _driver.config_motor(
                motor_config.driver_address,
                0,
                motor_config.motor_direction,
                motor_config.motor_resolution,
                motor_config.motor_velocity,
                motor_config.motor_acceleration,
                steps)

        except Exception:
            msg = 'Failed to configure driver.'
            _QMessageBox.critical(self, 'Failure', msg, _QMessageBox.Ok)
            _traceback.print_exc(file=_sys.stdout)
            return False

    def start_measurement(self):
        self.clear()

        try:
            if not _integrator.connected:
                msg = 'Integrator not connected.'
                _QMessageBox.critical(self, 'Failure', msg, _QMessageBox.Ok)
                return False

            if not _driver.connected:
                msg = 'Driver not connected.'
                _QMessageBox.critical(self, 'Failure', msg, _QMessageBox.Ok)
                return False

            if not self.update_configuration():
                return False

            if not self.save_db():
                return False

            if self.config.main_component == 'horizontal':
                self.gain_part1 = self.config.main_component_gain
                self.gain_part2 = self.config.residual_component_gain

            elif self.config.main_component == 'vertical':
                self.gain_part1 = self.config.main_component_gain
                self.gain_part2 = self.config.residual_component_gain

            elif self.config.main_component == 'longitudinal':
                self.gain_part1 = self.config.residual_component_gain
                self.gain_part2 = self.config.main_component_gain

            self.offset_part1 = 0
            self.offset_part2 = 0

            self.block_volume = float(self.ui.le_block_volume.text())
            self.global_measurement_config = self.config.copy()

        except Exception:
            msg = 'Measurement configuration failed.'
            _QMessageBox.critical(self, 'Failure', msg, _QMessageBox.Ok)
            _traceback.print_exc(file=_sys.stdout)
            return False

        self.configure_graph(
            self.global_measurement_config.nr_turns)
        self.ui.pbt_start_measurement.setEnabled(False)
        _QApplication.processEvents()

        if not self.measure_part1():
            self.ui.pbt_start_measurement.setEnabled(True)
            return False

        self.integrated_voltage_part2 = self.integrated_voltage_part1

        msg = 'Rotate block.'
        _QMessageBox.information(self, 'Information', msg, _QMessageBox.Ok)

        if not self.measure_part2():
            self.ui.pbt_start_measurement.setEnabled(True)
            return False

        self.plot_integrated_voltage()

        m, mstd = self.measurement_data.get_magnetization_components(
            self.global_measurement_config.main_component,
            self.integrated_voltage_part1*_integrator.conversion_factor,
            self.integrated_voltage_part2*_integrator.conversion_factor,
            0, 0,
            self.global_measurement_config.coil_turns,
            self.global_measurement_config.coil_radius*1e-3,
            self.global_measurement_config.coil_distance_center*1e-3,
            self.block_volume*1e-9)

        self.ui.le_avg_mx.setText(str(m[0]))
        self.ui.le_avg_my.setText(str(m[1]))
        self.ui.le_avg_mz.setText(str(m[2]))

        self.ui.le_std_mx.setText(str(mstd[0]))
        self.ui.le_std_my.setText(str(mstd[1]))
        self.ui.le_std_mz.setText(str(mstd[2]))

        self.ui.pbt_start_measurement.setEnabled(True)
        _QApplication.processEvents()

        msg = 'End of measurement.'
        _QMessageBox.information(
            self, 'Measurement', msg, _QMessageBox.Ok)

        return True

    def measure_part1(self):
        if self.stop:
            return False

        if not self.measure(gain=self.gain_part1):
            return False

        self.integrated_voltage_part1 = _np.array([
            iv for iv in self.integrated_voltage])

        _np.savetxt(
            'C:\\Users\\labimas\\Desktop\\test_software\\iv1.txt',
            self.integrated_voltage_part1)

        return True

    def measure_part2(self):
        if self.stop:
            return False

        if not self.measure(gain=self.gain_part2):
            return False

        self.integrated_voltage_part2 = _np.array([
            iv for iv in self.integrated_voltage])
        return True

    def measure(self, gain):
        if self.stop:
            return False

        try:
            wait = 0.1
            self.integrated_voltage = []

            if not self.global_motor_integrator_config.valid_data():
                msg = 'Motor and integrator parameters not configured.'
                _QMessageBox.critical(self, 'Failure', msg, _QMessageBox.Ok)
                return False

            if not self.configure_integrator(gain):
                return False

            if not self.homing():
                return False

            if not self.configure_driver():
                return False

            _integrator.read_from_device()
            _time.sleep(wait)

            _integrator.send_command(
                _integrator.commands.stop_measurement)
            _integrator.read_from_device()
            _time.sleep(wait)

            _integrator.send_command(
                _integrator.commands.start_measurement)
            _time.sleep(wait)

            _driver.move_motor(
                self.global_motor_integrator_config.driver_address)

            integrated_voltage = []
            finished = False
            while (not finished) and (not self.stop):
                tmp = _integrator.read_from_device()
                if 'A' in tmp:
                    valor = float(tmp.replace('A',''))
                    integrated_voltage.append(valor)
                    _QApplication.processEvents()
                elif tmp == '\x1a':
                    finished = True

            integrated_voltage = _np.array(integrated_voltage).reshape(
                self.global_measurement_config.integration_points,
                self.global_measurement_config.nr_turns)

            self.integrated_voltage = integrated_voltage

            return True

        except Exception:
            _traceback.print_exc(file=_sys.stdout)
            msg = 'Measurement failed.'
            _QMessageBox.critical(self, 'Failure', msg, _QMessageBox.Ok)
            return False

    def stop_measurement(self):
        try:
            self.stop = True
            self.ui.pbt_start_measurement.setEnabled(True)
            msg = 'The user stopped the measurements.'
            _QMessageBox.information(
                self, 'Abort', msg, _QMessageBox.Ok)

        except Exception:
            self.stop = True
            _traceback.print_exc(file=_sys.stdout)
            msg = 'Failed to stop measurements.'
            _QMessageBox.critical(self, 'Failure', msg, _QMessageBox.Ok)

    def update_volume_page(self):
        try:
            if self.ui.rbt_volume.isChecked():
                self.ui.stw_volume.setCurrentIndex(0)
            elif self.ui.rbt_size.isChecked():
                self.ui.stw_volume.setCurrentIndex(1)
            elif self.ui.rbt_mass.isChecked():
                self.ui.stw_volume.setCurrentIndex(2)
            self.update_volume()
        except Exception:
            _traceback.print_exc(file=_sys.stdout)

    def update_volume(self):
        try:
            vstr = ''
            fmt = '{0:.3f}'
            if self.ui.rbt_volume.isChecked():
                v = self.ui.sbd_block_volume.value()
                vstr = fmt.format(v)

            elif self.ui.rbt_size.isChecked():
                d1 = self.ui.sbd_block_dimension1.value()
                d2 = self.ui.sbd_block_dimension2.value()
                d3 = self.ui.sbd_block_dimension3.value()
                vstr = fmt.format(d1*d2*d3)

            elif self.ui.rbt_mass.isChecked():
                m = self.ui.sbd_block_mass.value()
                d = self.ui.sbd_density.value()/1000
                vstr = fmt.format(m/d)

            self.ui.le_block_volume.setText(vstr)
        except Exception:
            _traceback.print_exc(file=_sys.stdout)

    def load(self):
        """Load configuration to set parameters."""
        try:
            rbt_name = 'rbt_' + self.config.volume_input
            rbt = getattr(self.ui, rbt_name)
            rbt.setChecked(True)
            super().load()

        except Exception:
            _traceback.print_exc(file=_sys.stdout)

    def update_configuration(self):
        """Update configuration parameters."""
        try:
            if self.ui.rbt_volume.isChecked():
                self.config.volume_input = 'volume'
            elif self.ui.rbt_size.isChecked():
                self.config.volume_input = 'size'
            elif self.ui.rbt_mass.isChecked():
                self.config.volume_input = 'mass'
            return super().update_configuration(clear=False)

        except Exception:
            _traceback.print_exc(file=_sys.stdout)
            self.config.clear()
            return False
