# -*- coding: utf-8 -*-

"""Main entry point to the control application."""

import sys as _sys
import threading as _threading
from qtpy.QtWidgets import QApplication as _QApplication

from helmholtz.gui import utils as _utils
from helmholtz.gui.mainwindow import MainWindow as _MainWindow
from helmholtz.gui.advancedoptionswidgets import AdvancedOptionsDialog \
    as _AdvancedOptionsDialog
from helmholtz.gui.resultsdialog import ResultsDialog \
    as _ResultsDialog
from helmholtz.gui.scanparameterdialog import ScanParameterDialog \
    as _ScanParameterDialog
from helmholtz.gui.findtriggerdialog import FindTriggerDialog \
    as _FindTriggerDialog
from helmholtz.data import configuration as _configuration
from helmholtz.data import measurement as _measurement


class MainApp(_QApplication):
    """Main application."""

    def __init__(self, args):
        """Start application."""
        super().__init__(args)
        self.setStyle(_utils.WINDOW_STYLE)

        self.directory = _utils.BASEPATH
        self.database_name = _utils.DATABASE_NAME
        self.mongo = _utils.MONGO
        self.server = _utils.SERVER
        self.create_database()
        self.measurement_config = _configuration.MeasurementConfig()
        self.advanced_options_dialog = None
        self.results_dialog = None
        self.scan_parameter_dialog = None
        self.find_trigger_dialog = None

    def create_dialogs(self):
        """Create dialogs."""
        self.advanced_options_dialog = _AdvancedOptionsDialog()
        self.results_dialog = _ResultsDialog()
        self.scan_parameter_dialog = _ScanParameterDialog()
        self.find_trigger_dialog = _FindTriggerDialog()

    def create_database(self):
        """Create database and tables."""
        connection_config = _configuration.ConnectionConfig(
            database_name=self.database_name,
            mongo=self.mongo, server=self.server)
        advanced_options = _configuration.AdvancedOptions(
            database_name=self.database_name,
            mongo=self.mongo, server=self.server)
        measurement_config = _configuration.MeasurementConfig(
            database_name=self.database_name,
            mongo=self.mongo, server=self.server)
        measurement_data = _measurement.MeasurementData(
            database_name=self.database_name,
            mongo=self.mongo, server=self.server)

        status = []
        status.append(connection_config.db_create_collection())
        status.append(advanced_options.db_create_collection())
        status.append(measurement_config.db_create_collection())
        status.append(measurement_data.db_create_collection())
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
            translators = _utils.get_translators()
            for translator in translators:
                self.app.installTranslator(translator)
            self.app.create_dialogs()
            self.window = _MainWindow(
                width=_utils.WINDOW_WIDTH, height=_utils.WINDOW_HEIGHT)
            self.window.show()
            self.window.centralize_window()
            _sys.exit(self.app.exec_())


def run():
    """Run application."""
    app = None
    if not _QApplication.instance():
        app = MainApp([])
        translators = _utils.get_translators()
        if translators is not None:
            for translator in translators:
                app.installTranslator(translator)
        app.create_dialogs()
        window = _MainWindow(
            width=_utils.WINDOW_WIDTH, height=_utils.WINDOW_HEIGHT)
        window.show()
        window.centralize_window()
        _sys.exit(app.exec_())


def run_in_thread():
    """Run application in a thread."""
    return GUIThread()
