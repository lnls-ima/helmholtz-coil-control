# -*- coding: utf-8 -*-

"""Motor and integrator widget for the control application."""

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
from helmholtz.devices import (
    driver as _driver,
    integrator as _integrator,
)


class MotorIntegratorWidget(_QWidget):
    """Motor and integrator widget class for the control application."""

    _update_encoder_interval = _utils.UPDATE_ENCODER_INTERVAL

    def __init__(self, parent=None):
        """Set up the ui."""
        super().__init__(parent)
        uifile = _utils.get_ui_file(self)
        self.ui = _uic.loadUi(uifile, self)
        self.connect_signal_slots()
        self.stop = True
        self.stop_encoder_update = True
        self.timer = _QTimer()
        self.timer.timeout.connect(self.update_encoder_reading)

    def connect_signal_slots(self):
        """Create signal/slot connections."""
        self.ui.pbt_homing.clicked.connect(self.homing)
        self.ui.chb_encoder.clicked.connect(
            self.enable_encoder_reading)
        self.ui.rbt_nr_turns.toggled.connect(self.disable_invalid_widgets)
        self.ui.rbt_nr_steps.toggled.connect(self.disable_invalid_widgets)
        self.ui.pbt_move_motor.clicked.connect(self.move_motor)
        self.ui.pbt_stop_motor.clicked.connect(self.stop_motor)

    @property
    def config(self):
        """Return global advanced options."""
        dialog = _QApplication.instance().advanced_options_dialog
        return dialog.config

    def homing(self):
        self.stop = False

        try:
            if not _driver.connected:
                msg = 'Driver not connected.'
                _QMessageBox.critical(
                    self, 'Failure', msg, _QMessageBox.Ok)
                return

            if not _integrator.connected:
                msg = 'Integrator not connected.'
                _QMessageBox.critical(
                    self, 'Failure', msg, _QMessageBox.Ok)
                return

            wait = 0.1

            driver_address = self.config.motor_driver_address
            resolution = self.config.motor_resolution
            rotation_direction = self.config.motor_roattion_direction
            velocity = self.config.motor_velocity
            acceleration = self.config.motor_acceleration

            mode = 0
            steps = int(int(resolution)*2)

            if not _driver.config_motor(
                    driver_address,
                    mode,
                    rotation_direction,
                    resolution,
                    velocity,
                    acceleration,
                    steps):
                msg = 'Failed to send configuration to motor.'
                _QMessageBox.critical(
                    self, 'Failure', msg, _QMessageBox.Ok)
                return

            encoder_direction = self.config.integrator_encoder_direction
            _integrator.send_command(_integrator.commands.reset_counter)
            _time.sleep(wait)

            _integrator.configure_homing(encoder_direction)
            _time.sleep(wait)

            if self.stop:
                return

            _driver.move_motor(driver_address)
            _time.sleep(wait)
            while not _driver.ready(driver_address) and not self.stop:
                _time.sleep(wait)
                _QApplication.processEvents()

        except Exception:
            _traceback.print_exc(file=_sys.stdout)
            msg = 'Homing failed.'
            _QMessageBox.critical(self, 'Failure', msg, _QMessageBox.Ok)
            return

    def move_motor(self):
        self.stop = False

        try:
            if not _driver.connected:
                msg = 'Driver not connected.'
                _QMessageBox.critical(
                    self, 'Failure', msg, _QMessageBox.Ok)
                return

            driver_address = self.config.motor_driver_address
            resolution = self.config.motor_resolution
            rotation_direction = self.config.motor_roattion_direction
            velocity = self.config.motor_velocity
            acceleration = self.config.motor_accelerationion.value()

            mode = 0

            if self.ui.rbt_nr_steps.isChecked():
                steps = self.ui.sb_nr_steps.value()
            else:
                steps = int(int(resolution)*self.ui.sbd_nr_turns.value())

            if not _driver.config_motor(
                    driver_address,
                    mode,
                    rotation_direction,
                    resolution,
                    velocity,
                    acceleration,
                    steps):

                msg = 'Failed to send configuration to motor.'
                _QMessageBox.critical(
                    self, 'Failure', msg, _QMessageBox.Ok)
                return

            if not self.stop:
                _driver.move_motor(driver_address)

        except Exception:
            _traceback.print_exc(file=_sys.stdout)
            msg = 'Failed to move motor.'
            _QMessageBox.critical(self, 'Failure', msg, _QMessageBox.Ok)
            return

    def stop_motor(self):
        self.stop = True

        try:
            driver_address = self.config.motor_driver_address
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
                if not _integrator.connected:
                    msg = 'Integrator not connected.'
                    _QMessageBox.critical(
                        self, 'Failure', msg, _QMessageBox.Ok)
                    self.stop_encoder_update = True
                    self.ui.lcd_encoder.setEnabled(False)
                    self.ui.chb_encoder.setChecked(False)
                    return

                encoder_resolution = self.config.integrator_encoder_resolution

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

            value = _integrator.read_encoder()
            self.ui.lcd_encoder.display(value)

        except Exception:
            pass
