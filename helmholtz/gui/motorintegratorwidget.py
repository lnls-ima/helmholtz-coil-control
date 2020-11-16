# -*- coding: utf-8 -*-

"""Motor and integrator widget for the control application."""

import os as _os
import sys as _sys
import traceback as _traceback
import serial.tools.list_ports as _list_ports
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
from helmholtz.devices import (
    driver as _driver,
    integrator as _integrator,
)

class MotorIntegratorWidget(_ConfigurationWidget):
    """Motor and integrator widget class for the control application."""

    _update_encoder_interval = _utils.UPDATE_ENCODER_INTERVAL

    def __init__(self, parent=None):
        """Set up the ui."""
        uifile = _utils.get_ui_file(self)
        config = _configuration.MotorIntegratorConfig()
        super().__init__(uifile, config, parent=parent)
        
        self.connect_signal_slots()

        self.stop_encoder_update = True
        self.timer = _QTimer()
        self.timer.timeout.connect(self.update_encoder_reading)

    @property
    def global_motor_encoder_config(self):
        """Return the motor and encoder global configuration."""
        return _QApplication.instance().motor_encoder_config

    @global_motor_encoder_config.setter
    def global_motor_encoder_config(self, value):
        _QApplication.instance().motor_encoder_config = value

    def connect_signal_slots(self):
        """Create signal/slot connections."""
        sbs = [
            self.ui.sb_driver_address,
            self.ui.sbd_motor_velocity,
            self.ui.sbd_motor_acceleration,
            self.ui.sb_encoder_resolution,
            ]
        for sb in sbs:
            sb.valueChanged.connect(self.clear_load_options)

        cmbs = [
            self.ui.cmb_motor_direction,
            self.ui.cmb_motor_resolution,
            self.ui.cmb_integrator_channel,
            self.ui.cmb_encoder_direction,
            ]
        for cmb in cmbs:
            cmb.currentIndexChanged.connect(self.clear_load_options)

        self.ui.pbt_config_param.clicked.connect(self.config_param)
        self.ui.chb_encoder.clicked.connect(
            self.enable_encoder_reading)
        self.ui.rbt_nr_turns.toggled.connect(self.disable_invalid_widgets)
        self.ui.rbt_nr_steps.toggled.connect(self.disable_invalid_widgets)
        self.ui.pbt_move_motor.clicked.connect(self.move_motor)
        self.ui.pbt_stop_motor.clicked.connect(self.stop_motor)
        super().connect_signal_slots()

    def move_motor(self):
        try:
            if not _driver.connected:
                msg = 'Driver not connected.'
                _QMessageBox.critical(
                    self, 'Failure', msg, _QMessageBox.Ok)
                return

            driver_address = self.ui.sb_driver_address.value()
            resolution = self.ui.cmb_motor_resolution.currentText()
            direction = self.ui.cmb_motor_direction.currentText()
            velocity = self.ui.sbd_motor_velocity.value()
            acceleration = self.ui.sbd_motor_acceleration.value()

            if self.ui.rbt_nr_steps.isChecked():
                steps = self.ui.sb_nr_steps.value()
            else:
                steps = resolution*self.ui.sbd_nr_turns.value()

            if not _driver.config_motor(
                    driver_address,
                    0,
                    direction,
                    resolution,
                    velocity,
                    acceleration,
                    steps):

                msg = 'Failed to send configuration to motor.'
                _QMessageBox.critical(
                    self, 'Failure', msg, _QMessageBox.Ok)
                return

            _driver.move_motor(self.config.driver_address)

        except Exception:
            _traceback.print_exc(file=_sys.stdout)
            msg = 'Failed to move motor.'
            _QMessageBox.critical(self, 'Failure', msg, _QMessageBox.Ok)
            return

    def stop_motor(self):
        if not self.update_configuration():
            return

        try:
            driver_address = self.ui.sb_driver_address.value()
            _driver.stop_motor(driver_address)

        except Exception:
            _traceback.print_exc(file=_sys.stdout)
            msg = 'Failed to stop motor.'
            _QMessageBox.critical(self, 'Failure', msg, _QMessageBox.Ok)
            return

    def disable_invalid_widgets(self):
        if self.ui.rbt_nr_steps.isChecked():
            self.ui.sb_nr_steps.setEnabled(True)
            self.ui.sbd_nr_turns.setEnabled(False)
        else:
            self.ui.sb_nr_steps.setEnabled(False)
            self.ui.sbd_nr_turns.setEnabled(True)

    def enable_encoder_reading(self):
        """Enable encoder reading."""
        try:
            if self.ui.chb_encoder.isChecked():
                encoder_resolution = self.ui.sb_encoder_resolution.value()

                if _integrator.configure_encoder_reading(encoder_resolution):
                    self.stop_encoder_update = False
                    self.timer.start(self._update_encoder_interval*1000)
                    self.ui.lcd_encoder.setEnabled(True)
                else:
                    msg = 'Failed to configure encoder reading.'
                    _QMessageBox.critical(
                        self, 'Failure', msg, _QMessageBox.Ok)
                    self.stop_encoder_update = True
                    self.ui.lcd_encoder.setEnabled(False)
                    self.ui.chb_encoder.setChecked(False)
            else:
                self.ui.lcd_encoder.setEnabled(False)
                self.stop_encoder_update = True
                self.timer.stop()

        except Exception:
            _traceback.print_exc(file=_sys.stdout)
            self.ui.lcd_encoder.setEnabled(False)
            self.stop_encoder_update = True
            self.timer.stop()

    def load(self):
        """Load configuration to set parameters."""
        try:
            self.ui.sb_driver_address.setValue(
                self.config.driver_address)
            self.ui.sbd_motor_velocity.setValue(
                self.config.motor_velocity)
            self.ui.sbd_motor_acceleration.setValue(
                self.config.motor_acceleration)
            self.ui.cmb_motor_direction.setCurrentIndex(
                self.ui.cmb_motor_direction.findText(
                    str(self.config.motor_direction)))
            self.ui.cmb_motor_resolution.setCurrentIndex(
                self.ui.cmb_motor_resolution.findText(
                    str(self.config.motor_resolution)))
            self.ui.cmb_integrator_channel.setCurrentIndex(
                self.ui.cmb_integrator_channel.findText(
                    str(self.config.integrator_channel)))
            self.ui.cmb_encoder_direction.setCurrentIndex(
                self.ui.cmb_encoder_direction.findText(
                    str(self.config.encoder_direction)))
            self.ui.sb_encoder_resolution.setValue(
                self.config.encoder_resolution)

        except Exception:
            _traceback.print_exc(file=_sys.stdout)
            msg = 'Failed to load configuration.'
            _QMessageBox.critical(self, 'Failure', msg, _QMessageBox.Ok)

    def update_configuration(self):
        """Update configuration parameters."""
        self.config.clear()

        try:
            self.config.driver_address = (
                self.ui.sb_driver_address.value())
            self.config.motor_velocity = (
                self.ui.sbd_motor_velocity.value())
            self.config.motor_acceleration = (
                self.ui.sbd_motor_acceleration.value())
            self.config.motor_direction = (
                self.ui.cmb_motor_direction.currentText())
            self.config.motor_resolution = (
                self.ui.cmb_motor_resolution.currentText())
            self.config.integrator_channel = (
                self.ui.cmb_integrator_channel.currentText())
            self.config.encoder_direction = (
                self.ui.cmb_encoder_direction.currentText())
            self.config.encoder_resolution = (
                self.ui.sb_encoder_resolution.value())

        except Exception:
            _traceback.print_exc(file=_sys.stdout)
            self.config.clear()

        if self.config.valid_data():
            return True
        else:
            msg = 'Invalid configuration.'
            _QMessageBox.critical(self, 'Failure', msg, _QMessageBox.Ok)
            return False

    def update_encoder_reading(self):
        """Update encoder reading."""
        if self.stop_encoder_update:
            self.ui.lcd_encoder.setvalue(0)
            self.ui.lcd_encoder.setEnabled(False)
            return

        try:
            if not _integrator.connected:
                self.ui.lcd_encoder.setvalue(0)
                self.ui.lcd_encoder.setEnabled(False)
                return

            value = int(_integrator.read_from_device())
            self.ui.lcd_encoder.setvalue(value)

        except Exception:
            pass

    def config_param(self):
        """Configure motor and encoder parameters."""
        self.config.clear()

        try:
            self.config.driver_address = (
                self.ui.sb_driver_address.value())
            self.config.motor_velocity = (
                self.ui.sbd_motor_velocity.value())
            self.config.motor_acceleration = (
                self.ui.sbd_motor_acceleration.value())
            self.config.motor_direction = (
                self.ui.cmb_motor_direction.currentText())
            self.config.motor_resolution = (
                self.ui.cmb_motor_resolution.currentText())
            self.config.integrator_channel = (
                self.ui.cmb_integrator_channel.currentText())
            self.config.encoder_direction = (
                self.ui.cmb_encoder_direction.currentText())
            self.config.encoder_resolution = (
                self.ui.sb_encoder_resolution.value())

            if not self.config.valid_data():
                msg = 'Invalid configuration.'
                _QMessageBox.critical(self, 'Failure', msg, _QMessageBox.Ok)
                return False

            self.save_db()

            self.global_motor_encoder_config = self.config.copy()
            msg = 'Motor and encoder parameters configured.'
            _QMessageBox.information(
                self, 'Information', msg, _QMessageBox.Ok)
            return True

        except Exception:
            _traceback.print_exc(file=_sys.stdout)
            return False
