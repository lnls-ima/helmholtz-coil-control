# -*- coding: utf-8 -*-

"""Advanced options widget for the control application."""

import sys as _sys
import traceback as _traceback
from qtpy.QtWidgets import (
    QDialog as _QDialog,
    QHBoxLayout as _QHBoxLayout,
    )
from qtpy.QtCore import (
    QCoreApplication as _QCoreApplication,
    )

from helmholtz.gui import utils as _utils
from helmholtz.gui.auxiliarywidgets import (
    ConfigurationWidget as _ConfigurationWidget
    )
import helmholtz.data.configuration as _configuration


class AdvancedOptionsDialog(_QDialog):
    """Advanced options dialog."""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.main_widget = AdvancedOptionsWidget(parent=parent)
        self.main_layout = _QHBoxLayout()
        self.main_layout.addWidget(self.main_widget)
        self.setLayout(self.main_layout)
        self.setWindowTitle(
            _QCoreApplication.translate('', "Advanced Options"))
        self.setWhatsThis(
            _QCoreApplication.translate(
                '', 'Advanced devices and measurement options.'))

    @property
    def config(self):
        """Return configuration."""
        return self.main_widget.config

    def show(self):
        try:
            self.main_widget.load_last_db_entry()
        except Exception:
            _traceback.print_exc(file=_sys.stdout)
        super().show()

    def open(self):
        try:
            self.main_widget.load_last_db_entry()
        except Exception:
            _traceback.print_exc(file=_sys.stdout)
        super().open()

    def update_dialog(self):
        try:
            self.main_widget.load_last_db_entry()
        except Exception:
            _traceback.print_exc(file=_sys.stdout)


class AdvancedOptionsWidget(_ConfigurationWidget):
    """Advanced options widget class for the control application."""

    def __init__(self, parent=None):
        """Set up the ui."""
        uifile = _utils.get_ui_file(self)
        config = _configuration.AdvancedOptions()
        super().__init__(uifile, config, parent=parent)

        self.sb_names = [
            'motor_driver_address',
            'integrator_encoder_resolution',
            'integration_trigger',
            'integration_nr_turns',
            'coil_turns',
            'temperature_nr_readings',
        ]

        self.sbd_names = [
            'motor_velocity',
            'motor_acceleration',
            'coil_radius',
            'coil_distance_center',
            'temperature_reading_frequency',
        ]

        self.cmb_names = [
            'motor_rotation_direction',
            'motor_resolution',
            'integrator_channel',
            'integrator_encoder_direction',
            'integration_points',
        ]

        self.connect_signal_slots()
        self.load_last_db_entry()

    def connect_signal_slots(self):
        """Create signal/slot connections."""
        super().connect_signal_slots()
        self.ui.pbt_save.clicked.connect(lambda: self.save_db(force=True))
        self.ui.pbt_cancel.clicked.connect(self.load)
