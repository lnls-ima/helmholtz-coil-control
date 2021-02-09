# -*- coding: utf-8 -*-

"""Measurement widget for the control application."""

import sys as _sys
import time as _time
import warnings as _warnings
import traceback as _traceback
import numpy as _np
import pyqtgraph as _pyqtgraph
from qtpy.QtWidgets import (
    QWidget as _QWidget,
    QMessageBox as _QMessageBox,
    QApplication as _QApplication,
    QProgressDialog as _QProgressDialog,
    )
from qtpy.QtCore import (
    Qt as _Qt,
    QTimer as _QTimer,
    QCoreApplication as _QCoreApplication,
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
    multimeter as _multimeter,
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

        self.te_names = [
            'comments',
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
            'gain_position_1',
            'gain_position_2',
        ]

        self.chb_names = [
            'measure_position_1',
            'measure_position_2',
        ]

        self.connect_signal_slots()
        self.load_last_db_entry()
        self.update_volume()

        self.stop = False
        self.block_volume = None
        self.offset_position_1 = None
        self.offset_position_2 = None
        self.integrated_voltage = []
        self.integrated_voltage_position_1 = []
        self.integrated_voltage_position_2 = []
        self.graph_position_1 = []
        self.graph_position_2 = []
        self.measurement_data = _measurement.MeasurementData()

        self.legend = _pyqtgraph.LegendItem(offset=(70, 30))
        self.legend.setParentItem(self.ui.pw_graph.graphicsItem())
        self.legend.setAutoFillBackground(1)

    @property
    def advanced_options(self):
        """Return global advanced options."""
        dialog = _QApplication.instance().advanced_options_dialog
        return dialog.config

    @property
    def scan_parameter_dialog(self):
        """Return scan parameter dialog."""
        return _QApplication.instance().scan_parameter_dialog

    @property
    def global_config(self):
        """Return the global measurement configuration."""
        return _QApplication.instance().measurement_config

    @global_config.setter
    def global_config(self, value):
        _QApplication.instance().measurement_config = value

    def clear(self):
        """Clear."""
        self.stop = False
        self.block_volume = None
        self.offset_position_1 = None
        self.offset_position_2 = None
        self.integrated_voltage = []
        self.integrated_voltage_position_1 = []
        self.integrated_voltage_position_2 = []
        self.ui.le_avg_mx.setText('')
        self.ui.le_avg_my.setText('')
        self.ui.le_avg_mz.setText('')
        self.ui.le_std_mx.setText('')
        self.ui.le_std_my.setText('')
        self.ui.le_std_mz.setText('')
        self.ui.pgb_status.setValue(0)
        self.measurement_data.clear()
        self.clear_graph()

    def clear_graph(self):
        """Clear plots."""
        self.ui.pw_graph.plotItem.curves.clear()
        self.ui.pw_graph.clear()
        self.graph_position_1 = []
        self.graph_position_2 = []

    def configure_driver(self, steps):
        try:
            _driver.stop_motor(
                self.advanced_options.motor_driver_address)
            _time.sleep(0.1)

            return _driver.config_motor(
                self.advanced_options.motor_driver_address,
                0,
                self.advanced_options.motor_rotation_direction,
                self.advanced_options.motor_resolution,
                self.advanced_options.motor_velocity,
                self.advanced_options.motor_acceleration,
                steps)

        except Exception:
            msg = _QCoreApplication.translate(
                '', 'Failed to configure driver.')
            title = _QCoreApplication.translate('', 'Failure')
            _QMessageBox.critical(self, title, msg, _QMessageBox.Ok)
            _traceback.print_exc(file=_sys.stdout)
            return False

    def configure_graph(self, nr_curves):
        """Configure graph."""
        self.clear_graph()
        self.legend.removeItem('Position 1')
        self.legend.removeItem('Position 2')

        for idx in range(nr_curves):
            self.graph_position_1.append(
                self.ui.pw_graph.plotItem.plot(
                    _np.array([]),
                    _np.array([]),
                    pen=(0, 255, 0),
                    symbol='o',
                    symbolPen=(0, 255, 0),
                    symbolSize=4,
                    symbolBrush=(0, 255, 0)))

            self.graph_position_2.append(
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
        self.legend.addItem(self.graph_position_1[0], 'Position 1')
        self.legend.addItem(self.graph_position_2[0], 'Position 2')

    def configure_integrator(self, gain):
        try:
            return _integrator.configure_measurement(
                self.advanced_options.integrator_channel,
                self.advanced_options.integrator_encoder_resolution,
                self.advanced_options.integrator_encoder_direction,
                self.advanced_options.integration_trigger,
                self.advanced_options.integration_points,
                self.advanced_options.integration_nr_turns,
                gain)

        except Exception:
            msg = _QCoreApplication.translate(
                '', 'Failed to configure integrator.')
            title = _QCoreApplication.translate('', 'Failure')
            _QMessageBox.critical(self, title, msg, _QMessageBox.Ok)
            _traceback.print_exc(file=_sys.stdout)
            return False

    def check_device_connection(self):
        if not _integrator.connected:
            msg = _QCoreApplication.translate(
                '', 'Integrator not connected.')
            title = _QCoreApplication.translate('', 'Failure')
            _QMessageBox.critical(self, title, msg, _QMessageBox.Ok)
            return False

        if not _driver.connected:
            msg = _QCoreApplication.translate(
                '', 'Driver not connected.')
            title = _QCoreApplication.translate('', 'Failure')
            _QMessageBox.critical(self, title, msg, _QMessageBox.Ok)
            return False

        return True

    def check_advanced_options(self):
        if not self.advanced_options.valid_data():
            msg = _QCoreApplication.translate(
                '', 'Invalid advanced options.')
            title = _QCoreApplication.translate('', 'Failure')
            _QMessageBox.critical(self, title, msg, _QMessageBox.Ok)
            return False

        return True

    def configure_measurement(self):
        self.clear()

        try:
            if not self.check_device_connection():
                return False

            if not self.check_advanced_options():
                return False

            if not self.update_configuration():
                return False

            if not self.save_db():
                return False

            self.global_config = self.config.copy()
            self.offset_position_1 = 0
            self.offset_position_2 = 0
            self.block_volume = float(self.ui.le_block_volume.text())

            if self.block_volume == 0:
                msg = _QCoreApplication.translate(
                    '', 'Invalid block volume.')
                title = _QCoreApplication.translate('', 'Failure')
                _QMessageBox.critical(self, title, msg, _QMessageBox.Ok)
                return False

            self.configure_graph(
                self.advanced_options.integration_nr_turns)

            return True

        except Exception:
            msg = _QCoreApplication.translate(
                '', 'Measurement configuration failed.')
            title = _QCoreApplication.translate('', 'Failure')
            _QMessageBox.critical(self, title, msg, _QMessageBox.Ok)
            _traceback.print_exc(file=_sys.stdout)
            return False

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
        self.ui.pbt_start_measurement.clicked.connect(self.start_measurements)
        self.ui.pbt_stop_measurement.clicked.connect(self.stop_measurement)
        self.ui.tbt_read_temperature.clicked.connect(self.read_temperature)
        self.ui.pbt_clear_results.clicked.connect(self.clear)
        self.ui.chb_show_position_1.stateChanged.connect(
            self.plot_integrated_voltage)
        self.ui.chb_show_position_2.stateChanged.connect(
            self.plot_integrated_voltage)
        self.ui.chb_scan_parameter.stateChanged.connect(
            self.enable_scan_configuration)
        self.ui.pbt_configure_scan.clicked.connect(
            self.show_scan_parameter_dialog)

    def enable_scan_configuration(self):
        if self.ui.chb_scan_parameter.isChecked():
            self.ui.pbt_configure_scan.setEnabled(True)
        else:
            self.ui.pbt_configure_scan.setEnabled(False)

    def show_scan_parameter_dialog(self):
        self.scan_parameter_dialog.show()

    def homing(self, nr_turns=1):
        try:
            if self.stop:
                return False

            wait = 0.1

            steps = int(self.advanced_options.motor_resolution*nr_turns)
            encoder_direction = (
                self.advanced_options.integrator_encoder_direction)
            driver_address = self.advanced_options.motor_driver_address

            if not self.configure_driver(steps):
                return False

            _integrator.configure_homing(encoder_direction)

            if self.stop:
                return False

            _driver.move_motor(driver_address)
            _time.sleep(wait)
            while not _driver.ready(driver_address) and not self.stop:
                _time.sleep(wait)
                _QApplication.processEvents()

            if self.stop:
                return False

            return True

        except Exception:
            msg = _QCoreApplication.translate(
                '', 'Homing failed.')
            title = _QCoreApplication.translate('', 'Failure')
            _QMessageBox.critical(self, title, msg, _QMessageBox.Ok)
            _traceback.print_exc(file=_sys.stdout)
            return False

    def load(self):
        """Load configuration to set parameters."""
        try:
            rbt_name = 'rbt_' + self.config.volume_input
            rbt = getattr(self.ui, rbt_name)
            rbt.setChecked(True)
            super().load()

        except Exception:
            _traceback.print_exc(file=_sys.stdout)

    def measure_position(self, gain):
        try:
            if self.stop:
                return False

            self.integrated_voltage = []

            steps = int((self.advanced_options.integration_nr_turns + 1)*(
                self.advanced_options.motor_resolution))

            if not self.configure_integrator(gain):
                return False

            if not self.configure_driver(steps):
                return False

            driver_address = self.advanced_options.motor_driver_address
            nr_turns = self.advanced_options.integration_nr_turns
            integration_points = self.advanced_options.integration_points
            total_npts = nr_turns*integration_points

            if total_npts > 100:
                step_status = int(total_npts/20)
            elif total_npts > 50:
                step_status = int(total_npts/10)
            else:
                step_status = 1

            if not _integrator.start_measurement():
                msg = _QCoreApplication.translate(
                    '', 'Incorrect integrator status.')
                title = _QCoreApplication.translate('', 'Failure')
                _QMessageBox.critical(
                    self, title, msg, _QMessageBox.Ok)
                return False

            if self.stop:
                return False

            _driver.move_motor(driver_address)

            self.ui.pgb_status.setMinimum(0)
            self.ui.pgb_status.setMaximum(total_npts)
            self.ui.pgb_status.setValue(0)

            count = 0
            while (count < total_npts) and (not self.stop):
                _QApplication.processEvents()
                count = _integrator.get_data_count()
                if count % step_status == 0:
                    self.ui.pgb_status.setValue(count)
            data = _integrator.get_data_array()
            if any(_np.isnan(di) for di in data):
                msg = _QCoreApplication.translate(
                    '', (
                    'Integrator over-range.\n' +
                    'Please configure a lower gain.'
                    ))
                title = _QCoreApplication.translate('', 'Warning')
                _QMessageBox.warning(self, title, msg, _QMessageBox.Ok)
                return False

            if self.stop:
                return False

            self.ui.pgb_status.setValue(total_npts)

            integrated_voltage = _np.array(data).reshape(
                nr_turns, integration_points).transpose()

            self.integrated_voltage = integrated_voltage*(
                _integrator.conversion_factor)

            if self.stop:
                return False

            return True

        except Exception:
            _traceback.print_exc(file=_sys.stdout)
            _driver.stop_motor(
                self.advanced_options.motor_driver_address)
            self.ui.pgb_status.setValue(0)
            msg = _QCoreApplication.translate(
                '', 'Measurement failed.')
            title = _QCoreApplication.translate('', 'Failure')
            _QMessageBox.critical(self, title, msg, _QMessageBox.Ok)
            return False

    def move_to_initial_position(self):
        try:
            if self.stop:
                return False
            
            trigger = self.advanced_options.integration_trigger
            encoder_res = self.advanced_options.integrator_encoder_resolution
            motor_resolution = self.advanced_options.motor_resolution
            rotation_direction = self.advanced_options.motor_rotation_direction
            driver_address = self.advanced_options.motor_driver_address

            wait = 0.3
            tol = encoder_res/10

            _time.sleep(wait)

            current_position = int(_integrator.read_encoder())
            position = trigger

            if _np.abs(current_position - position) <= tol:
                return True

            diff = (current_position - position)
            if rotation_direction == '-':
                diff = diff*(-1)
            pulses = (encoder_res - diff) % encoder_res
            steps = int((pulses*motor_resolution)/encoder_res)

            if not self.configure_driver(steps):
                return False

            if self.stop:
                return False

            _driver.move_motor(driver_address)
            _time.sleep(wait)

            while not _driver.ready(driver_address) and not self.stop:
                _time.sleep(wait)
                _QApplication.processEvents()

            _time.sleep(wait)

            if self.stop:
                return False

            return True

        except Exception:
            msg = _QCoreApplication.translate(
                '', 'Failed to move motor to initial position.')
            title = _QCoreApplication.translate('', 'Failure')
            _QMessageBox.critical(self, title, msg, _QMessageBox.Ok)
            _traceback.print_exc(file=_sys.stdout)
            return False

    def move_half_turn(self):
        try:
            if self.stop:
                return False

            wait = 0.3
            
            _time.sleep(wait)

            motor_resolution = self.advanced_options.motor_resolution
            driver_address = self.advanced_options.motor_driver_address
            steps = int(int(motor_resolution)*0.5)

            if not self.configure_driver(steps):
                return False

            if self.stop:
                return False

            _driver.move_motor(driver_address)
            _time.sleep(wait)

            while not _driver.ready(driver_address) and not self.stop:
                _time.sleep(wait)
                _QApplication.processEvents()

            _time.sleep(wait)

            if self.stop:
                return False

            return True

        except Exception:
            msg = _QCoreApplication.translate(
                '', 'Failed to move motor to initial position.')
            title = _QCoreApplication.translate('', 'Failure')
            _QMessageBox.critical(self, title, msg, _QMessageBox.Ok)
            _traceback.print_exc(file=_sys.stdout)
            return False

    def plot_integrated_voltage(self):
        """Plot integrated voltage values."""
        with _warnings.catch_warnings():
            _warnings.simplefilter("ignore")

            show_position_1 = (
                self.ui.chb_show_position_1.isChecked() *
                len(self.integrated_voltage_position_1))

            show_position_2 = (
                self.ui.chb_show_position_2.isChecked() *
                len(self.integrated_voltage_position_2))

            if show_position_1:
                n1 = self.integrated_voltage_position_1.shape[1]
                for idx in range(n1):
                    self.graph_position_1[idx].setData(
                        self.integrated_voltage_position_1[:, idx])
            else:
                for curve in self.graph_position_1:
                    curve.clear()

            if show_position_2:
                n2 = self.integrated_voltage_position_2.shape[1]
                for idx in range(n2):
                    self.graph_position_2[idx].setData(
                        self.integrated_voltage_position_2[:, idx])
            else:
                for curve in self.graph_position_2:
                    curve.clear()

    def read_temperature(self):
        try:
            if not _multimeter.connected:
                msg = _QCoreApplication.translate(
                    '', 'Multimeter not connected.')
                title = _QCoreApplication.translate('', 'Failure')
                _QMessageBox.critical(self, title, msg, _QMessageBox.Ok)
                return False

            msg = _QCoreApplication.translate(
                '', 'Place temperature sensor on the magnet.')
            title = _QCoreApplication.translate('', 'Information')
            _QMessageBox.information(self, title, msg, _QMessageBox.Ok)

            _multimeter.config_resistance_4w(wait=0.5)

            nr_readings = self.advanced_options.temperature_nr_readings
            freq = self.advanced_options.temperature_reading_frequency

            msg = _QCoreApplication.translate(
                '', 'Measuring temperature...')
            prg_dialog = _QProgressDialog(
                msg, _QCoreApplication.translate('', 'Stop'), 0, nr_readings)
            prg_dialog.setWindowTitle(_QCoreApplication.translate(
                '', 'Information'))
            prg_dialog.autoClose()
            prg_dialog.show()

            temperature_list = []
            for i in range(nr_readings):
                reading = _multimeter.read()
                temperature = _multimeter.pt100_resistance_to_temperature(
                    reading)
                temperature_list.append(temperature)

                for j in range(10):
                    _time.sleep(1/freq/10)
                    _QApplication.processEvents()

                if prg_dialog.wasCanceled():
                    break

                prg_dialog.setValue(i+1)

            if len(temperature_list) == 0:
                temperature_avg = 0
            else:
                temperature_avg = _np.mean(temperature_list)

            self.ui.sbd_block_temperature.setValue(temperature_avg)
            self.config.block_temperature = temperature_avg

        except Exception:
            msg = _QCoreApplication.translate(
                '', 'Failed to read temperature.')
            title = _QCoreApplication.translate('', 'Failure')
            _QMessageBox.critical(self, title, msg, _QMessageBox.Ok)
            _traceback.print_exc(file=_sys.stdout)
            return False

    def save_measurement_data(self):
        try:
            if self.database_name is None:
                msg = _QCoreApplication.translate(
                    '', 'Invalid database filename.')
                title = _QCoreApplication.translate('', 'Failure')
                _QMessageBox.critical(
                    self, title, msg, _QMessageBox.Ok)
                return False

            self.measurement_data.db_update_database(
                self.database_name,
                mongo=self.mongo, server=self.server)
            self.measurement_data.db_save()
            return True

        except Exception:
            _traceback.print_exc(file=_sys.stdout)
            msg = _QCoreApplication.translate(
                '', 'Failed to save measurement to database.')
            title = _QCoreApplication.translate('', 'Failure')
            _QMessageBox.critical(self, title, msg, _QMessageBox.Ok)
            return False

    def start_measurements(self):
        if not self.configure_measurement():
            return False

        self.ui.pbt_start_measurement.setEnabled(False)
        _QApplication.processEvents()

        if self.ui.chb_scan_parameter.isChecked():
            if not self.scan_parameter_dialog.valid_scan:
                msg = _QCoreApplication.translate(
                    '', 'Invalid scan configuration.')
                title = _QCoreApplication.translate('', 'Failure')
                _QMessageBox.critical(
                    self, title, msg, _QMessageBox.Ok)
                return False
            else:
                try:
                    scan_parameter = self.scan_parameter_dialog.scan_parameter
                    scan_values = self.scan_parameter_dialog.scan_values

                    for value in scan_values:
                        setattr(self.advanced_options, scan_parameter, value)
                        setattr(self.advanced_options, 'date', None)
                        setattr(self.advanced_options, 'hour', None)
                        self.advanced_options.db_save()
                        self.start_one_measurement(silent=True)

                except Exception:
                    msg = _QCoreApplication.translate(
                        '', 'Set of measurements failed.')
                    title = _QCoreApplication.translate('', 'Failure')
                    _QMessageBox.critical(
                        self, title, msg, _QMessageBox.Ok)
                    return False
        else:
            if not self.start_one_measurement():
                return False

        self.ui.pbt_start_measurement.setEnabled(True)
        _QApplication.processEvents()

        msg = _QCoreApplication.translate(
            '', 'End of measurement.')
        title = _QCoreApplication.translate('', 'Information')
        _QMessageBox.information(
            self, title, msg, _QMessageBox.Ok)

        return True

    def start_one_measurement(self, silent=False):
        if not self.move_to_initial_position():
            return False          

        if self.global_config.measure_position_1:
            if not silent:
                msg = _QCoreApplication.translate(
                    '', 'Place the magnet in Position 1.')
                title = _QCoreApplication.translate('', 'Information')
                _QMessageBox.information(
                    self, title, msg, _QMessageBox.Ok)

            if not self.move_half_turn():
                return False  

            gain = self.global_config.gain_position_1
            if not self.measure_position(gain=gain):
                self.ui.pbt_start_measurement.setEnabled(True)
                return False

            self.integrated_voltage_position_1 = _np.array(
                self.integrated_voltage)

        if self.stop:
            return False

        if self.global_config.measure_position_2:
            if not silent:
                msg = _QCoreApplication.translate(
                    '', 'Place the magnet in Position 2.')
                title = _QCoreApplication.translate('', 'Information')
                _QMessageBox.information(
                    self, title, msg, _QMessageBox.Ok)

            if not self.move_half_turn():
                return False 

            gain = self.global_config.gain_position_2
            if not self.measure_position(gain=gain):
                self.ui.pbt_start_measurement.setEnabled(True)
                return False

            self.integrated_voltage_position_2 = _np.array(
                self.integrated_voltage)

        if self.stop:
            return False

        gc = self.global_config
        self.measurement_data.block_name = gc.block_name
        self.measurement_data.block_temperature = gc.block_temperature
        self.measurement_data.advanced_options_id = self.advanced_options.idn
        self.measurement_data.configuration_id = gc.idn
        self.measurement_data.comments = gc.comments

        m, mstd = self.measurement_data.set_magnetization_components(
            self.integrated_voltage_position_1,
            self.integrated_voltage_position_2,
            self.offset_position_1,
            self.offset_position_2,
            self.advanced_options.coil_radius*1e-3,
            self.advanced_options.coil_distance_center*1e-3,
            self.advanced_options.coil_turns,
            self.block_volume*1e-9)

        if not self.save_measurement_data():
            return False

        self.update_magnetization_values(m, mstd)

        self.plot_integrated_voltage()

        if not self.move_to_initial_position():
            return False

        if self.stop:
            return False

        return True

    def update_magnetization_values(self, m, mstd):
        fmt_avg = '{0:.6f}'
        self.ui.le_avg_mx.setText(fmt_avg.format(m[0]))
        self.ui.le_avg_my.setText(fmt_avg.format(m[1]))
        self.ui.le_avg_mz.setText(fmt_avg.format(m[2]))

        fmt_std = '{0:.2g}'
        self.ui.le_std_mx.setText(fmt_std.format(mstd[0]))
        self.ui.le_std_my.setText(fmt_std.format(mstd[1]))
        self.ui.le_std_mz.setText(fmt_std.format(mstd[2]))

    def stop_measurement(self):
        try:
            self.stop = True
            self.ui.pbt_start_measurement.setEnabled(True)
            _driver.stop_motor(
                self.advanced_options.motor_driver_address)
            msg = _QCoreApplication.translate(
                '', 'The user stopped the measurements.')
            title = _QCoreApplication.translate('', 'Abort')
            _QMessageBox.information(
                self, title, msg, _QMessageBox.Ok)

        except Exception:
            self.stop = True
            _traceback.print_exc(file=_sys.stdout)
            msg = _QCoreApplication.translate(
                '', 'Failed to stop measurements.')
            title = _QCoreApplication.translate('', 'Failure')
            _QMessageBox.critical(self, title, msg, _QMessageBox.Ok)

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
