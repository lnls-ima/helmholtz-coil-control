# -*- coding: utf-8 -*-

"""Measurement widget for the control application."""

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


class MeasurementWidget(_ConfigurationWidget):
    """Measurement widget class for the control application."""

    def __init__(self, parent=None):
        """Set up the ui."""
        uifile = _utils.get_ui_file(self)
        config = _configuration.MeasurementConfig()
        super().__init__(uifile, config, parent=parent)
        
        self.connect_signal_slots()
        
    def connect_signal_slots(self):
        """Create signal/slot connections."""
        sbs = [
            ]
        for sb in sbs:
            sb.valueChanged.connect(self.clear_load_options)

        cmbs = [
            ]
        for cmb in cmbs:
            cmb.currentIndexChanged.connect(self.clear_load_options)

        super().connect_signal_slots()

    def load(self):
        """Load configuration to set parameters."""
        try:
            pass

        except Exception:
            _traceback.print_exc(file=_sys.stdout)
            msg = 'Failed to load configuration.'
            _QMessageBox.critical(self, 'Failure', msg, _QMessageBox.Ok)

    def update_configuration(self):
        """Update configuration parameters."""
        self.config.clear()

        try:
            pass

        except Exception:
            _traceback.print_exc(file=_sys.stdout)
            self.config.clear()

        if self.config.valid_data():
            return True
        else:
            msg = 'Invalid configuration.'
            _QMessageBox.critical(self, 'Failure', msg, _QMessageBox.Ok)
            return False
