# -*- coding: utf-8 -*-

"""Measurement widget for the control application."""

import sys as _sys
import traceback as _traceback
import numpy as _np
from qtpy.QtWidgets import (
    QDialog as _QDialog,
    )
import qtpy.uic as _uic

from helmholtz.gui import utils as _utils


class ScanParameterDialog(_QDialog):
    """Scan parameter dialog for the control application."""

    def __init__(self, parent=None):
        """Set up the ui."""
        super().__init__(parent)
        uifile = _utils.get_ui_file(self)
        self.ui = _uic.loadUi(uifile, self)
        self.connect_signal_slots()
        self.scan_parameter = None
        self.scan_values = []
        self.scan_count = 0

    @property
    def valid_scan(self):
        """Return True if the scan configuration is valid, False otherwise."""
        if self.scan_parameter is None:
            return False

        if len(self.scan_values) == 0:
            return False

        return True

    def clear(self):
        """Clear."""
        self.scan_parameter = None
        self.scan_values = []
        self.scan_count = 0
        self.ui.cmb_parameter.setCurrentIndex(-1)
        self.ui.tbl_values.clearContents()
        self.ui.tbl_values.setRowCount(0)
        self.ui.la_updated_led.setEnabled(False)
        self.ui.sbd_start.setValue(0)
        self.ui.sbd_end.setValue(0)
        self.ui.sbd_step.setValue(0)
        self.ui.le_nr_points.setText('')

    def add_row(self):
        """Add row to values table."""
        self.disable_led()
        idx = self.ui.tbl_values.currentRow()
        if idx == -1:
            self.ui.tbl_values.insertRow(0)
        else:
            self.ui.tbl_values.insertRow(idx)

    def remove_row(self):
        """Remove row from values table."""
        self.disable_led()
        idx = self.ui.tbl_values.currentRow()
        self.ui.tbl_values.removeRow(idx)

    def disable_led(self):
        """Disbale led."""
        self.ui.la_updated_led.setEnabled(False)

    def connect_signal_slots(self):
        """Create signal/slot connections."""
        self.ui.cmb_parameter.currentIndexChanged.connect(self.disable_led)
        self.ui.tbl_values.itemSelectionChanged.connect(self.disable_led)
        self.ui.pbt_add_row.clicked.connect(self.add_row)
        self.ui.pbt_remove_row.clicked.connect(self.remove_row)
        self.ui.pbt_clear_table.clicked.connect(self.clear)
        self.ui.pbt_update_scan_config.clicked.connect(self.update_scan_config)
        self.ui.rbt_table.toggled.connect(self.update_page)
        self.ui.rbt_step.toggled.connect(self.update_page)
        self.ui.sbd_start.editingFinished.connect(self.update_step_values)
        self.ui.sbd_end.editingFinished.connect(self.update_step_values)
        self.ui.sbd_step.editingFinished.connect(self.update_step_values)

    def update_step_values(self):
        start = self.ui.sbd_start.value()
        end = self.ui.sbd_end.value()
        step = self.ui.sbd_step.value()
        if (end - start) > 0 and step != 0:
            npts = round((end - start)/step)
            end_corr = start + npts*step
            self.ui.sbd_end.setValue(end_corr)
            self.ui.le_nr_points.setText(str(npts+1))
        else:
            self.ui.le_nr_points.setText('')

    def update_page(self):
        if self.ui.rbt_table.isChecked():
            self.ui.stw_values.setCurrentWidget(self.ui.pg_table)
        else:
            self.ui.stw_values.setCurrentWidget(self.ui.pg_step)

    def update_scan_config(self):
        """Update scan parameter and values."""
        try:
            self.scan_parameter = None
            self.scan_values = []
            self.scan_count = 0

            cmb_text = self.ui.cmb_parameter.currentText().lower()

            parameter = None
            if cmb_text == 'trigger':
                parameter = 'integration_trigger'
            elif cmb_text in ('integration points', 'pontos de integração'):
                parameter = 'integration_points'
            elif cmb_text in ('number of turns', 'número de voltas'):
                parameter = 'integration_nr_turns'
            elif cmb_text in ('maximum velocity', 'velocidade máxima'):
                parameter = 'motor_velocity'
            elif cmb_text in ('acceleration', 'aceleração'):
                parameter = 'motor_acceleration'

            self.scan_parameter = parameter

            if self.ui.rbt_table.isChecked():
                text_list = []
                nrows = self.ui.tbl_values.rowCount()
                for i in range(nrows):
                    item = self.ui.tbl_values.item(i, 0)
                    if item is not None:
                        text_list.append(item.text())

                values = []
                if cmb_text == 'trigger':
                    values = [int(t) for t in text_list]
                elif cmb_text in ('integration points', 'pontos de integração'):
                    values = [int(t) for t in text_list]
                elif cmb_text in ('number of turns', 'número de voltas'):
                    values = [int(t) for t in text_list]
                elif cmb_text in ('maximum velocity', 'velocidade máxima'):
                    values = [float(t) for t in text_list]
                elif cmb_text in ('acceleration', 'aceleração'):
                    values = [float(t) for t in text_list]

                self.scan_values = values
                self.scan_count = 0
            
            else:
                start = self.ui.sbd_start.value()
                end = self.ui.sbd_end.value()
                step = self.ui.sbd_step.value()
                npts = round((end - start)/step)
                self.scan_values = _np.linspace(start, end, npts+1)
                self.scan_count = 0

            if self.valid_scan:
                self.ui.la_updated_led.setEnabled(True)

        except Exception:
            _traceback.print_exc(file=_sys.stdout)
