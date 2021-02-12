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
from qtpy.QtCore import (
    Qt as _Qt,
    QCoreApplication as _QCoreApplication,
    )
import qtpy.uic as _uic
import pyqtgraph as _pyqtgraph

import helmholtz.data as _data
from helmholtz.gui import utils as _utils
from helmholtz.gui.auxiliarywidgets import (
    CheckableComboBox as _CheckableComboBox,
    )


class ResultsDialog(_QDialog):
    """Results dialog class for the control application."""

    def __init__(self, parent=None):
        """Set up the ui and create connections."""
        super().__init__(parent)

        uifile = _utils.get_ui_file(self)
        self.ui = _uic.loadUi(uifile, self)

        self.measurement_list = []
        self.measurement_idns = []
        self.integration_trigger_list = []
        self.volume_list = []
        self.temperature_list = []
        self.mx = []
        self.my = []
        self.mz = []
        self.graph_mx = None
        self.graph_my = None
        self.graph_mz = None
        self.xmin_line = None
        self.xmax_line = None
        self.graph_vol = None
        self.graph_temp = None
        self.graph_iv_1 = None
        self.graph_iv_2 = None
        self.max_nr_tunrs = 10

        # Plot parameters
        self.graph_linewidth = _utils.PLOT_LINE_WIDTH
        self.graph_symbolsize = _utils.PLOT_MARKER_SIZE
        self.graph_fontsize = _utils.PLOT_FONT_SIZE
        self.graph_label_style = {
            'font-size': '{0:d}px'.format(self.graph_fontsize)}
        self.graph_font = _QFont()
        self.graph_font.setPixelSize(self.graph_fontsize)

        # Create legends
        self.legend_mag = _pyqtgraph.LegendItem(offset=(70, 30))
        self.legend_mag.setParentItem(self.ui.pw_graph_mag.graphicsItem())
        self.legend_mag.setAutoFillBackground(1)
        self.legend_mag_items = []

        self.legend_iv = _pyqtgraph.LegendItem(offset=(70, 30))
        self.legend_iv.setParentItem(self.ui.pw_graph_iv_1.graphicsItem())
        self.legend_iv.setAutoFillBackground(1)
        self.legend_iv_items = []

        # Add combo box
        self.cmb_idns = _CheckableComboBox()
        self.ui.hlt_select_ids.addWidget(self.cmb_idns)

        self.connect_signal_slots()

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
            plots = self.get_selected_plots_mag()
            if len(plots) == 0:
                return

            x, y = self.get_x_y()

            func = self.ui.cmb_fitfunction.currentText()
            if func.lower() == 'linear':
                xfit, yfit, param, label = _linear_fit(x, y)
            elif func.lower() in ('polynomial', 'polinomial'):
                order = self.ui.sb_polyorder.value()
                xfit, yfit, param, label = _polynomial_fit(x, y, order)
            elif func.lower() in ('gaussian', 'gaussiana'):
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

            self.update_plot_mag()
            self.ui.pw_graph_mag.plotItem.plot(xfit, yfit, pen=(0, 0, 0))

        except Exception:
            _traceback.print_exc(file=_sys.stdout)

    def clear(self):
        """Clear all."""
        self.measurement_list = []
        self.measurement_idns = []
        self.integration_trigger_list = []
        self.volume_list = []
        self.temperature_list = []
        self.mx = []
        self.my = []
        self.mz = []
        self.xmin_line = None
        self.xmax_line = None
        self.clear_fit()
        self.cmb_idns.clear()
        self.clear_plots()

    def clear_fit(self):
        """Clear fit."""
        self.ui.tbl_fit.clearContents()
        self.ui.tbl_fit.setRowCount(0)
        self.ui.la_fitfunction.setText('')

    def clear_plots(self):
        self.clear_plot_mag()
        self.clear_plot_iv()
        self.clear_plot_vol_temp()

    def clear_plot_mag(self):
        """Clear magnetization plot."""
        for item in self.legend_mag_items:
            self.legend_mag.removeItem(item)
        self.legend_mag_items = []
        self.ui.pw_graph_mag.plotItem.curves.clear()
        self.ui.pw_graph_mag.clear()
        self.graph_mx = None
        self.graph_my = None
        self.graph_mz = None

    def clear_plot_iv(self):
        """Clear integrated voltage plots."""
        for item in self.legend_iv_items:
            self.legend_iv.removeItem(item)
        self.legend_iv_items = []
        self.ui.pw_graph_iv_1.plotItem.curves.clear()
        self.ui.pw_graph_iv_1.clear()
        self.ui.pw_graph_iv_2.plotItem.curves.clear()
        self.ui.pw_graph_iv_2.clear()
        self.graph_iv_1 = None
        self.graph_iv_2 = None

    def clear_plot_vol_temp(self):
        """Clear volume and temperature plots."""
        self.ui.pw_graph_vol.plotItem.curves.clear()
        self.ui.pw_graph_vol.clear()
        self.ui.pw_graph_temp.plotItem.curves.clear()
        self.ui.pw_graph_temp.clear()
        self.graph_vol = None
        self.graph_temp = None

    def configure_plot_iv(self, selected_idns):
        """Configure integrated voltage plot."""
        try:
            self.clear_plot_iv()

            colors = _utils.COLOR_LIST
            nr_idns = len(selected_idns)
            nr_turns = self.max_nr_tunrs

            if nr_idns > len(colors):
                colors = list(colors)*int(_np.ceil(nr_idns/len(colors)))

            self.graph_iv_1 = []
            self.graph_iv_2 = []
            for i in range(nr_idns):
                pen = _pyqtgraph.mkPen(
                    color=colors[i], width=self.graph_linewidth)
                
                gl1 = []
                gl2 = []
                
                if self.ui.chb_avg.isChecked():
                    plot_data_item = self.ui.pw_graph_iv_1.plotItem.plot(
                        _np.array([]))
                    plot_data_item.setPen(pen)
                    gl1.append(plot_data_item)

                    plot_data_item = self.ui.pw_graph_iv_2.plotItem.plot(
                        _np.array([]))
                    plot_data_item.setPen(pen)
                    gl2.append(plot_data_item)

                else:
                    for j in range(nr_turns):
                        plot_data_item = self.ui.pw_graph_iv_1.plotItem.plot(
                            _np.array([]))
                        plot_data_item.setPen(pen)
                        gl1.append(plot_data_item)

                        plot_data_item = self.ui.pw_graph_iv_2.plotItem.plot(
                            _np.array([]))
                        plot_data_item.setPen(pen)
                        gl2.append(plot_data_item)

                self.graph_iv_1.append(gl1)
                self.graph_iv_2.append(gl2)
                    
                legend_item = 'ID:{0:d}'.format(selected_idns[i])
                self.legend_iv_items.append(legend_item)
                self.legend_iv.addItem(self.graph_iv_1[i][0], legend_item)

            self.ui.pw_graph_iv_1.setLabel(
                'left',
                text='IV Position 1 [V.s]',
                **self.graph_label_style)
            self.ui.pw_graph_iv_1.getAxis('left').tickFont = self.graph_font
            self.ui.pw_graph_iv_1.getAxis('left').setStyle(
                tickTextOffset=self.graph_fontsize)

            self.ui.pw_graph_iv_2.setLabel(
                'left',
                text='IV Position 2 [V.s]',
                **self.graph_label_style)
            self.ui.pw_graph_iv_2.getAxis('left').tickFont = self.graph_font
            self.ui.pw_graph_iv_2.getAxis('left').setStyle(
                tickTextOffset=self.graph_fontsize)

            self.ui.pw_graph_iv_1.setLabel(
                'bottom', text='Number of Points', **self.graph_label_style)
            self.ui.pw_graph_iv_1.getAxis('bottom').tickFont = self.graph_font
            self.ui.pw_graph_iv_1.getAxis('bottom').setStyle(
                tickTextOffset=self.graph_fontsize)

            self.ui.pw_graph_iv_2.setLabel(
                'bottom', text='Number of Points', **self.graph_label_style)
            self.ui.pw_graph_iv_2.getAxis('bottom').tickFont = self.graph_font
            self.ui.pw_graph_iv_2.getAxis('bottom').setStyle(
                tickTextOffset=self.graph_fontsize)

            self.ui.pw_graph_iv_1.showGrid(x=True, y=True)
            self.ui.pw_graph_iv_2.showGrid(x=True, y=True)
        
        except Exception:
            _traceback.print_exc(file=_sys.stdout)

    def configure_plot_vol_temp(self):
        """Configure integrated voltage plot."""
        self.clear_plot_vol_temp()

        color_vol = (0, 255, 0)
        color_temp = (0, 0, 255)

        # Configure volume plot
        pen = _pyqtgraph.mkPen(color=color_vol, width=self.graph_linewidth)
        self.graph_vol = self.ui.pw_graph_vol.plotItem.plot(
            _np.array([]),
            _np.array([]),
            symbol='o',
            symbolPen=color_vol,
            symbolSize=self.graph_symbolsize,
            symbolBrush=color_vol)
        self.graph_vol.setPen(pen)

        self.ui.pw_graph_vol.setLabel(
            'left', text='Volume [cm3]', **self.graph_label_style)
        self.ui.pw_graph_vol.getAxis('left').tickFont = self.graph_font
        self.ui.pw_graph_vol.getAxis('left').setStyle(
            tickTextOffset=self.graph_fontsize)

        self.ui.pw_graph_vol.setLabel(
            'bottom', text='Database ID', **self.graph_label_style)
        self.ui.pw_graph_vol.getAxis('bottom').tickFont = self.graph_font
        self.ui.pw_graph_vol.getAxis('bottom').setStyle(
            tickTextOffset=self.graph_fontsize)

        self.ui.pw_graph_vol.showGrid(x=True, y=True)

        # Configure temperature plot
        pen = _pyqtgraph.mkPen(color=color_temp, width=self.graph_linewidth)
        self.graph_temp = self.ui.pw_graph_temp.plotItem.plot(
            _np.array([]),
            _np.array([]),
            symbol='o',
            symbolPen=color_temp,
            symbolSize=self.graph_symbolsize,
            symbolBrush=color_temp)
        self.graph_temp.setPen(pen)

        self.ui.pw_graph_temp.setLabel(
            'left', text='Temperature [degC]', **self.graph_label_style)
        self.ui.pw_graph_temp.getAxis('left').tickFont = self.graph_font
        self.ui.pw_graph_temp.getAxis('left').setStyle(
            tickTextOffset=self.graph_fontsize)

        self.ui.pw_graph_temp.setLabel(
            'bottom', text='Database ID', **self.graph_label_style)
        self.ui.pw_graph_temp.getAxis('bottom').tickFont = self.graph_font
        self.ui.pw_graph_temp.getAxis('bottom').setStyle(
            tickTextOffset=self.graph_fontsize)

        self.ui.pw_graph_temp.showGrid(x=True, y=True)

    def configure_plot_mag(self):
        """Configure magnetization plot."""
        self.clear_plot_mag()

        color_mx = (255, 0, 0)
        color_my = (0, 255, 0)
        color_mz = (0, 0, 255)

        pen = _pyqtgraph.mkPen(color=color_mx, width=self.graph_linewidth)
        self.graph_mx = self.ui.pw_graph_mag.plotItem.plot(
            _np.array([]),
            _np.array([]),
            symbol='o',
            symbolPen=color_mx,
            symbolSize=self.graph_symbolsize,
            symbolBrush=color_mx)
        self.graph_mx.setPen(pen)

        pen = _pyqtgraph.mkPen(color=color_my, width=self.graph_linewidth)
        self.graph_my = self.ui.pw_graph_mag.plotItem.plot(
            _np.array([]),
            _np.array([]),
            symbol='o',
            symbolPen=color_my,
            symbolSize=self.graph_symbolsize,
            symbolBrush=color_my)
        self.graph_my.setPen(pen)

        pen = _pyqtgraph.mkPen(color=color_mz, width=self.graph_linewidth)
        self.graph_mz = self.ui.pw_graph_mag.plotItem.plot(
            _np.array([]),
            _np.array([]),
            symbol='o',
            symbolPen=color_mz,
            symbolSize=self.graph_symbolsize,
            symbolBrush=color_mz)
        self.graph_mz.setPen(pen)

        self.legend_mag_items = ['Mx', 'My', 'Mz']
        self.legend_mag.addItem(self.graph_mx, self.legend_mag_items[0])
        self.legend_mag.addItem(self.graph_my, self.legend_mag_items[1])
        self.legend_mag.addItem(self.graph_mz, self.legend_mag_items[2])

        self.ui.pw_graph_mag.setLabel(
            'left', text='Magnetization [T]', **self.graph_label_style)

        self.ui.pw_graph_mag.getAxis('left').tickFont = self.graph_font
        self.ui.pw_graph_mag.getAxis('left').setStyle(
            tickTextOffset=self.graph_fontsize)

        xlabel = self.get_bottom_axis_label()
        self.ui.pw_graph_mag.setLabel(
            'bottom', text=xlabel, **self.graph_label_style)
        self.ui.pw_graph_mag.getAxis('bottom').tickFont = self.graph_font
        self.ui.pw_graph_mag.getAxis('bottom').setStyle(
            tickTextOffset=self.graph_fontsize)

        self.ui.pw_graph_mag.showGrid(x=True, y=True)

    def connect_signal_slots(self):
        """Create signal/slot connections."""
        self.ui.pbt_update_plot_mag.clicked.connect(self.update_plot_mag)
        self.ui.chb_mx.stateChanged.connect(
            self.enable_limits_and_update_plot_mag)
        self.ui.chb_my.stateChanged.connect(
            self.enable_limits_and_update_plot_mag)
        self.ui.chb_mz.stateChanged.connect(
            self.enable_limits_and_update_plot_mag)
        self.ui.cmb_fitfunction.currentIndexChanged.connect(
            self.fit_function_changed)
        self.ui.pbt_fit.clicked.connect(self.calc_curve_fit)
        self.ui.pbt_resetlim.clicked.connect(self.reset_xlimits)

        self.ui.pbt_select_all.clicked.connect(
            lambda: self.set_selection_all(True))
        self.ui.pbt_clear_all.clicked.connect(
            lambda: self.set_selection_all(False))
        self.ui.pbt_update_plot_iv.clicked.connect(
            self.update_plot_iv)

        self.ui.pbt_update_plot_vol_temp.clicked.connect(
            self.update_plot_vol_temp)

        self.ui.cmb_bottom_axis.currentIndexChanged.connect(
            self.update_plots)

    def set_selection_all(self, checked):
        """Set selection all."""
        self.blockSignals(True)
        if checked:
            state = _Qt.Checked
        else:
            state = _Qt.Unchecked

        for idx in range(self.cmb_idns.count()):
            item = self.cmb_idns.model().item(idx, 0)
            item.setCheckState(state)

        self.blockSignals(False)
        self.update_plot_iv()

    def update_xlimits(self):
        x = self.get_bottom_axis_data()
        self.ui.sbd_xmin.setValue(_np.min(x))
        self.ui.sbd_xmax.setValue(_np.max(x))

    def get_selected_plots_mag(self):
        """Get all selected scans and components."""
        try:
            plots = []
            if self.ui.chb_mx.isChecked():
                plots.append('mx')
            if self.ui.chb_my.isChecked():
                plots.append('my')
            if self.ui.chb_mz.isChecked():
                plots.append('mz')
            return plots

        except Exception:
            _traceback.print_exc(file=_sys.stdout)
            return None

    def get_selected_plots_iv(self):
        """Get all selected IDs."""
        try:
            selected_idns = [
                int(t) for t in self.cmb_idns.checked_items_text()]
            return selected_idns

        except Exception:
            _traceback.print_exc(file=_sys.stdout)
            return None

    def get_bottom_axis_data(self):
        text = self.ui.cmb_bottom_axis.currentText().lower()
        data = self.measurement_idns
        if text in ('integration trigger',):
            if len(self.integration_trigger_list) > 0:
                data = self.integration_trigger_list
        return data

    def get_bottom_axis_label(self):
        text = self.ui.cmb_bottom_axis.currentText().lower()
        label = 'Database ID'
        if text in ('integration trigger',):
            if len(self.integration_trigger_list) > 0:
                label = 'Integration Trigger'
        return label

    def fit_function_changed(self):
        """Hide or show polynomial fitting order and update dict value."""
        self.clear_fit()
        self.update_plot_mag()
        func = self.ui.cmb_fitfunction.currentText()
        if func.lower() in ('polynomial', 'polinomial'):
            self.ui.la_polyorder.show()
            self.ui.sb_polyorder.show()
        else:
            self.ui.la_polyorder.hide()
            self.ui.sb_polyorder.hide()

    def get_x_y(self):
        """Get X, Y values."""
        xdata = self.get_bottom_axis_data()
        plots = self.get_selected_plots_mag()

        if len(plots) == 0:
            return [], []

        if 'mx' in plots:
            ydata = self.mx
        elif 'my' in plots:
            ydata = self.my
        elif 'mz' in plots:
            ydata = self.mz

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
        self.update_plot_mag()

    def show(self, measurement_list):
        """Update data and show dialog."""
        try:
            if measurement_list is None or len(measurement_list) == 0:
                msg = _QCoreApplication.translate('', 'Invalid data list.')
                title = _QCoreApplication.translate('', 'Failure')
                _QMessageBox.critical(self, title, msg, _QMessageBox.Ok)
                return

            self.measurement_list = measurement_list
            self.measurement_idns = [m.idn for m in measurement_list]

            for index, idn in enumerate(self.measurement_idns):
                self.cmb_idns.addItem(str(idn))
                item = self.cmb_idns.model().item(index, 0)
                item.setCheckState(_Qt.Checked)

            self.mx = []
            self.my = []
            self.mz = []
            self.volume_list = []
            self.temperature_list = []
            for m in self.measurement_list:
                self.mx.append(m.mx_avg)
                self.my.append(m.my_avg)
                self.mz.append(m.mz_avg)
                self.volume_list.append(m.block_volume*1e6)
                self.temperature_list.append(m.block_temperature)

            self.max_nr_tunrs = 10
            self.integration_trigger_list = []
            for m in self.measurement_list:
                adv_opt_idn = m.advanced_options_id
                adv_opt = _data.configuration.AdvancedOptions(
                    database_name=self.database_name,
                    mongo=self.mongo, server=self.server)
                adv_opt.db_read(adv_opt_idn)

                trigger = adv_opt.integration_trigger
                if trigger is None:
                    self.integration_trigger_list = []
                    break

                self.integration_trigger_list.append(trigger)
                if adv_opt.integration_nr_turns > self.max_nr_tunrs:
                    self.max_nr_tunrs = adv_opt.integration_nr_turns

            self.ui.la_polyorder.hide()
            self.ui.sb_polyorder.hide()
            self.cmb_idns.setCurrentIndex(-1)
            self.reset_xlimits()
            self.enable_limits_and_update_plot_mag()
            super().show()

        except Exception:
            _traceback.print_exc(file=_sys.stdout)
            msg = _QCoreApplication.translate('', 'Failed to show dialog.')
            title = _QCoreApplication.translate('', 'Failure')
            _QMessageBox.critical(self, 'Failure', msg, _QMessageBox.Ok)
            return

    def enable_limits(self):
        """Enable or disable group boxes."""
        self.clear_fit()

        plots = self.get_selected_plots_mag()
        if len(plots) == 1:
            self.ui.gb_xlimits.setEnabled(True)
            self.ui.gb_fit.setEnabled(True)
        else:
            self.ui.gb_xlimits.setEnabled(False)
            self.ui.gb_fit.setEnabled(False)

    def enable_limits_and_update_plot_mag(self):
        """Update controls and plot."""
        self.enable_limits()
        self.update_plot_mag()

    def update_plots(self):
        self.update_plot_mag()
        self.update_plot_iv()
        self.update_plot_vol_temp()

    def update_plot_mag(self):
        """Update magnetization plot."""
        try:
            self.clear_plot_mag()

            plots = self.get_selected_plots_mag()

            if len(plots) == 0:
                show_xlines = False
                return

            if len(plots) > 1:
                show_xlines = False
            else:
                show_xlines = True

            self.configure_plot_mag()

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

            if show_xlines:
                xmin = self.ui.sbd_xmin.value()
                xmax = self.ui.sbd_xmax.value()

                self.xmin_line = _pyqtgraph.InfiniteLine(
                    xmin, pen=(0, 0, 0), movable=True)
                self.ui.pw_graph_mag.addItem(self.xmin_line)
                self.xmin_line.sigPositionChangeFinished.connect(
                    self.update_xmin_spin_box)

                self.xmax_line = _pyqtgraph.InfiniteLine(
                    xmax, pen=(0, 0, 0), movable=True)
                self.ui.pw_graph_mag.addItem(self.xmax_line)
                self.xmax_line.sigPositionChangeFinished.connect(
                    self.update_xmax_spin_box)
            else:
                self.xmin_line = None
                self.xmax_line = None

        except Exception:
            _traceback.print_exc(file=_sys.stdout)
            return

    def update_plot_iv(self):
        try:
            self.clear_plot_iv()

            selected_idns = self.get_selected_plots_iv()
            if len(selected_idns) == 0:
                return

            self.configure_plot_iv(selected_idns)

            with _warnings.catch_warnings():
                _warnings.simplefilter("ignore")

                count = 0
                for m in self.measurement_list:
                    if m.idn in selected_idns:
                        iv1 = m.integrated_voltage_position_1
                        iv2 = m.integrated_voltage_position_2
                        
                        if self.ui.chb_avg.isChecked():
                            self.graph_iv_1[count][0].setData(
                                _np.mean(iv1, axis=1))
                            
                            self.graph_iv_2[count][0].setData(
                                _np.mean(iv2, axis=1))
                        else:
                            for j in range(iv1.shape[1]):
                                self.graph_iv_1[count][j].setData(
                                    iv1[:, j])

                            for j in range(iv2.shape[1]):
                                self.graph_iv_2[count][j].setData(
                                    iv2[:, j])
                        
                        count += 1

        except Exception:
            _traceback.print_exc(file=_sys.stdout)
            return

    def update_plot_vol_temp(self):
        try:
            self.clear_plot_vol_temp()
            self.configure_plot_vol_temp()

            with _warnings.catch_warnings():
                _warnings.simplefilter("ignore")
                x = self.measurement_idns
                self.graph_vol.setData(x, self.volume_list)
                self.graph_temp.setData(x, self.temperature_list)

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
