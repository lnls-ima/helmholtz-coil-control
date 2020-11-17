# -*- coding: utf-8 -*-

"""Connection widget for the control application."""

import os as _os
import sys as _sys
import traceback as _traceback
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
from helmholtz.devices import (
    display as _display,
    driver as _driver,
    multimeter as _multimeter,
    integrator as _integrator,
    )


class ConnectionWidget(_ConfigurationWidget):
    """Connection widget class for the control application."""

    def __init__(self, parent=None):
        """Set up the ui."""
        uifile = _utils.get_ui_file(self)
        config = _configuration.ConnectionConfig()
        super().__init__(uifile, config, parent=parent)

        self.sb_names = [
            'display_bytesize',
            'driver_bytesize',
            'multimeter_bytesize',
            'integrator_address',
            'integrator_board',
        ]

        self.cmb_names = [
            'display_port',
            'display_baudrate',
            'display_parity',
            'display_stopbits',
            'driver_port',
            'driver_baudrate',
            'driver_parity',
            'driver_stopbits',
            'multimeter_port',
            'multimeter_baudrate',
            'multimeter_parity',
            'multimeter_stopbits',
        ]   

        self.chb_names = [
            'display_enable',
            'driver_enable',
            'multimeter_enable',
            'integrator_enable',
        ]

        self.connect_signal_slots()
        self.load_last_db_entry()

    def closeEvent(self, event):
        """Close widget."""
        try:
            self.disconnect_devices(msgbox=False)
            event.accept()
        except Exception:
            _traceback.print_exc(file=_sys.stdout)
            event.accept()

    def connect_devices(self):
        """Connect devices."""
        if not self.update_configuration():
            return

        self.blockSignals(True)
        _QApplication.setOverrideCursor(_Qt.WaitCursor)

        try:
            if self.config.display_enable:
                _display.connect(
                    self.config.display_port,
                    self.config.display_baudrate,
                    bytesize=self.config.display_bytesize,
                    stopbits=float(self.config.display_stopbits),
                    parity=self.config.display_parity[0],
                    )

            if self.config.driver_enable:
                _driver.connect(
                    self.config.driver_port,
                    self.config.driver_baudrate,
                    bytesize=self.config.driver_bytesize,
                    stopbits=float(self.config.driver_stopbits),
                    parity=self.config.driver_parity[0],
                    )

            if self.config.multimeter_enable:
                _multimeter.connect(
                    self.config.multimeter_port,
                    self.config.multimeter_baudrate,
                    bytesize=self.config.multimeter_bytesize,
                    stopbits=float(self.config.multimeter_stopbits),
                    parity=self.config.multimeter_parity[0],
                    )

            if self.config.integrator_enable:
                _integrator.connect(
                    self.config.integrator_address,
                    board=self.config.integrator_board,
                    )

            self.update_led_status()
            connected = self.connection_status()

            self.blockSignals(False)
            _QApplication.restoreOverrideCursor()

            if not connected:
                msg = 'Failed to connect devices.'
                _QMessageBox.critical(
                    self, 'Failure', msg, _QMessageBox.Ok)

        except Exception:
            _traceback.print_exc(file=_sys.stdout)
            self.blockSignals(False)
            _QApplication.restoreOverrideCursor()
            msg = 'Failed to connect devices.'
            _QMessageBox.critical(self, 'Failure', msg, _QMessageBox.Ok)

    def connection_status(self):
        """Return the connection status."""
        try:
            if (self.config.display_enable and
                    not _display.connected):
                return False

            if (self.config.driver_enable and
                    not _driver.connected):
                return False

            if (self.config.multimeter_enable and
                    not _multimeter.connected):
                return False

            if (self.config.integrator_enable and
                    not _integrator.connected):
                return False

            return True

        except Exception:
            _traceback.print_exc(file=_sys.stdout)
            return False

    def connect_signal_slots(self):
        """Create signal/slot connections."""
        super().connect_signal_slots()
        self.ui.pbt_connect.clicked.connect(self.connect_devices)
        self.ui.pbt_disconnect.clicked.connect(self.disconnect_devices)

    def disconnect_devices(self, msgbox=True):
        """Disconnect bench devices."""
        try:
            _display.disconnect()
            _driver.disconnect()
            _multimeter.disconnect()
            _integrator.disconnect()
            self.update_led_status()

        except Exception:
            _traceback.print_exc(file=_sys.stdout)
            if msgbox:
                msg = 'Failed to disconnect devices.'
                _QMessageBox.critical(self, 'Failure', msg, _QMessageBox.Ok)

    def update_led_status(self):
        """Update led status."""
        try:
            self.ui.la_display_led.setEnabled(_display.connected)
            self.ui.la_driver_led.setEnabled(_driver.connected)
            self.ui.la_multimeter_led.setEnabled(_multimeter.connected)
            self.ui.la_integrator_led.setEnabled(_integrator.connected)

        except Exception:
            _traceback.print_exc(file=_sys.stdout)

    def update_serial_ports(self):
        """Update avaliable serial ports."""
        ports = _driver.list_ports()

        self.ui.cmb_display_port.clear()
        self.ui.cmb_display_port.addItems(ports)

        self.ui.cmb_driver_port.clear()
        self.ui.cmb_driver_port.addItems(ports)

        self.ui.cmb_multimeter_port.clear()
        self.ui.cmb_multimeter_port.addItems(ports)
