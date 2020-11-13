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

from helmholtz.gui.utils import get_ui_file as _get_ui_file
import helmholtz.data.configuration as _configuration


class CoilWidget(_QWidget):
    """Coil widget class for the control application."""

    def __init__(self, parent=None):
        """Set up the ui."""
        super().__init__(parent)

        # setup the ui
        uifile = _get_ui_file(self)
        self.ui = _uic.loadUi(uifile, self)

        self.config = _configuration.CoilConfig()

        self.connect_signal_slots()
        self.update_ids()
        self.load_last_db_entry()

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

    @property
    def global_coil_config(self):
        """Return the coil global configuration."""
        return _QApplication.instance().coil_config

    @global_coil_config.setter
    def global_coil_config(self, value):
        _QApplication.instance().coil_config = value

    def clear_load_options(self):
        """Clear load options."""
        self.ui.cmb_idn.setCurrentIndex(-1)

    def connect_signal_slots(self):
        """Create signal/slot connections."""
        sbs = [
            self.ui.sbd_radius_1,
            self.ui.sbd_radius_2,
            self.ui.sbd_center_distance,
            self.ui.sb_nr_turns,
            ]
        for sb in sbs:
            sb.valueChanged.connect(self.clear_load_options)

        self.ui.cmb_idn.currentIndexChanged.connect(self.enable_load_db)
        self.ui.tbt_update_idn.clicked.connect(self.update_ids)
        self.ui.pbt_load_db.clicked.connect(self.load_db)
        self.ui.tbt_save_db.clicked.connect(self.save_db)
        self.ui.pbt_config_param.clicked.connect(self.config_param)

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
            self.update_ids()
            idx = self.ui.cmb_idn.findText(str(idn))
            if idx == -1:
                self.ui.cmb_idn.setCurrentIndex(-1)
                _QMessageBox.critical(
                    self, 'Failure', 'Invalid database ID.', _QMessageBox.Ok)
                return

            self.config.clear()
            self.config.db_update_database(
                self.database_name, mongo=self.mongo, server=self.server)
            self.config.db_read(idn)
        except Exception:
            _traceback.print_exc(file=_sys.stdout)
            msg = 'Failed to read from database.'
            _QMessageBox.critical(self, 'Failure', msg, _QMessageBox.Ok)
            return

        self.load()
        self.ui.cmb_idn.setCurrentIndex(self.ui.cmb_idn.findText(str(idn)))
        self.ui.pbt_load_db.setEnabled(False)

    def load_last_db_entry(self):
        """Load configuration from database to set parameters."""
        try:
            self.config.clear()
            self.config.db_update_database(
                self.database_name, mongo=self.mongo, server=self.server)
            self.config.db_read()

            idn = self.config.idn
            self.update_ids()
            idx = self.ui.cmb_idn.findText(str(idn))
            if idx == -1:
                self.ui.cmb_idn.setCurrentIndex(-1)
                return
       
        except Exception:
            return

        self.load()
        self.ui.cmb_idn.setCurrentIndex(self.ui.cmb_idn.findText(str(idn)))
        self.ui.pbt_load_db.setEnabled(False)

    def load(self):
        """Load configuration to set parameters."""
        try:
            self.ui.sbd_radius_1.setValue(
                self.config.radius_1)
            self.ui.sbd_radius_2.setValue(
                self.config.radius_2)
            self.ui.sbd_center_distance.setValue(
                self.config.center_distance)
            self.ui.sb_nr_turns.setValue(
                self.config.nr_turns)

        except Exception:
            _traceback.print_exc(file=_sys.stdout)
            msg = 'Failed to load configuration.'
            _QMessageBox.critical(self, 'Failure', msg, _QMessageBox.Ok)

    def save_db(self):
        """Save parameters to database."""
        self.ui.cmb_idn.setCurrentIndex(-1)
        if self.database_name is not None:
            try:
                if self.update_configuration():
                    self.config.db_update_database(
                        self.database_name,
                        mongo=self.mongo, server=self.server)
                    idn = self.config.db_save()
                    self.ui.cmb_idn.addItem(str(idn))
                    self.ui.cmb_idn.setCurrentIndex(self.ui.cmb_idn.count()-1)
                    self.ui.pbt_load_db.setEnabled(False)
            except Exception:
                _traceback.print_exc(file=_sys.stdout)
                msg = 'Failed to save to database.'
                _QMessageBox.critical(self, 'Failure', msg, _QMessageBox.Ok)
        else:
            msg = 'Invalid database filename.'
            _QMessageBox.critical(
                self, 'Failure', msg, _QMessageBox.Ok)

    def update_ids(self):
        """Update IDs in combo box."""
        current_text = self.ui.cmb_idn.currentText()
        load_enabled = self.ui.pbt_load_db.isEnabled()
        self.ui.cmb_idn.clear()
        try:
            self.config.db_update_database(
                self.database_name,
                mongo=self.mongo, server=self.server)
            idns = self.config.db_get_id_list()
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
        """Update configuration parameters."""
        self.config.clear()

        try:
            self.config.radius_1 = (
                self.ui.sbd_radius_1.value())
            self.config.radius_2 = (
                self.ui.sbd_radius_2.value())
            self.config.center_distance = (
                self.ui.sbd_center_distance.value())
            self.config.nr_turns = (
                self.ui.sb_nr_turns.value())

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
            self.config.nr_turns = (
                self.ui.sb_nr_turns.value())

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