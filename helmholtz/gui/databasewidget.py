"""Database tables widgets."""

import os as _os
import sys as _sys
import time as _time
import numpy as _np
import pandas as _pd
import sqlite3 as _sqlite3
import traceback as _traceback
import qtpy.uic as _uic
from qtpy.QtCore import (
    Qt as _Qt,
    QCoreApplication as _QCoreApplication,
    )
from qtpy.QtWidgets import (
    QWidget as _QWidget,
    QApplication as _QApplication,
    QLabel as _QLabel,
    QTableWidget as _QTableWidget,
    QTableWidgetItem as _QTableWidgetItem,
    QMessageBox as _QMessageBox,
    QVBoxLayout as _QVBoxLayout,
    QHBoxLayout as _QHBoxLayout,
    QSpinBox as _QSpinBox,
    QFileDialog as _QFileDialog,
    QInputDialog as _QInputDialog,
    QAbstractItemView as _QAbstractItemView,
    )

from imautils.gui import databasewidgets as _databasewidgets
from helmholtz.gui import utils as _utils
import helmholtz.data as _data


_ConnectionConfig = _data.configuration.ConnectionConfig
_AdvancedOptions = _data.configuration.AdvancedOptions
_MeasurementConfig = _data.configuration.MeasurementConfig
_MeasurementData = _data.measurement.MeasurementData


class DatabaseWidget(_QWidget):
    """Database widget class for the control application."""

    _connection_table_name = _ConnectionConfig.collection_name
    _advanced_options_table_name = _AdvancedOptions.collection_name
    _configuration_table_name = _MeasurementConfig.collection_name
    _measurement_table_name = _MeasurementData.collection_name

    _hidden_columns = []

    def __init__(self, parent=None):
        """Set up the ui."""
        super().__init__(parent)

        # setup the ui
        uifile = _utils.get_ui_file(self)
        self.ui = _uic.loadUi(uifile, self)

        self._table_object_dict = {
            self._connection_table_name: _ConnectionConfig,
            self._advanced_options_table_name: _AdvancedOptions,
            self._configuration_table_name: _MeasurementConfig,
            self._measurement_table_name: _MeasurementData,
            }

        self._table_page_dict = {}
        for key in self._table_object_dict.keys():
            self._table_page_dict[key] = None
        self._table_page_dict[
            self._measurement_table_name] = self.ui.pg_helmholtz_measurement

        self.short_version_hidden_tables = [
            self._connection_table_name,
            self._advanced_options_table_name,
            self._configuration_table_name,
        ]

        self.twg_database = _databasewidgets.DatabaseTabWidget(
            database_name=self.database_name,
            mongo=self.mongo, server=self.server, max_str_size=100,
            max_number_rows=2000)
        self.ui.lyt_database.addWidget(self.twg_database)

        self.connect_signal_slots()
        self.disable_invalid_buttons()
        self.configure_gui_visualization()

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
    def directory(self):
        """Return the default directory."""
        return _QApplication.instance().directory

    @property
    def results_dialog(self):
        """Return results dialog."""
        return _QApplication.instance().results_dialog

    def configure_gui_visualization(self):
        if _utils.SIMPLE:
            self.ui.pbt_delete.hide()
        else:
            self.ui.pbt_delete.show()

    def closeEvent(self, event):
        """Close widget and dialogs."""
        try:
            self.results_dialog.close()
            event.accept()
        except Exception:
            _traceback.print_exc(file=_sys.stdout)
            event.accept()

    def clear(self):
        """Clear."""
        try:
            self.twg_database.delete_widgets()
            self.twg_database.clear()
        except Exception:
            _traceback.print_exc(file=_sys.stdout)

    def connect_signal_slots(self):
        """Create signal/slot connections."""
        self.ui.pbt_save.clicked.connect(self.save_files)
        self.ui.pbt_read.clicked.connect(self.read_files)
        self.ui.pbt_delete.clicked.connect(
            self.twg_database.delete_database_documents)

        self.ui.tbt_refresh.clicked.connect(self.update_database_tables)
        self.ui.tbt_clear.clicked.connect(self.clear)
        self.ui.twg_database.currentChanged.connect(
            self.disable_invalid_buttons)

        self.ui.pbt_save_summary.clicked.connect(self.save_summary)
        self.ui.pbt_edit_comment.clicked.connect(self.edit_comment)
        self.ui.pbt_view_results.clicked.connect(self.show_results_dialog)

    def edit_comment(self):
        try:
            table_name = self.twg_database.get_current_table_name()
            if table_name is None:
                return

            idn = self.twg_database.get_table_selected_id(table_name)
            if idn is None:
                return

            object_class = self._table_object_dict[table_name]
            obj = object_class(
                database_name=self.database_name,
                mongo=self.mongo, server=self.server)
            obj.db_read(idn)
            prev_comments = obj.comments

            title = _QCoreApplication.translate('', 'Edit Comments')
            label = _QCoreApplication.translate('', 'Comments:')
            new_comments, resp = _QInputDialog.getText(
                self, title, label, text=prev_comments)

            if not resp:
                return

            obj.comments = new_comments
            obj.db_update(idn)

            self.update_database_tables()

        except Exception:
            _traceback.print_exc(file=_sys.stdout)

    def show_results_dialog(self):
        try:
            table_name = self.twg_database.get_current_table_name()
            if table_name is None:
                return

            idns = self.twg_database.get_table_selected_ids(table_name)
            nr_idns = len(idns)
            if nr_idns == 0:
                return

            measurement_list = []
            for idn in idns:
                object_class = self._table_object_dict[table_name]
                obj = object_class(
                    database_name=self.database_name,
                    mongo=self.mongo, server=self.server)
                obj.db_read(idn)
                measurement_list.append(obj)

            self.results_dialog.show(measurement_list)

        except Exception:
            _traceback.print_exc(file=_sys.stdout)

    def save_summary(self):
        try:
            table_name = self.twg_database.get_current_table_name()
            if table_name is None:
                return

            object_class = self._table_object_dict[table_name]

            idns = self.twg_database.get_table_selected_ids(table_name)
            nr_idns = len(idns)
            if nr_idns == 0:
                return

            try:
                attrs = [
                    'date', 'hour', 'block_name',
                    'mx_avg', 'my_avg', 'mz_avg',
                    'block_volume', 'block_temperature',
                    'comments',
                    ]
                df = _pd.DataFrame(columns=attrs)
                for i in range(nr_idns):
                    idn = idns[i]
                    obj = object_class(
                        database_name=self.database_name,
                        mongo=self.mongo, server=self.server)
                    obj.db_read(idn)
                    for attr in attrs:
                        value = getattr(obj, attr)
                        if attr == 'block_volume':
                            value = value*1e6
                        df.at[idn, attr] = value

            except Exception:
                _traceback.print_exc(file=_sys.stdout)
                msg = _QCoreApplication.translate(
                    '', 'Failed to read database entries.')
                title = _QCoreApplication.translate('', 'Failure')
                _QMessageBox.critical(self, title, msg, _QMessageBox.Ok)
                return

            timestamp = _time.strftime(
                '%Y-%m-%d_%H-%M-%S', _time.localtime())

            default_filename = timestamp + '_Helmholtz_Measurement_Summary.xlsx'

            caption = _QCoreApplication.translate('', 'Save file')
            filename = _QFileDialog.getSaveFileName(
                self, caption=caption,
                directory=_os.path.join(self.directory, default_filename),
                filter="Text files (*.txt *.dat)")

            if isinstance(filename, tuple):
                filename = filename[0]

            if len(filename) == 0:
                return

            try:
                df.to_excel(filename)

            except Exception:
                _traceback.print_exc(file=_sys.stdout)
                msg = _QCoreApplication.translate(
                    '', 'Failed to save file.')
                title = _QCoreApplication.translate('', 'Failure')
                _QMessageBox.critical(self, title, msg, _QMessageBox.Ok)

        except Exception:
            _traceback.print_exc(file=_sys.stdout)

    def disable_invalid_buttons(self):
        """Disable invalid buttons."""
        try:
            current_table_name = self.twg_database.get_current_table_name()
            if current_table_name is not None:
                self.ui.stw_buttons.setEnabled(True)

                for table_name, page in self._table_page_dict.items():
                    if page is not None:
                        page.setEnabled(False)
                        _idx = self.ui.stw_buttons.indexOf(page)
                    else:
                        self.ui.stw_buttons.setCurrentIndex(0)

                current_page = self._table_page_dict[current_table_name]
                if current_page is not None:
                    current_page.setEnabled(True)
                    _idx = self.ui.stw_buttons.indexOf(current_page)
                    self.ui.stw_buttons.setCurrentWidget(current_page)
            else:
                self.ui.stw_buttons.setCurrentIndex(0)
                self.ui.stw_buttons.setEnabled(False)

        except Exception:
            _traceback.print_exc(file=_sys.stdout)

    def load_database(self):
        """Load database."""
        try:
            self.twg_database.database_name = self.database_name
            self.twg_database.mongo = self.mongo
            self.twg_database.server = self.server
            if self.ui.chb_short_version.isChecked():
                hidden_tables = self.short_version_hidden_tables
                self.twg_database.hidden_tables = hidden_tables
            else:
                self.twg_database.hidden_tables = []
            self.twg_database.load_database()
            self.disable_invalid_buttons()
        except Exception:
            _traceback.print_exc(file=_sys.stdout)

    def read_files(self):
        """Read file and save in database."""
        table_name = self.twg_database.get_current_table_name()
        if table_name is None:
            return

        object_class = self._table_object_dict[table_name]

        caption = _QCoreApplication.translate('', 'Read files')
        fns = _QFileDialog.getOpenFileNames(
            self, caption=caption, directory=self.directory,
            filter="Text files (*.txt *.dat)")

        if isinstance(fns, tuple):
            fns = fns[0]

        if len(fns) == 0:
            return

        try:
            idns = []
            for filename in fns:
                obj = object_class(
                    database_name=self.database_name,
                    mongo=self.mongo, server=self.server)
                obj.read_file(filename)
                idn = obj.db_save()
                idns.append(idn)
            msg = _QCoreApplication.translate(
                '', 'Added to database table.\nIDs: ' + str(idns))
            self.update_database_tables()
            title = _QCoreApplication.translate('', 'Information')
            _QMessageBox.information(self, title, msg, _QMessageBox.Ok)
        except Exception:
            _traceback.print_exc(file=_sys.stdout)
            msg = _QCoreApplication.translate(
                '', 'Failed to read files and save values in database.')
            title = _QCoreApplication.translate('', 'Failure')
            _QMessageBox.critical(self, title, msg, _QMessageBox.Ok)
            return

    def save_files(self):
        """Save database record to file."""
        try:
            table_name = self.twg_database.get_current_table_name()
            if table_name is None:
                return

            object_class = self._table_object_dict[table_name]

            idns = self.twg_database.get_table_selected_ids(table_name)
            nr_idns = len(idns)
            if nr_idns == 0:
                return

            objs = []
            fns = []
            try:
                for i in range(nr_idns):
                    idn = idns[i]
                    obj = object_class(
                        database_name=self.database_name,
                        mongo=self.mongo, server=self.server)
                    obj.db_read(idn)
                    default_filename = obj.default_filename
                    objs.append(obj)
                    fns.append(default_filename)

            except Exception:
                _traceback.print_exc(file=_sys.stdout)
                msg = _QCoreApplication.translate(
                    '', 'Failed to read database entries.')
                title = _QCoreApplication.translate('', 'Failure')
                _QMessageBox.critical(self, title, msg, _QMessageBox.Ok)
                return

            if nr_idns == 1:
                caption = _QCoreApplication.translate('', 'Save file')
                filename = _QFileDialog.getSaveFileName(
                    self, caption=caption,
                    directory=_os.path.join(self.directory, fns[0]),
                    filter="Text files (*.txt *.dat)")

                if isinstance(filename, tuple):
                    filename = filename[0]

                if len(filename) == 0:
                    return

                fns[0] = filename
            else:
                caption = _QCoreApplication.translate('', 'Save files')
                directory = _QFileDialog.getExistingDirectory(
                    self, caption=caption, directory=self.directory)

                if isinstance(directory, tuple):
                    directory = directory[0]

                if len(directory) == 0:
                    return

                for i in range(len(fns)):
                    fns[i] = _os.path.join(directory, fns[i])

            try:
                for i in range(nr_idns):
                    obj = objs[i]
                    idn = idns[i]
                    filename = fns[i]
                    if (not filename.endswith('.txt') and
                       not filename.endswith('.dat')):
                        filename = filename + '.txt'
                    obj.save_file(filename)
            except Exception:
                _traceback.print_exc(file=_sys.stdout)
                msg = _QCoreApplication.translate(
                    '', 'Failed to save files.')
                title = _QCoreApplication.translate('', 'Failure')
                _QMessageBox.critical(self, title, msg, _QMessageBox.Ok)
        except Exception:
            _traceback.print_exc(file=_sys.stdout)

    def update_database_tables(self):
        """Update database tables."""
        if not self.isVisible():
            return

        try:
            self.twg_database.database_name = self.database_name
            self.twg_database.mongo = self.mongo
            self.twg_database.server = self.server
            if self.ui.chb_short_version.isChecked():
                hidden_tables = self.short_version_hidden_tables
                self.twg_database.hidden_tables = hidden_tables
            else:
                self.twg_database.hidden_tables = []
            self.twg_database.update_database_tables()
            self.disable_invalid_buttons()
        except Exception:
            _traceback.print_exc(file=_sys.stdout)
