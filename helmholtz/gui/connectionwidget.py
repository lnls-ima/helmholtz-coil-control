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
        
        self.connect_signal_slots()

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
        chbs = [
            self.ui.chb_display_enable,
            self.ui.chb_driver_enable,
            self.ui.chb_multimeter_enable,
            self.ui.chb_integrator_enable,
            ]
        for chb in chbs:
            chb.stateChanged.connect(self.clear_load_options)

        sbs = [
            self.ui.sb_integrator_address,
            self.ui.sb_display_bytesize,
            self.ui.sb_driver_bytesize,
            self.ui.sb_multimeter_bytesize,
            self.ui.sb_integrator_board,
            ]
        for sb in sbs:
            sb.valueChanged.connect(self.clear_load_options)

        cmbs = [
            self.ui.cmb_display_port,
            self.ui.cmb_display_baudrate,
            self.ui.cmb_display_parity,
            self.ui.cmb_display_stopbits,
            self.ui.cmb_driver_port,
            self.ui.cmb_driver_baudrate,
            self.ui.cmb_driver_parity,
            self.ui.cmb_driver_stopbits,
            self.ui.cmb_multimeter_port,
            self.ui.cmb_multimeter_baudrate,
            self.ui.cmb_multimeter_parity,
            self.ui.cmb_multimeter_stopbits,
            ]
        for cmb in cmbs:
            cmb.currentIndexChanged.connect(self.clear_load_options)

        self.ui.pbt_connect.clicked.connect(self.connect_devices)
        self.ui.pbt_disconnect.clicked.connect(self.disconnect_devices)
        super().connect_signal_slots()

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

    def load(self):
        """Load configuration to set connection parameters."""
        try:
            self.ui.chb_display_enable.setChecked(
                self.config.display_enable)
            self.ui.cmb_display_port.setCurrentIndex(
                self.ui.cmb_display_port.findText(
                    self.config.display_port))
            self.ui.cmb_display_baudrate.setCurrentIndex(
                self.ui.cmb_display_baudrate.findText(
                    str(self.config.display_baudrate)))
            self.ui.sb_display_bytesize.setValue(
                self.config.display_bytesize)
            self.ui.cmb_display_parity.setCurrentIndex(
                self.ui.cmb_display_parity.findText(
                    self.config.display_parity))
            self.ui.cmb_display_stopbits.setCurrentIndex(
                self.ui.cmb_display_stopbits.findText(
                    self.config.display_stopbits))

            self.ui.chb_driver_enable.setChecked(
                self.config.driver_enable)
            self.ui.cmb_driver_port.setCurrentIndex(
                self.ui.cmb_driver_port.findText(
                    self.config.driver_port))
            self.ui.cmb_driver_baudrate.setCurrentIndex(
                self.ui.cmb_driver_baudrate.findText(
                    str(self.config.driver_baudrate)))
            self.ui.sb_driver_bytesize.setValue(
                self.config.driver_bytesize)
            self.ui.cmb_driver_parity.setCurrentIndex(
                self.ui.cmb_driver_parity.findText(
                    self.config.driver_parity))
            self.ui.cmb_driver_stopbits.setCurrentIndex(
                self.ui.cmb_driver_stopbits.findText(
                    self.config.driver_stopbits))

            self.ui.chb_multimeter_enable.setChecked(
                self.config.multimeter_enable)
            self.ui.cmb_multimeter_port.setCurrentIndex(
                self.ui.cmb_multimeter_port.findText(
                    self.config.multimeter_port))
            self.ui.cmb_multimeter_baudrate.setCurrentIndex(
                self.ui.cmb_multimeter_baudrate.findText(
                    str(self.config.multimeter_baudrate)))
            self.ui.sb_multimeter_bytesize.setValue(
                self.config.multimeter_bytesize)
            self.ui.cmb_multimeter_parity.setCurrentIndex(
                self.ui.cmb_multimeter_parity.findText(
                    self.config.multimeter_parity))
            self.ui.cmb_multimeter_stopbits.setCurrentIndex(
                self.ui.cmb_multimeter_stopbits.findText(
                    self.config.multimeter_stopbits))

            self.ui.chb_integrator_enable.setChecked(
                self.config.integrator_enable)
            self.ui.sb_integrator_address.setValue(
                self.config.integrator_address)
            self.ui.sb_integrator_board.setValue(
                self.config.integrator_board)

        except Exception:
            _traceback.print_exc(file=_sys.stdout)
            msg = 'Failed to load configuration.'
            _QMessageBox.critical(self, 'Failure', msg, _QMessageBox.Ok)

    def update_configuration(self):
        """Update connection configuration parameters."""
        self.config.clear()

        try:
            self.config.display_enable = (
                self.ui.chb_display_enable.isChecked())
            self.config.display_port = (
                self.ui.cmb_display_port.currentText())
            self.config.display_baudrate = int(
                self.ui.cmb_display_baudrate.currentText())
            self.config.display_bytesize = int(
                self.ui.sb_display_bytesize.value())
            self.config.display_parity = (
                self.ui.cmb_display_parity.currentText())
            self.config.display_stopbits = (
                self.ui.cmb_display_stopbits.currentText())

            self.config.driver_enable = (
                self.ui.chb_driver_enable.isChecked())
            self.config.driver_port = (
                self.ui.cmb_driver_port.currentText())
            self.config.driver_baudrate = int(
                self.ui.cmb_driver_baudrate.currentText())
            self.config.driver_bytesize = int(
                self.ui.sb_driver_bytesize.value())
            self.config.driver_parity = (
                self.ui.cmb_driver_parity.currentText())
            self.config.driver_stopbits = (
                self.ui.cmb_driver_stopbits.currentText())

            self.config.multimeter_enable = (
                self.ui.chb_multimeter_enable.isChecked())
            self.config.multimeter_port = (
                self.ui.cmb_multimeter_port.currentText())
            self.config.multimeter_baudrate = int(
                self.ui.cmb_multimeter_baudrate.currentText())
            self.config.multimeter_bytesize = int(
                self.ui.sb_multimeter_bytesize.value())
            self.config.multimeter_parity = (
                self.ui.cmb_multimeter_parity.currentText())
            self.config.multimeter_stopbits = (
                self.ui.cmb_multimeter_stopbits.currentText())

            self.config.integrator_enable = (
                self.ui.chb_integrator_enable.isChecked())
            self.config.integrator_address = (
                self.ui.sb_integrator_address.value())
            self.config.integrator_board = (
                self.ui.sb_integrator_board.value())

        except Exception:
            _traceback.print_exc(file=_sys.stdout)
            self.config.clear()

        if self.config.valid_data():
            return True
        else:
            msg = 'Invalid connection configuration.'
            _QMessageBox.critical(self, 'Failure', msg, _QMessageBox.Ok)
            return False

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
