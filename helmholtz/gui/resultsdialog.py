# -*- coding: utf-8 -*-

"""View data dialog for the Hall Bench Control application."""

import sys as _sys
import collections as _collections
import warnings as _warnings
import traceback as _traceback
import numpy as _np
import pandas as _pd
import scipy.optimize as _optimize
import scipy.integrate as _integrate
from qtpy.QtWidgets import (
    QDialog as _QDialog,
    QVBoxLayout as _QVBoxLayout,
    QMessageBox as _QMessageBox,
    QApplication as _QApplication,
    QTableWidgetItem as _QTableWidgetItem,
    )
from qtpy.QtGui import QFont as _QFont
from qtpy.QtCore import Qt as _Qt
import qtpy.uic as _uic
import pyqtgraph as _pyqtgraph

from helmholtz.gui import utils as _utils


class ResultsDialog(_QDialog):
    """Results dialog class for the control application."""

    def __init__(self, parent=None):
        """Set up the ui and create connections."""
        super().__init__(parent)

        uifile = _utils.get_ui_file(self)
        self.ui = _uic.loadUi(uifile, self)

        self.measurement_list = []
        self.mx = []
        self.my = []
        self.mz = []
        self.graph_mx = None
        self.graph_my = None
        self.graph_mz = None
        self.graph_right = None
        self.xmin_line = None
        self.xmax_line = None

        self.axis_label_dict = {
            'temperature': 'Temperature [degC]',
            'volume': 'Volume [mm3]',
        }

        for key in self.axis_label_dict.keys():
            self.ui.cmb_bottom_axis.addItem(key)
            self.ui.cmb_right_axis.addItem(key)

        # Create legend
        self.legend = _pyqtgraph.LegendItem(offset=(70, 30))
        self.legend.setParentItem(self.ui.pw_graph.graphicsItem())
        self.legend.setAutoFillBackground(1)
        self.legend_items = []

        self.connect_signal_slots()

    def accept(self):
        """Close dialog."""
        self.clear()
        super().accept()

    def closeEvent(self, event):
        """Close widget."""
        try:
            self.clear()
            event.accept()
        except Exception:
            _traceback.print_exc(file=_sys.stdout)
            event.accept()

    def calc_curve_fit(self):
        """Calculate curve fit."""
        try:
            plots = self.get_selected_plots()
            if len(plots) == 0:
                return

            x, y = self.get_x_y()

            func = self.ui.cmb_fitfunction.currentText()
            if func.lower() == 'linear':
                xfit, yfit, param, label = _linear_fit(x, y)
            elif func.lower() == 'polynomial':
                order = self.ui.sb_polyorder.value()
                xfit, yfit, param, label = _polynomial_fit(x, y, order)
            elif func.lower() == 'gaussian':
                xfit, yfit, param, label = _gaussian_fit(x, y)
            else:
                xfit = []
                yfit = []
                param = {}
                label = ''

            self.ui.la_fitfunction.setText(label)
            self.ui.tbl_fit.clearContents()
            self.ui.tbl_fit.setRowCount(len(param))
            rcount = 0
            for key, value in param.items():
                self.ui.tbl_fit.setItem(
                    rcount, 0, _QTableWidgetItem(str(key)))
                self.ui.tbl_fit.setItem(
                    rcount, 1, _QTableWidgetItem(str(value)))
                rcount = rcount + 1

            self.update_plot()
            self.ui.pw_graph.plotItem.plot(xfit, yfit, pen=(0, 0, 0))

        except Exception:
            _traceback.print_exc(file=_sys.stdout)

    def clear(self):
        """Clear all."""
        self.measurement_list = []
        self.mx = []
        self.my = []
        self.mz = []
        self.xmin_line = None
        self.xmax_line = None
        self.clear_fit()
        self.clear_graph()

    def clear_fit(self):
        """Clear fit."""
        self.ui.tbl_fit.clearContents()
        self.ui.tbl_fit.setRowCount(0)
        self.ui.la_fitfunction.setText('')

    def clear_graph(self):
        """Clear plots."""
        for item in self.legend_items:
            self.legend.removeItem(item)
        self.legend_items = []
        self.ui.pw_graph.plotItem.curves.clear()
        self.ui.pw_graph.clear()
        self.graph_mx = None
        self.graph_my = None
        self.graph_mz = None
        self.graph_right = None

    def configure_graph(self, bottom_axis_attr=None, right_axis_attr=None):
        """Configure graph."""
        self.clear_graph()

        color_mx = (255, 0, 0)
        color_my = (0, 255, 0)
        color_mz = (0, 0, 255)
        color_right_axis = (0, 0, 0)

        width = _utils.PLOT_LINE_WIDTH
        font_str = '{0:d}px'.format(_utils.PLOT_FONT_SIZE)
        label_style = {'font-size': font_str}
        font = _QFont()
        font.setPixelSize(_utils.PLOT_FONT_SIZE)

        pen = _pyqtgraph.mkPen(color=color_mx, width=width)
        self.graph_mx = self.ui.pw_graph.plotItem.plot(
            _np.array([]),
            _np.array([]))
        self.graph_mx.setPen(pen)

        pen = _pyqtgraph.mkPen(color=color_my, width=width)
        self.graph_my = self.ui.pw_graph.plotItem.plot(
            _np.array([]),
            _np.array([]))
        self.graph_my.setPen(pen)

        pen = _pyqtgraph.mkPen(color=color_mz, width=width)
        self.graph_mz = self.ui.pw_graph.plotItem.plot(
            _np.array([]), _np.array([]))
        self.graph_mz.setPen(pen)

        self.legend_items = ['Mx', 'My', 'Mz']
        self.legend.addItem(self.graph_mx, self.legend_items[0])
        self.legend.addItem(self.graph_my, self.legend_items[1])
        self.legend.addItem(self.graph_mz, self.legend_items[2])

        self.ui.pw_graph.setLabel(
            'left', text='Magnetization [T]', **label_style)

        self.ui.pw_graph.getAxis('left').tickFont = font
        self.ui.pw_graph.getAxis('left').setStyle(
            tickTextOffset=_utils.PLOT_FONT_SIZE)

        if bottom_axis_attr is None or bottom_axis_attr == '':
            bottom_axis_label = ''
        else:
            bottom_axis_label = self.axis_label_dict[bottom_axis_attr]
        self.ui.pw_graph.setLabel(
            'bottom', text=bottom_axis_label, **label_style)
        self.ui.pw_graph.getAxis('bottom').tickFont = font
        self.ui.pw_graph.getAxis('bottom').setStyle(
            tickTextOffset=_utils.PLOT_FONT_SIZE)

        if right_axis_attr is not None and right_axis_attr != '':
            right_axis_label = self.axis_label_dict[right_axis_attr]
            pen = _pyqtgraph.mkPen(color=color_right_axis, width=width)
            right_axis = _utils.plot_item_add_first_right_axis(
                self.ui.pw_graph.plotItem)
            self.graph_right = _pyqtgraph.PlotDataItem(
                _np.array([]), _np.array([]))
            self.graph_right.setPen(pen)
            right_axis.linkedView().addItem(self.graph_right)

            right_axis.setLabel(right_axis_label, **label_style)
            right_axis.tickFont = font
            right_axis.setStyle(
                tickTextOffset=_utils.PLOT_FONT_SIZE)

            self.legend_items.append(right_axis_attr)
            self.legend.addItem(self.graph_right, right_axis_attr)

        self.ui.pw_graph.showGrid(x=True, y=True)

    def connect_signal_slots(self):
        """Create signal/slot connections."""
        self.ui.cmb_bottom_axis.currentIndexChanged.connect(
            self.update_xlimits)
        self.ui.pbt_update_plot.clicked.connect(self.update_plot)
        self.ui.chb_mx.stateChanged.connect(self.update_controls_and_plot)
        self.ui.chb_my.stateChanged.connect(self.update_controls_and_plot)
        self.ui.chb_mz.stateChanged.connect(self.update_controls_and_plot)
        self.ui.cmb_bottom_axis.currentIndexChanged.connect(
            self.update_controls_and_plot)
        self.ui.cmb_right_axis.currentIndexChanged.connect(
            self.update_controls_and_plot)
        self.ui.chb_bottom_axis.stateChanged.connect(
            self.update_controls_and_plot)
        self.ui.chb_right_axis.stateChanged.connect(
            self.update_controls_and_plot)
        self.ui.chb_bottom_axis.stateChanged.connect(
            self.enabled_bottom_axis_selection)
        self.ui.chb_right_axis.stateChanged.connect(
            self.enabled_right_axis_selection)
        self.ui.cmb_fitfunction.currentIndexChanged.connect(
            self.fit_function_changed)
        self.ui.pbt_fit.clicked.connect(self.calc_curve_fit)
        self.ui.pbt_resetlim.clicked.connect(self.reset_xlimits)

    def update_xlimits(self):
        x = self.get_bottom_axis_data()
        self.ui.sbd_xmin.setValue(_np.min(x))
        self.ui.sbd_xmax.setValue(_np.max(x))

    def enabled_bottom_axis_selection(self):
        if self.ui.chb_bottom_axis.isChecked():
            self.ui.cmb_bottom_axis.setEnabled(True)
        else:
            self.ui.cmb_bottom_axis.setEnabled(False)

    def enabled_right_axis_selection(self):
        if self.ui.chb_right_axis.isChecked():
            self.ui.cmb_right_axis.setEnabled(True)
        else:
            self.ui.cmb_right_axis.setEnabled(False)

    def get_selected_plots(self):
        """Get all selected scans and components."""
        try:
            plots = []
            if self.ui.chb_mx.isChecked():
                plots.append('mx')
            if self.ui.chb_my.isChecked():
                plots.append('my')
            if self.ui.chb_mz.isChecked():
                plots.append('mz')
            if self.ui.chb_right_axis.isChecked():
                plots.append(
                    self.ui.cmb_right_axis.currentText())
            return plots

        except Exception:
            _traceback.print_exc(file=_sys.stdout)
            return None

    def get_bottom_axis_data(self):
        try:
            if self.ui.chb_bottom_axis.isChecked():
                bottom_axis_attr = self.ui.cmb_bottom_axis.currentText()
                x = []
                for m in self.measurement_list:
                    x.append(getattr(m, bottom_axis_attr))
                return x
            else:
                return list(range(len(self.measurement_list)))

        except Exception:
            return list(range(len(self.measurement_list)))

    def get_right_axis_data(self):
        try:
            if self.ui.chb_right_axis.isChecked():
                right_axis_attr = self.ui.cmb_right_axis.currentText()
                y = []
                for m in self.measurement_list:
                    y.append(getattr(m, right_axis_attr))
                return y
            else:
                return []
        except Exception:
            return []

    def fit_function_changed(self):
        """Hide or show polynomial fitting order and update dict value."""
        self.clear_fit()
        self.update_plot()
        func = self.ui.cmb_fitfunction.currentText()
        if func.lower() == 'polynomial':
            self.ui.la_polyorder.show()
            self.ui.sb_polyorder.show()
        else:
            self.ui.la_polyorder.hide()
            self.ui.sb_polyorder.hide()

    def get_x_y(self):
        """Get X, Y values."""
        xdata = self.get_bottom_axis_data()
        plots = self.get_selected_plots()

        if len(plots) == 0:
            return [], []

        if 'mx' in plots:
            ydata = self.mx
        elif 'my' in plots:
            ydata = self.my
        elif 'mz' in plots:
            ydata = self.mz
        else:
            ydata = self.get_right_axis_data()

        sorted_data = _np.array(sorted(zip(xdata, ydata)))
        x = sorted_data[:, 0]
        y = sorted_data[:, 1]

        xmin = self.ui.sbd_xmin.value()
        xmax = self.ui.sbd_xmax.value()

        y = y[(x >= xmin) & (x <= xmax)]
        x = x[(x >= xmin) & (x <= xmax)]
        return x, y

    def reset_xlimits(self):
        """Reset X limits.."""
        x = self.get_bottom_axis_data()

        if len(x) > 0:
            xmin = _np.min(x)
            xmax = _np.max(x)
        else:
            xmin = 0
            xmax = 0

        self.ui.sbd_xmin.setValue(xmin)
        self.ui.sbd_xmax.setValue(xmax)
        self.update_plot()

    def show(self, measurement_list):
        """Update data and show dialog."""
        try:
            if measurement_list is None or len(measurement_list) == 0:
                msg = 'Invalid data list.'
                _QMessageBox.critical(self, 'Failure', msg, _QMessageBox.Ok)
                return

            self.measurement_list = measurement_list

            self.mx = []
            self.my = []
            self.mz = []
            for m in measurement_list:
                self.mx.append(m.mx_avg)
                self.my.append(m.my_avg)
                self.mz.append(m.mz_avg)

            self.ui.la_polyorder.hide()
            self.ui.sb_polyorder.hide()
            self.update_controls_and_plot()
            super().show()

        except Exception:
            _traceback.print_exc(file=_sys.stdout)
            msg = 'Failed to show dialog.'
            _QMessageBox.critical(self, 'Failure', msg, _QMessageBox.Ok)
            return

    def update_controls(self):
        """Enable or disable group boxes."""
        self.clear_fit()

        plots = self.get_selected_plots()
        if len(plots) == 1:
            self.ui.gb_xlimits.setEnabled(True)
            self.ui.gb_fit.setEnabled(True)
        else:
            self.ui.gb_xlimits.setEnabled(False)
            self.ui.gb_fit.setEnabled(False)

    def update_controls_and_plot(self):
        """Update controls and plot."""
        self.update_controls()
        self.update_plot()

    def update_plot(self):
        """Update plot."""
        try:
            self.clear_graph()

            plots = self.get_selected_plots()

            if len(plots) == 0:
                show_xlines = False
                return

            if len(plots) > 1:
                show_xlines = False
            else:
                show_xlines = True

            if self.ui.chb_bottom_axis.isChecked():
                bottom_axis_attr = self.ui.cmb_bottom_axis.currentText()
            else:
                bottom_axis_attr = None

            if self.ui.chb_right_axis.isChecked():
                right_axis_attr = self.ui.cmb_right_axis.currentText()
            else:
                right_axis_attr = None

            self.configure_graph(
                bottom_axis_attr=bottom_axis_attr,
                right_axis_attr=right_axis_attr)

            with _warnings.catch_warnings():
                _warnings.simplefilter("ignore")
                x = self.get_bottom_axis_data()

                if 'mx' in plots:
                    sorted_data = _np.array(sorted(zip(x, self.mx)))
                    x_sorted = sorted_data[:, 0]
                    mx_sorted = sorted_data[:, 1]
                    self.graph_mx.setData(x_sorted, mx_sorted)
                if 'my' in plots:
                    sorted_data = _np.array(sorted(zip(x, self.my)))
                    x_sorted = sorted_data[:, 0]
                    my_sorted = sorted_data[:, 1]
                    self.graph_my.setData(x_sorted, my_sorted)
                if 'mz' in plots:
                    sorted_data = _np.array(sorted(zip(x, self.mz)))
                    x_sorted = sorted_data[:, 0]
                    mz_sorted = sorted_data[:, 1]
                    self.graph_mz.setData(x_sorted, mz_sorted)

                if right_axis_attr:
                    right_data = self.get_right_axis_data()
                    sorted_data = _np.array(sorted(zip(x, right_data)))
                    x_sorted = sorted_data[:, 0]
                    right_data_sorted = sorted_data[:, 1]
                    self.graph_right.setData(x_sorted, right_data_sorted)

            if show_xlines:
                xmin = self.ui.sbd_xmin.value()
                xmax = self.ui.sbd_xmax.value()

                self.xmin_line = _pyqtgraph.InfiniteLine(
                    xmin, pen=(0, 0, 0), movable=True)
                self.ui.pw_graph.addItem(self.xmin_line)
                self.xmin_line.sigPositionChangeFinished.connect(
                    self.update_xmin_spin_box)

                self.xmax_line = _pyqtgraph.InfiniteLine(
                    xmax, pen=(0, 0, 0), movable=True)
                self.ui.pw_graph.addItem(self.xmax_line)
                self.xmax_line.sigPositionChangeFinished.connect(
                    self.update_xmax_spin_box)
            else:
                self.xmin_line = None
                self.xmax_line = None

        except Exception:
            _traceback.print_exc(file=_sys.stdout)
            return

    def update_xmax_spin_box(self):
        """Update xmax value."""
        self.ui.sbd_xmax.setValue(self.xmax_line.pos()[0])

    def update_xmin_spin_box(self):
        """Update xmin value."""
        self.ui.sbd_xmin.setValue(self.xmin_line.pos()[0])


def _linear_fit(x, y):
    label = 'y = K0 + K1*x'

    if len(x) != len(y) or len(x) < 2:
        xfit = []
        yfit = []
        param = {}

    else:
        try:
            p = _np.polyfit(x, y, 1)
            xfit = _np.linspace(x[0], x[-1], 100)
            yfit = _np.polyval(p, xfit)

            prev = p[::-1]
            if prev[1] != 0:
                x0 = - prev[0]/prev[1]
            else:
                x0 = _np.nan
            param = _collections.OrderedDict([
                ('K0', prev[0]),
                ('K1', prev[1]),
                ('x (y=0)', x0),
            ])
        except Exception:
            _traceback.print_exc(file=_sys.stdout)
            xfit = []
            yfit = []
            param = {}

    return (xfit, yfit, param, label)


def _polynomial_fit(x, y, order):
    label = 'y = K0 + K1*x + K2*x^2 + ...'

    if len(x) != len(y) or len(x) < order + 1:
        xfit = []
        yfit = []
        param = {}

    else:
        try:
            p = _np.polyfit(x, y, order)
            xfit = _np.linspace(x[0], x[-1], 100)
            yfit = _np.polyval(p, xfit)
            prev = p[::-1]
            _dict = {}
            for i in range(len(prev)):
                _dict['K' + str(i)] = prev[i]
            param = _collections.OrderedDict(_dict)
        except Exception:
            _traceback.print_exc(file=_sys.stdout)
            xfit = []
            yfit = []
            param = {}

    return (xfit, yfit, param, label)


def _gaussian_fit(x, y):
    label = 'y = y0 + A*exp(-(x-x0)^2/(2*Sigma^2))'

    def gaussian(x, y0, a, x0, sigma):
        return y0 + a*_np.exp(-(x-x0)**2/(2*sigma**2))

    try:
        mean = sum(x * y) / sum(y)
        sigma = _np.sqrt(sum(y * (x - mean)**2) / sum(y))
        if mean <= _np.max(y):
            a = _np.max(y)
            y0 = _np.min(y)
        else:
            a = _np.min(y)
            y0 = _np.max(y)

        popt, pcov = _optimize.curve_fit(
            gaussian, x, y, p0=[y0, a, mean, sigma])

        xfit = _np.linspace(x[0], x[-1], 100)
        yfit = gaussian(xfit, popt[0], popt[1], popt[2], popt[3])

        param = _collections.OrderedDict([
            ('y0', popt[0]),
            ('A', popt[1]),
            ('x0', popt[2]),
            ('Sigma', popt[3]),
        ])
    except Exception:
        _traceback.print_exc(file=_sys.stdout)
        xfit = []
        yfit = []
        param = {}

    return (xfit, yfit, param, label)
