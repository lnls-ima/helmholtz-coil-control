# -*- coding: utf-8 -*-

"""Measurement widget for the control application."""

import sys as _sys
import traceback as _traceback
import numpy as _np
from qtpy.QtWidgets import (
    QDialog as _QDialog,
    QMessageBox as _QMessageBox,
    QApplication as _QApplication,
    )
from qtpy.QtGui import QFont as _QFont
from qtpy.QtCore import (
    QCoreApplication as _QCoreApplication,
    )
import qtpy.uic as _uic

from helmholtz.gui import utils as _utils
import pyqtgraph as _pyqtgraph


class FindTriggerDialog(_QDialog):
    """Find trigger dialog."""

    def __init__(self, parent=None):
        """Set up the ui."""
        super().__init__(parent)
        uifile = _utils.get_ui_file(self)
        self.ui = _uic.loadUi(uifile, self)

        self.graph_1 = None
        self.graph_2 = None
        self.trigger_avg = None
        self.trigger_list = []
        self.mx_list_1 = []
        self.mx_list_2 = []

        self.graph_linewidth = _utils.PLOT_LINE_WIDTH
        self.graph_symbolsize = _utils.PLOT_MARKER_SIZE
        self.graph_fontsize = _utils.PLOT_FONT_SIZE
        self.graph_label_style = {
            'font-size': '{0:d}px'.format(self.graph_fontsize)}
        self.graph_font = _QFont()
        self.graph_font.setPixelSize(self.graph_fontsize)

        self.connect_signal_slots()

    @property
    def advanced_options(self):
        """Return global advanced options."""
        dialog = _QApplication.instance().advanced_options_dialog
        return dialog.config

    @property
    def advanced_options_dialog(self):
        """Advanced options dialog."""
        return _QApplication.instance().advanced_options_dialog

    def accept(self):
        """Close dialog."""
        self.clear()
        super().accept()

    def clear(self):
        """Clear."""
        self.trigger_avg = None
        self.mx_list_1 = []
        self.mx_list_2 = []
        self.clear_plots()
        self.ui.la_updated_led.setEnabled(False)
        self.ui.lcd_trigger.setEnabled(False)

    def clear_plots(self):
        self.ui.pw_graph_2.plotItem.curves.clear()
        self.ui.pw_graph_1.plotItem.curves.clear()
        self.ui.pw_graph_1.clear()
        self.ui.pw_graph_2.clear()
        self.graph_1 = None        
        self.graph_2 = None

    def closeEvent(self, event):
        """Close widget."""
        try:
            self.clear()
            event.accept()
        except Exception:
            _traceback.print_exc(file=_sys.stdout)
            event.accept()

    def connect_signal_slots(self):
        """Create signal/slot connections."""
        self.ui.pbt_update_trigger_config.clicked.connect(self.update_trigger_config)

    def update_trigger_config(self):
        if self.trigger_avg is not None:
            self.advanced_options_dialog.close()
            self.advanced_options.integration_trigger = self.trigger_avg
            self.advanced_options.db_save()
            self.ui.la_updated_led.setEnabled(True)

    def config_and_plot_mag(self):
        """Configure and plot magnetization."""
        try:
            self.clear_plots()            

            color_1 = (0, 255, 0)
            color_2 = (0, 0, 255)

            pen = _pyqtgraph.mkPen(color=color_1, width=self.graph_linewidth)
            self.graph_1 = self.ui.pw_graph_1.plotItem.plot(
                self.trigger_list,
                self.mx_list_1,
                symbol='o',
                symbolPen=color_1,
                symbolSize=self.graph_symbolsize,
                symbolBrush=color_1)
            self.graph_1.setPen(pen)
            
            pen = _pyqtgraph.mkPen(color=color_2, width=self.graph_linewidth)
            self.graph_2 = self.ui.pw_graph_2.plotItem.plot(
                self.trigger_list,
                self.mx_list_2,
                symbol='o',
                symbolPen=color_2,
                symbolSize=self.graph_symbolsize,
                symbolBrush=color_2)
            self.graph_2.setPen(pen)

            self.ui.pw_graph_1.setLabel(
                'left', text='Mx (Initial Position) [T]', **self.graph_label_style)
            self.ui.pw_graph_1.getAxis('left').tickFont = self.graph_font
            self.ui.pw_graph_1.getAxis('left').setStyle(
                tickTextOffset=self.graph_fontsize)

            self.ui.pw_graph_2.setLabel(
                'left', text='Mx (Rotated Position) [T]', **self.graph_label_style)
            self.ui.pw_graph_2.getAxis('left').tickFont = self.graph_font
            self.ui.pw_graph_2.getAxis('left').setStyle(
                tickTextOffset=self.graph_fontsize)

            self.ui.pw_graph_1.setLabel(
                'bottom', text='Trigger', **self.graph_label_style)
            self.ui.pw_graph_1.getAxis('bottom').tickFont = self.graph_font
            self.ui.pw_graph_1.getAxis('bottom').setStyle(
                tickTextOffset=self.graph_fontsize)

            self.ui.pw_graph_2.setLabel(
                'bottom', text='Trigger', **self.graph_label_style)
            self.ui.pw_graph_2.getAxis('bottom').tickFont = self.graph_font
            self.ui.pw_graph_2.getAxis('bottom').setStyle(
                tickTextOffset=self.graph_fontsize)

            self.ui.pw_graph_1.showGrid(x=True, y=True)
            self.ui.pw_graph_2.showGrid(x=True, y=True)
        
        except Exception:
            _traceback.print_exc(file=_sys.stdout)

    def calc_and_plot_fit(self):
        xfit_1, yfit_1, trigger_1 = _linear_fit(self.trigger_list, self.mx_list_1)
        self.ui.le_trigger_initial_pos.setText('{0:.0f}'.format(trigger_1))
        self.ui.pw_graph_1.plotItem.plot(xfit_1, yfit_1, pen=(0, 0, 0))

        xfit_2, yfit_2, trigger_2 = _linear_fit(self.trigger_list, self.mx_list_2)
        self.ui.le_trigger_rotated_pos.setText('{0:.0f}'.format(trigger_2))
        self.ui.pw_graph_2.plotItem.plot(xfit_2, yfit_2, pen=(0, 0, 0))

        trigger_avg = _np.mean([trigger_1, trigger_2])
        if not _np.isnan(trigger_avg):
            self.trigger_avg = int(trigger_avg)
            self.ui.lcd_trigger.display(self.trigger_avg)
            self.ui.lcd_trigger.setEnabled(True)
        else:
            self.trigger_avg = None
            self.ui.lcd_trigger.setEnabled(False)

    def show(self, trigger_list, mx_list_1, mx_list_2):
        try:
            self.trigger_list = trigger_list
            self.mx_list_1 = mx_list_1
            self.mx_list_2 = mx_list_2
            self.config_and_plot_mag()
            self.calc_and_plot_fit()
            super().show()
            
        except Exception:
            _traceback.print_exc(file=_sys.stdout)
            msg = _QCoreApplication.translate('', 'Failed to show trigger dialog.')
            title = _QCoreApplication.translate('', 'Failure')
            _QMessageBox.critical(self, title, msg, _QMessageBox.Ok)


def _linear_fit(x, y):
    if len(x) != len(y) or len(x) < 2:
        xfit = []
        yfit = []
        x0 = _np.nan
    
    else:
        try:
            poly = _np.polynomial.polynomial.polyfit(x, y, 1)
            xfit = _np.linspace(x[0], x[-1], 100)
            yfit = _np.polynomial.polynomial.polyval(xfit, poly)

            if poly[1] != 0:
                x0 = -poly[0]/poly[1]
            else:
                x0 = _np.nan

        except Exception:
            _traceback.print_exc(file=_sys.stdout)
            xfit = []
            yfit = []
            x0 = _np.nan
    
    return xfit, yfit, x0