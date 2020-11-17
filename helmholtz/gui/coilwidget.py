# -*- coding: utf-8 -*-

"""Coil widget for the control application."""

import os as _os
import sys as _sys
import traceback as _traceback
import serial.tools.list_ports as _list_ports
from qtpy.QtWidgets import (
    QWidget as _QWidget,
    QMessageBox as _QMessageBox,
    QApplication as _QApplication,
    )
from qtpy.QtCore import Qt as _Qt
import qtpy.uic as _uic

from helmholtz.gui import utils as _utils
from helmholtz.gui.auxiliarywidgets import (
    ConfigurationWidget as _ConfigurationWidget
    )
import helmholtz.data.configuration as _configuration


class CoilWidget(_ConfigurationWidget):
    """Coil widget class for the control application."""

    def __init__(self, parent=None):
        """Set up the ui."""
        uifile = _utils.get_ui_file(self)
        config = _configuration.CoilConfig()
        super().__init__(uifile, config, parent=parent)

        self.connect_signal_slots()

    @property
    def global_coil_config(self):
        """Return the coil global configuration."""
        return _QApplication.instance().coil_config

    @global_coil_config.setter
    def global_coil_config(self, value):
        _QApplication.instance().coil_config = value

    def connect_signal_slots(self):
        """Create signal/slot connections."""
        sbs = [
            self.ui.sbd_radius_1,
            self.ui.sbd_radius_2,
            self.ui.sbd_center_distance,
            self.ui.sb_coil_turns,
            ]
        for sb in sbs:
            sb.valueChanged.connect(self.clear_load_options)

        self.ui.pbt_config_param.clicked.connect(self.config_param)
        super().connect_signal_slots()

    def load(self):
        """Load configuration to set parameters."""
        try:
            self.ui.sbd_radius_1.setValue(
                self.config.radius_1)
            self.ui.sbd_radius_2.setValue(
                self.config.radius_2)
            self.ui.sbd_center_distance.setValue(
                self.config.center_distance)
            self.ui.sb_coil_turns.setValue(
                self.config.coil_turns)

        except Exception:
            _traceback.print_exc(file=_sys.stdout)
            msg = 'Failed to load configuration.'
            _QMessageBox.critical(self, 'Failure', msg, _QMessageBox.Ok)

    def update_configuration(self):
        """Update configuration parameters."""
        self.config.clear()

        try:
            self.config.radius_1 = (
                self.ui.sbd_radius_1.value())
            self.config.radius_2 = (
                self.ui.sbd_radius_2.value())
            self.config.center_distance = (
                self.ui.sbd_center_distance.value())
            self.config.coil_turns = (
                self.ui.sb_coil_turns.value())

        except Exception:
            _traceback.print_exc(file=_sys.stdout)
            self.config.clear()

        if self.config.valid_data():
            return True
        else:
            msg = 'Invalid configuration.'
            _QMessageBox.critical(self, 'Failure', msg, _QMessageBox.Ok)
            return False

    def config_param(self):
        """Configure coil parameters."""
        try:
            self.config.clear()

            self.config.radius_1 = (
                self.ui.sbd_radius_1.value())
            self.config.radius_2 = (
                self.ui.sbd_radius_2.value())
            self.config.center_distance = (
                self.ui.sbd_center_distance.value())
            self.config.coil_turns = (
                self.ui.sb_coil_turns.value())

            if not self.config.valid_data():
                msg = 'Invalid configuration.'
                _QMessageBox.critical(self, 'Failure', msg, _QMessageBox.Ok)
                return False

            self.save_db()

            self.global_coil_config = self.config.copy()
            msg = 'Coil parameters configured.'
            _QMessageBox.information(
                self, 'Information', msg, _QMessageBox.Ok)
            return True

        except Exception:
            _traceback.print_exc(file=_sys.stdout)
            return False
