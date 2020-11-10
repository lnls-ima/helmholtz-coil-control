# -*- coding: utf-8 -*-

"""Connection widget for the control application."""

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

from helmholtzcoil.gui.utils import get_ui_file as _get_ui_file
import helmholtzcoil.data.configuration as _configuration
from helmholtzcoil.devices import (
    display as _display,
    driver as _driver,
    multimeter as _multimeter,
    integrator as _integrator,
    )


class ConnectionWidget(_QWidget):
    """Connection widget class for the control application."""

    def __init__(self, parent=None):
        """Set up the ui."""
        super().__init__(parent)

        # setup the ui
        uifile = _get_ui_file(self)
        self.ui = _uic.loadUi(uifile, self)

        self.connection_config = _configuration.ConnectionConfig()

        self.connect_signal_slots()
        self.update_serial_ports()
        self.update_connection_ids()

    @property
    def database_name(self):
        """Database name."""
        return _QApplication.instance().database_name

    @property
    def mongo(self):
        """MongoDB database."""
        return _QApplication.instance().mongo

    @property
    def server(self):
        """Server for MongoDB database."""
        return _QApplication.instance().server

    def closeEvent(self, event):
        """Close widget."""
        try:
            self.disconnect_devices(msgbox=False)
            event.accept()
        except Exception:
            _traceback.print_exc(file=_sys.stdout)
            event.accept()

    def clear_load_options(self):
        """Clear load options."""
        self.ui.cmb_idn.setCurrentIndex(-1)

    def connect_devices(self):
        """Connect devices."""
        if not self.update_configuration():
            return

        self.blockSignals(True)
        _QApplication.setOverrideCursor(_Qt.WaitCursor)

        try:
            if self.connection_config.display_enable:
                _display.connect(
                    self.connection_config.display_port,
                    self.connection_config.display_baudrate)

            if self.connection_config.driver_enable:
                _driver.connect(
                    self.connection_config.driver_port,
                    self.connection_config.driver_baudrate)

            if self.connection_config.multimeter_enable:
                _multimeter.connect(
                    self.connection_config.multimeter_port,
                    self.connection_config.multimeter_baudrate)

            if self.connection_config.integrator_enable:
                _integrator.connect(
                    self.connection_config.integrator_address)

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
            if (self.connection_config.display_enable and
                    not _display.connected):
                return False

            if (self.connection_config.driver_enable and
                    not _driver.connected):
                return False

            if (self.connection_config.multimeter_enable and
                    not _mulitimeter.connected):
                return False

            if (self.connection_config.integrator_enable and
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
            ]
        for sb in sbs:
            sb.valueChanged.connect(self.clear_load_options)

        cmbs = [
            self.ui.cmb_display_port,
            self.ui.cmb_display_baudrate,
            self.ui.cmb_driver_port,
            self.ui.cmb_driver_baudrate,
            self.ui.cmb_multimeter_port,
            self.ui.cmb_multimeter_baudrate,
            ]
        for cmb in cmbs:
            cmb.currentIndexChanged.connect(self.clear_load_options)

        self.ui.cmb_idn.currentIndexChanged.connect(self.enable_load_db)
        self.ui.tbt_update_idn.clicked.connect(self.update_connection_ids)
        self.ui.pbt_load_db.clicked.connect(self.load_db)
        self.ui.tbt_save_db.clicked.connect(self.save_db)
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

    def enable_load_db(self):
        """Enable button to load configuration from database."""
        if self.ui.cmb_idn.currentIndex() != -1:
            self.ui.pbt_load_db.setEnabled(True)
        else:
            self.ui.pbt_load_db.setEnabled(False)

    def load_db(self):
        """Load configuration from database to set parameters."""
        try:
            idn = int(self.ui.cmb_idn.currentText())
        except Exception:
            _QMessageBox.critical(
                self, 'Failure', 'Invalid database ID.', _QMessageBox.Ok)
            return

        try:
            self.update_connection_ids()
            idx = self.ui.cmb_idn.findText(str(idn))
            if idx == -1:
                self.ui.cmb_idn.setCurrentIndex(-1)
                _QMessageBox.critical(
                    self, 'Failure', 'Invalid database ID.', _QMessageBox.Ok)
                return

            self.connection_config.clear()
            self.connection_config.db_update_database(
                self.database_name, mongo=self.mongo, server=self.server)
            self.connection_config.db_read(idn)
        except Exception:
            _traceback.print_exc(file=_sys.stdout)
            msg = 'Failed to read connection from database.'
            _QMessageBox.critical(self, 'Failure', msg, _QMessageBox.Ok)
            return

        self.load()
        self.ui.cmb_idn.setCurrentIndex(self.ui.cmb_idn.findText(str(idn)))
        self.ui.pbt_load_db.setEnabled(False)

    def load(self):
        """Load configuration to set connection parameters."""
        try:
            self.ui.chb_display_enable.setChecked(
                self.connection_config.display_enable)
            self.ui.cmb_display_port.setCurrentIndex(
                self.ui.cmb_display_port.findText(
                    self.connection_config.display_port))
            self.ui.cmb_display_baudrate.setCurrentIndex(
                self.ui.cmb_display_baudrate.findText(
                    str(self.connection_config.display_baudrate)))

            self.ui.chb_driver_enable.setChecked(
                self.connection_config.driver_enable)
            self.ui.cmb_driver_port.setCurrentIndex(
                self.ui.cmb_driver_port.findText(
                    self.connection_config.driver_port))
            self.ui.cmb_driver_baudrate.setCurrentIndex(
                self.ui.cmb_driver_baudrate.findText(
                    str(self.connection_config.driver_baudrate)))

            self.ui.chb_multimeter_enable.setChecked(
                self.connection_config.multimeter_enable)
            self.ui.cmb_multimeter_port.setCurrentIndex(
                self.ui.cmb_multimeter_port.findText(
                    self.connection_config.multimeter_port))
            self.ui.cmb_multimeter_baudrate.setCurrentIndex(
                self.ui.cmb_multimeter_baudrate.findText(
                    str(self.connection_config.multimeter_baudrate)))

            self.ui.chb_integrator_enable.setChecked(
                self.connection_config.integrator_enable)
            self.ui.sb_integrator_address.setValue(
                self.connection_config.integrator_address)

        except Exception:
            _traceback.print_exc(file=_sys.stdout)
            msg = 'Failed to load configuration.'
            _QMessageBox.critical(self, 'Failure', msg, _QMessageBox.Ok)

    def save_db(self):
        """Save connection parameters to database."""
        self.ui.cmb_idn.setCurrentIndex(-1)
        if self.database_name is not None:
            try:
                if self.update_configuration():
                    self.connection_config.db_update_database(
                        self.database_name,
                        mongo=self.mongo, server=self.server)
                    idn = self.connection_config.db_save()
                    self.ui.cmb_idn.addItem(str(idn))
                    self.ui.cmb_idn.setCurrentIndex(self.ui.cmb_idn.count()-1)
                    self.ui.pbt_load_db.setEnabled(False)
            except Exception:
                _traceback.print_exc(file=_sys.stdout)
                msg = 'Failed to save connection to database.'
                _QMessageBox.critical(self, 'Failure', msg, _QMessageBox.Ok)
        else:
            msg = 'Invalid database filename.'
            _QMessageBox.critical(
                self, 'Failure', msg, _QMessageBox.Ok)

    def update_connection_ids(self):
        """Update connection IDs in combo box."""
        current_text = self.ui.cmb_idn.currentText()
        load_enabled = self.ui.pbt_load_db.isEnabled()
        self.ui.cmb_idn.clear()
        try:
            self.connection_config.db_update_database(
                self.database_name,
                mongo=self.mongo, server=self.server)
            idns = self.connection_config.db_get_id_list()
            self.ui.cmb_idn.addItems([str(idn) for idn in idns])
            if len(current_text) == 0:
                self.ui.cmb_idn.setCurrentIndex(self.ui.cmb_idn.count()-1)
                self.ui.pbt_load_db.setEnabled(True)
            else:
                self.ui.cmb_idn.setCurrentText(current_text)
                self.ui.pbt_load_db.setEnabled(load_enabled)
        except Exception:
            pass

    def update_configuration(self):
        """Update connection configuration parameters."""
        self.connection_config.clear()

        try:
            self.connection_config.display_enable = (
                self.ui.chb_display_enable.isChecked())
            self.connection_config.display_port = (
                self.ui.cmb_display_port.currentText())
            self.connection_config.display_baudrate = int(
                self.ui.cmb_display_baudrate.currentText())

            self.connection_config.driver_enable = (
                self.ui.chb_driver_enable.isChecked())
            self.connection_config.driver_port = (
                self.ui.cmb_driver_port.currentText())
            self.connection_config.driver_baudrate = int(
                self.ui.cmb_driver_baudrate.currentText())

            self.connection_config.multimeter_enable = (
                self.ui.chb_multimeter_enable.isChecked())
            self.connection_config.multimeter_port = (
                self.ui.cmb_multimeter_port.currentText())
            self.connection_config.multimeter_baudrate = int(
                self.ui.cmb_multimeter_baudrate.currentText())

            self.connection_config.integrator_enable = (
                self.ui.chb_integrator_enable.isChecked())
            self.connection_config.integrator_address = (
                self.ui.sb_integrator_address.value())

        except Exception:
            _traceback.print_exc(file=_sys.stdout)
            self.connection_config.clear()

        if self.connection_config.valid_data():
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
        _l = [p[0] for p in _list_ports.comports()]

        if len(_l) == 0:
            return

        _ports = []
        _s = ''
        _k = str
        if 'COM' in _l[0]:
            _s = 'COM'
            _k = int

        for key in _l:
            _ports.append(key.strip(_s))
        _ports.sort(key=_k)
        _ports = [_s + key for key in _ports]

        self.ui.cmb_display_port.clear()
        self.ui.cmb_display_port.addItems(_ports)

        self.ui.cmb_driver_port.clear()
        self.ui.cmb_driver_port.addItems(_ports)

        self.ui.cmb_multimeter_port.clear()
        self.ui.cmb_multimeter_port.addItems(_ports)
