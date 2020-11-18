# -*- coding: utf-8 -*-

"""Motor and integrator widget for the control application."""

import os as _os
import sys as _sys
import time as _time
import traceback as _traceback
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

        self.sb_names = [
            'driver_address',
            'encoder_resolution',
        ]

        self.sbd_names = [
            'motor_velocity',
            'motor_acceleration',
        ]

        self.cmb_names = [
            'motor_direction',
            'motor_resolution',
            'integrator_channel',
            'encoder_direction',
        ]

        self.connect_signal_slots()
        self.load_last_db_entry()

        self.stop_encoder_update = True
        self.timer = _QTimer()
        self.timer.timeout.connect(self.update_encoder_reading)

    @property
    def global_motor_integrator_config(self):
        """Return the motor and encoder global configuration."""
        return _QApplication.instance().motor_integrator_config

    @global_motor_integrator_config.setter
    def global_motor_integrator_config(self, value):
        _QApplication.instance().motor_integrator_config = value

    def connect_signal_slots(self):
        """Create signal/slot connections."""
        super().connect_signal_slots()
        self.ui.pbt_config_param.clicked.connect(self.config_param)
        self.ui.chb_encoder.clicked.connect(
            self.enable_encoder_reading)
        self.ui.rbt_nr_turns.toggled.connect(self.disable_invalid_widgets)
        self.ui.rbt_nr_steps.toggled.connect(self.disable_invalid_widgets)
        self.ui.pbt_move_motor.clicked.connect(self.move_motor)
        self.ui.pbt_stop_motor.clicked.connect(self.stop_motor)

    def move_motor(self):
        try:
            if not _driver.connected:
                msg = 'Driver not connected.'
                _QMessageBox.critical(
                    self, 'Failure', msg, _QMessageBox.Ok)
                return

            driver_address = self.ui.sb_driver_address.value()
            resolution = int(self.ui.cmb_motor_resolution.currentText())
            direction = self.ui.cmb_motor_direction.currentText()
            velocity = self.ui.sbd_motor_velocity.value()
            acceleration = self.ui.sbd_motor_acceleration.value()

            if self.ui.rbt_nr_steps.isChecked():
                steps = self.ui.sb_nr_steps.value()
            else:
                steps = int(int(resolution)*self.ui.sbd_nr_turns.value())

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
                    _integrator.send_command(
                        _integrator.commands.reset_counter)
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

            _integrator.send_command(
                _integrator.commands.read_counter)
            _time.sleep(0.1)
            value = int(_integrator.read_from_device())
            self.ui.lcd_encoder.display(value)

        except Exception:
            pass

    def config_param(self):
        """Configure motor and encoder parameters."""
        try:
            if not self.update_configuration():
                return False

            self.save_db()

            self.global_motor_integrator_config = self.config.copy()
            
            msg = 'Motor and encoder parameters configured.'
            _QMessageBox.information(
                self, 'Information', msg, _QMessageBox.Ok)
            return True

        except Exception:
            _traceback.print_exc(file=_sys.stdout)
            return False
