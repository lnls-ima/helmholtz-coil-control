# -*- coding: utf-8 -*-

"""Measurement widget for the control application."""

import sys as _sys
import traceback as _traceback
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

    def clear_table(self):
        """Clear values table."""
        self.disable_led()
        self.ui.tbl_values.clearContents()
        self.ui.tbl_values.setRowCount(0)

    def disable_led(self):
        """Disbale led."""
        self.ui.la_updated_led.setEnabled(False)

    def connect_signal_slots(self):
        """Create signal/slot connections."""
        self.ui.cmb_parameter.currentIndexChanged.connect(self.disable_led)
        self.ui.tbl_values.itemSelectionChanged.connect(self.disable_led)
        self.ui.pbt_add_row.clicked.connect(self.add_row)
        self.ui.pbt_remove_row.clicked.connect(self.remove_row)
        self.ui.pbt_clear_table.clicked.connect(self.clear_table)
        self.ui.pbt_update_scan_config.clicked.connect(self.update_scan_config)

    def update_scan_config(self):
        """Update scan parameter and values."""
        try:
            cmb_text = self.ui.cmb_parameter.currentText().lower()

            text_list = []
            nrows = self.ui.tbl_values.rowCount()
            for i in range(nrows):
                item = self.ui.tbl_values.item(i, 0)
                if item is not None:
                    text_list.append(item.text())

            parameter = None
            values = []
            if cmb_text == 'trigger':
                parameter = 'integration_trigger'
                values = [int(t) for t in text_list]
            elif cmb_text in ('integration points', 'pontos de integração'):
                parameter = 'integration_points'
                values = [int(t) for t in text_list]
            elif cmb_text in ('number of turns', 'número de voltas'):
                parameter = 'integration_nr_turns'
                values = [int(t) for t in text_list]
            elif cmb_text in ('maximum velocity', 'velocidade máxima'):
                parameter = 'motor_velocity'
                values = [float(t) for t in text_list]
            elif cmb_text in ('acceleration', 'aceleração'):
                parameter = 'motor_acceleration'
                values = [float(t) for t in text_list]

            self.scan_parameter = parameter
            self.scan_values = values
            self.scan_count = 0

            if self.valid_scan:
                self.ui.la_updated_led.setEnabled(True)

        except Exception:
            _traceback.print_exc(file=_sys.stdout)