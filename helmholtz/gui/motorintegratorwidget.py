# -*- coding: utf-8 -*-

"""Motor and integrator widget for the control application."""

import sys as _sys
import time as _time
import numpy as _np
import traceback as _traceback
from qtpy.QtWidgets import (
    QWidget as _QWidget,
    QMessageBox as _QMessageBox,
    QApplication as _QApplication,
    )
from qtpy.QtCore import (
    Qt as _Qt,
    QTimer as _QTimer,
    QCoreApplication as _QCoreApplication,
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
        self.ui.rbt_encoder_position.toggled.connect(
            self.disable_invalid_widgets)
        self.ui.pbt_move_motor.clicked.connect(self.move_motor)
        self.ui.pbt_stop_motor.clicked.connect(self.stop_motor)
        self.ui.pbt_reset.clicked.connect(self.reset_integrator)
        self.ui.pbt_shut_down.clicked.connect(
            self.shut_down_integrator)
        self.ui.pbt_short_circuit_on.clicked.connect(
            self.turn_on_integrator_short_circuit)
        self.ui.pbt_short_circuit_off.clicked.connect(
            self.turn_off_integrator_short_circuit)
        self.ui.pbt_calibrate.clicked.connect(self.calibrate_integrator)
        self.ui.pbt_set_gain.clicked.connect(self.set_gain_integrator)

    @property
    def advanced_options(self):
        """Return global advanced options."""
        dialog = _QApplication.instance().advanced_options_dialog
        return dialog.config

    def reset_integrator(self):
        if self.check_integrator_connection():
            _integrator.reset()

    def shut_down_integrator(self):
        if self.check_integrator_connection():
            _integrator.shut_down()

    def turn_on_integrator_short_circuit(self):
        if self.check_integrator_connection():
            _integrator.short_circuit_on()

    def turn_off_integrator_short_circuit(self):
        if self.check_integrator_connection():
            _integrator.short_circuit_off()

    def calibrate_integrator(self):
        if self.check_integrator_connection():
            _integrator.calibrate()

    def set_gain_integrator(self):
        try:
            if self.check_integrator_connection():
                gain = int(self.ui.cmb_gain.currentText())
                _integrator.configure_gain(gain)
        except Exception:
            _traceback.print_exc(file=_sys.stdout)
            return

    def check_integrator_connection(self):
        if not _integrator.connected:
            msg = _QCoreApplication.translate('',  'Integrator not connected.')
            title = _QCoreApplication.translate('', 'Failure')
            _QMessageBox.critical(self, title, msg, _QMessageBox.Ok)
            return False
        return True       

    def check_driver_connection(self):
        if not _driver.connected:
            msg = _QCoreApplication.translate('', 'Driver not connected.')
            title = _QCoreApplication.translate('', 'Failure')
            _QMessageBox.critical(self, title, msg, _QMessageBox.Ok)
            return False
        return True       

    def homing(self):
        self.stop = False

        try:
            if not self.check_driver_connection():
                return

            if not self.check_integrator_connection():
                return

            wait = 0.1

            driver_address = self.advanced_options.motor_driver_address
            resolution = self.advanced_options.motor_resolution
            rotation_direction = self.advanced_options.motor_rotation_direction
            velocity = self.advanced_options.motor_velocity
            acceleration = self.advanced_options.motor_acceleration

            mode = 0
            steps = int(int(resolution))

            if not _driver.config_motor(
                    driver_address,
                    mode,
                    rotation_direction,
                    resolution,
                    velocity,
                    acceleration,
                    steps):
                msg = _QCoreApplication.translate(
                    '', 'Failed to send configuration to motor.')
                title = _QCoreApplication.translate('', 'Failure')
                _QMessageBox.critical(
                    self, title, msg, _QMessageBox.Ok)
                return

            encoder_dir = self.advanced_options.integrator_encoder_direction

            _integrator.configure_homing(encoder_dir)
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
            msg = _QCoreApplication.translate('', 'Homing failed.')
            title = _QCoreApplication.translate('', 'Failure')
            _QMessageBox.critical(self, title, msg, _QMessageBox.Ok)
            return

    def get_steps_for_encoder_position(self, encoder_position):
        try:
            if not self.check_integrator_connection():
                return None

            encoder_res = self.advanced_options.integrator_encoder_resolution
            motor_resolution = self.advanced_options.motor_resolution
            rotation_direction = self.advanced_options.motor_rotation_direction
            current_encoder_position = int(_integrator.read_encoder())

            tol = 20
            if current_encoder_position > encoder_res + tol:
                msg = _QCoreApplication.translate(
                    '', 
                    'Invalid initial encoder position.\n' +
                    'Please, perform homing procedure.'
                    )
                title = _QCoreApplication.translate('', 'Failure')
                _QMessageBox.critical(
                    self, title, msg, _QMessageBox.Ok)
                return None

            if encoder_position > encoder_res + tol:
                msg = _QCoreApplication.translate(
                    '', 'Invalid final encoder position.')
                title = _QCoreApplication.translate('', 'Failure')
                _QMessageBox.critical(
                    self, title, msg, _QMessageBox.Ok)
                return None

            diff = (current_encoder_position - encoder_position)
            if rotation_direction == '+':
                diff = diff*(-1)
            pulses = (encoder_res - diff) % encoder_res
            steps = int((pulses*motor_resolution)/encoder_res)
            return steps

        except Exception:
            _traceback.print_exc(file=_sys.stdout)
            msg = _QCoreApplication.translate(
                '', 'Failed to calculated number of motor steps.')
            title = _QCoreApplication.translate('', 'Failure')
            _QMessageBox.critical(
                self, title, msg, _QMessageBox.Ok)
            return None

    def move_motor(self):
        self.stop = False

        try:
            if not self.check_driver_connection():
                return

            driver_address = self.advanced_options.motor_driver_address
            resolution = self.advanced_options.motor_resolution
            rotation_direction = self.advanced_options.motor_rotation_direction
            velocity = self.advanced_options.motor_velocity
            acceleration = self.advanced_options.motor_acceleration
            mode = 0

            if self.ui.rbt_nr_steps.isChecked():
                steps = self.ui.sb_nr_steps.value()
            elif self.ui.rbt_encoder_position.isChecked():
                encoder_position = self.ui.sb_encoder_position.value()
                steps = self.get_steps_for_encoder_position(encoder_position)
                if steps is None:
                    return
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

                msg = _QCoreApplication.translate(
                    '', 'Failed to send configuration to motor.')
                title = _QCoreApplication.translate('', 'Failure')
                _QMessageBox.critical(
                    self, title, msg, _QMessageBox.Ok)
                return

            if not self.stop:
                _driver.move_motor(driver_address)

        except Exception:
            _traceback.print_exc(file=_sys.stdout)
            msg = _QCoreApplication.translate(
                '', 'Failed to move motor.')
            title = _QCoreApplication.translate('', 'Failure')
            _QMessageBox.critical(self, title, msg, _QMessageBox.Ok)
            return

    def stop_motor(self):
        self.stop = True

        try:
            driver_address = self.advanced_options.motor_driver_address
            _driver.stop_motor(driver_address)

        except Exception:
            _traceback.print_exc(file=_sys.stdout)
            msg = _QCoreApplication.translate(
                '', 'Failed to stop motor.')
            title = _QCoreApplication.translate('', 'Failure')
            _QMessageBox.critical(self, title, msg, _QMessageBox.Ok)
            return

    def disable_invalid_widgets(self):
        if self.ui.rbt_nr_steps.isChecked():
            self.ui.sbd_nr_turns.setEnabled(False)
            self.ui.sb_nr_steps.setEnabled(True)
            self.ui.sb_encoder_position.setEnabled(False)
        elif self.ui.rbt_encoder_position.isChecked():
            self.ui.sbd_nr_turns.setEnabled(False)
            self.ui.sb_nr_steps.setEnabled(False)
            self.ui.sb_encoder_position.setEnabled(True)
        else:
            self.ui.sbd_nr_turns.setEnabled(True)
            self.ui.sb_nr_steps.setEnabled(False)
            self.ui.sb_encoder_position.setEnabled(False)

    def enable_encoder_reading(self):
        """Enable encoder reading."""
        try:
            encoder_res = self.advanced_options.integrator_encoder_resolution

            if self.ui.chb_encoder.isChecked():
                if not self.check_integrator_connection():
                    self.stop_encoder_update = True
                    self.ui.lcd_encoder.setEnabled(False)
                    self.ui.chb_encoder.setChecked(False)
                    return

                if _integrator.configure_encoder_reading(encoder_res):
                    self.stop_encoder_update = False
                    self.timer.start(self._update_encoder_interval*1000)
                    self.ui.lcd_encoder.setEnabled(True)
                else:
                    msg = _QCoreApplication.translate(
                        '', 'Failed to configure encoder reading.')
                    title = _QCoreApplication.translate('', 'Failure')
                    _QMessageBox.critical(
                        self, title, msg, _QMessageBox.Ok)
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
