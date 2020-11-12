# -*- coding: utf-8 -*-

"""Main entry poin to the control application."""

import sys as _sys
import threading as _threading
from qtpy.QtWidgets import QApplication as _QApplication

from helmholtz.gui import utils as _utils
from helmholtz.gui.mainwindow import MainWindow as _MainWindow
from helmholtz.data import configuration as _configuration


class MainApp(_QApplication):
    """Hall bench application."""

    def __init__(self, args):
        """Start application."""
        super().__init__(args)
        self.setStyle(_utils.WINDOW_STYLE)

        self.directory = _utils.BASEPATH
        self.database_name = _utils.DATABASE_NAME
        self.mongo = _utils.MONGO
        self.server = _utils.SERVER
        self.create_database()
        self.coil_config = _configuration.CoilConfig()
        self.motor_encoder_config = _configuration.MotorEncoderConfig()

    def create_database(self):
        """Create database and tables."""
        _ConnectionConfig = _configuration.ConnectionConfig(
            database_name=self.database_name,
            mongo=self.mongo, server=self.server)
        _CoilConfig = _configuration.CoilConfig(
            database_name=self.database_name,
            mongo=self.mongo, server=self.server)
        _MotorEncoderConfig = _configuration.MotorEncoderConfig(
            database_name=self.database_name,
            mongo=self.mongo, server=self.server)

        status = []
        status.append(_ConnectionConfig.db_create_collection())
        status.append(_CoilConfig.db_create_collection())
        status.append(_MotorEncoderConfig.db_create_collection())
        if not all(status):
            raise Exception("Failed to create database.")


class GUIThread(_threading.Thread):
    """GUI Thread."""

    def __init__(self):
        """Start thread."""
        _threading.Thread.__init__(self)
        self.app = None
        self.window = None
        self.daemon = True
        self.start()

    def run(self):
        """Thread target function."""
        self.app = None
        if not _QApplication.instance():
            self.app = MainApp([])
            self.window = _MainWindow(
                width=_utils.WINDOW_WIDTH, height=_utils.WINDOW_HEIGHT)
            self.window.show()
            self.window.centralize_window()
            _sys.exit(self.app.exec_())


def run():
    """Run hallbench application."""
    app = None
    if not _QApplication.instance():
        app = MainApp([])
        window = _MainWindow(
            width=_utils.WINDOW_WIDTH, height=_utils.WINDOW_HEIGHT)
        window.show()
        window.centralize_window()
        _sys.exit(app.exec_())


def run_in_thread():
    """Run hallbench application in a thread."""
    return GUIThread()
