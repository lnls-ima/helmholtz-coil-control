# -*- coding: utf-8 -*-

"""Main window for the control application."""

import sys as _sys
import traceback as _traceback
from qtpy.QtWidgets import (
    QFileDialog as _QFileDialog,
    QMainWindow as _QMainWindow,
    QApplication as _QApplication,
    QDesktopWidget as _QDesktopWidget,
    )
import qtpy.uic as _uic

from helmholtz.gui import utils as _utils
from helmholtz.gui.auxiliarywidgets import (
    SelectTabsDialog as _SelectTabsDialog,
    LogDialog as _LogDialog
    )
from helmholtz.gui.connectionwidget import ConnectionWidget \
    as _ConnectionWidget
from helmholtz.gui.temperaturewidget import TemperatureWidget \
    as _TemperatureWidget
from helmholtz.gui.motorintegratorwidget import MotorIntegratorWidget \
    as _MotorIntegratorWidget
from helmholtz.gui.measurementwidget import MeasurementWidget \
    as _MeasurementWidget
from helmholtz.gui.databasewidget import DatabaseWidget \
    as _DatabaseWidget
from helmholtz.gui.blockpositionwidget import BlockPositionWidget \
    as _BlockPositionWidget
from helmholtz.devices import logfile as _logfile


class MainWindow(_QMainWindow):
    """Main Window class for the control application."""

    def __init__(
            self, parent=None, width=_utils.WINDOW_WIDTH,
            height=_utils.WINDOW_HEIGHT):
        """Set up the ui and add main tabs."""
        super().__init__(parent)

        # setup the ui
        uifile = _utils.get_ui_file(self)
        self.ui = _uic.loadUi(uifile, self)
        self.resize(width, height)

        # clear the current tabs
        self.ui.twg_main.clear()

        # define tab names and corresponding widgets
        if _utils.TRANSLATE:
            self.tab_names = [
                'conexao',
                'temperatura',
                'motor_e_integrador',
                'medida',
                'posicionamento_do_bloco',
                'banco_de_dados',
                ]
        
        else:
            self.tab_names = [
                'connection',
                'temperature',
                'motor_and_integrator',
                'measurement',
                'block_position',
                'database',
                ]

        self.tab_widgets = [
            _ConnectionWidget,
            _TemperatureWidget,
            _MotorIntegratorWidget,
            _MeasurementWidget,
            _BlockPositionWidget,
            _DatabaseWidget,
            ]

        # add select tabs dialog
        self.select_tabs_dialog = _SelectTabsDialog(self.tab_names)
        for tab_name in self.tab_names:
            chb = getattr(self.select_tabs_dialog, 'chb_' + tab_name)
            chb.setChecked(True)
       
        self.select_tabs_dialog.tab_selection_changed.connect(self.change_tabs)

        self.log_dialog = _LogDialog()

        # show database name
        self.ui.le_database.setText(self.database_name)

        # connect signals and slots
        self.select_tabs_dialog.emit_tab_selection_signal()
        self.connect_signal_slots()

        self.configure_gui_visualization()

    @property
    def database_name(self):
        """Return the database name."""
        return _QApplication.instance().database_name

    @database_name.setter
    def database_name(self, value):
        _QApplication.instance().database_name = value

    @property
    def directory(self):
        """Return the default directory."""
        return _QApplication.instance().directory

    @property
    def advanced_options_dialog(self):
        """Advanced options dialog."""
        return _QApplication.instance().advanced_options_dialog

    @property
    def find_trigger_dialog(self):
        """Find trigger dialog."""
        return _QApplication.instance().find_trigger_dialog

    def configure_gui_visualization(self):
        if _utils.SIMPLE:
            self.ui.fm_options.hide()
        else:
            self.ui.fm_options.show()

    def closeEvent(self, event):
        """Close main window and dialogs."""
        try:
            for idx in range(self.ui.twg_main.count()):
                widget = self.ui.twg_main.widget(idx)
                widget.close()
            self.advanced_options_dialog.close()
            self.select_tabs_dialog.close()
            self.log_dialog.close()
            event.accept()
        except Exception:
            _traceback.print_exc(file=_sys.stdout)
            event.accept()

    def change_database(self):
        """Change database file."""
        fn = _QFileDialog.getOpenFileName(
            self, caption='Database file', directory=self.directory,
            filter="Database File (*.db)")

        if isinstance(fn, tuple):
            fn = fn[0]

        if len(fn) == 0:
            return

        self.database_name = fn
        self.ui.le_database.setText(self.database_name)

    def change_tabs(self, tab_status):
        """Hide or show tabs."""
        try:
            if self.ui.twg_main.count() != 0:
                tab_current = self.ui.twg_main.currentWidget()
            else:
                tab_current = None

            self.ui.twg_main.clear()
            for idx, tab_name in enumerate(self.tab_names):
                tab_attr = 'tab_' + tab_name
                tab_name_split = tab_name.split('_')
                tab_label = ' '.join([s.capitalize() for s in tab_name_split])
                status = tab_status[tab_name]
                if status:
                    if hasattr(self, tab_attr):
                        tab = getattr(self, tab_attr)
                    else:
                        tab = self.tab_widgets[idx]()
                        setattr(self, tab_attr, tab)
                    self.ui.twg_main.addTab(tab, tab_label)

            if tab_current is not None:
                idx = self.ui.twg_main.indexOf(tab_current)
                self.ui.twg_main.setCurrentIndex(idx)

        except Exception:
            _traceback.print_exc(file=_sys.stdout)

    def centralize_window(self):
        """Centralize window."""
        window_center = _QDesktopWidget().availableGeometry().center()
        self.move(
            window_center.x() - self.geometry().width()/2,
            window_center.y() - self.geometry().height()/2)

    def connect_signal_slots(self):
        """Create signal/slot connections."""
        self.ui.tbt_select_tabs.clicked.connect(self.select_tabs_dialog.show)
        self.ui.tbt_database.clicked.connect(self.change_database)
        self.ui.tbt_log.clicked.connect(self.open_log)
        self.ui.pbt_advanced_options.clicked.connect(
            self.advanced_options_dialog.show)

    def open_log(self):
        """Open log info."""
        try:
            with open(_logfile, 'r') as f:
                text = f.read()
            self.log_dialog.te_text.setText(text)
            vbar = self.log_dialog.te_text.verticalScrollBar()
            vbar.setValue(vbar.maximum())
            self.log_dialog.show()
        except Exception:
            _traceback.print_exc(file=_sys.stdout)
