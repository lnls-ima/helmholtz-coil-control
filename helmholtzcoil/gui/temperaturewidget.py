# -*- coding: utf-8 -*-

"""Temperature widget for the control application."""

import sys as _sys
import numpy as _np
import time as _time
import traceback as _traceback
from qtpy.QtWidgets import (
    QApplication as _QApplication,
    QMessageBox as _QMessageBox,
    QPushButton as _QPushButton,
    QLabel as _QLabel,
    QDoubleSpinBox as _QDoubleSpinBox,
    )
from qtpy.QtCore import (
    Qt as _Qt,
    QThread as _QThread,
    QObject as _QObject,
    Signal as _Signal,
    )

from helmholtzcoil.gui.auxiliarywidgets import (
    TablePlotWidget as _TablePlotWidget
    )
from helmholtzcoil.devices import (
    multimeter as _multimeter,
    )


class TemperatureWidget(_TablePlotWidget):
    """Temperature class for the control application."""

    _left_axis_1_label = 'Temperature [degC]'
    _left_axis_1_format = '{0:.4f}'
    _left_axis_1_data_labels = ['Temperature [degC]']
    _left_axis_1_data_colors = [(255, 0, 0)]

    def __init__(self, parent=None):
        """Set up the ui and signal/slot connections."""
        super().__init__(parent)

        # add check box and configure button
        self.la_resistance = _QLabel('Cable Resistance [Ohms]')
        self.sbd_resistance = _QDoubleSpinBox()
        self.sbd_resistance.setDecimals(4)
        self.sbd_resistance.setValue(0.8202)
        self.pbt_configure = _QPushButton('Configure Device')
        self.pbt_configure.clicked.connect(self.configure_devices)
        self.add_widgets_next_to_table(
            [[self.la_resistance, self.sbd_resistance],
            [self.pbt_configure]])

        # Create reading thread
        self.wthread = _QThread()
        self.worker = ReadValueWorker()
        self.worker.moveToThread(self.wthread)
        self.wthread.started.connect(self.worker.run)
        self.worker.finished.connect(self.wthread.quit)
        self.worker.finished.connect(self.get_reading)

    def check_connection(self, monitor=False):
        """Check devices connection."""
        if not _multimeter.connected:
            if not monitor:
                _QMessageBox.critical(
                    self,
                    'Failure',
                    'Multimeter not connected.',
                    _QMessageBox.Ok)
            return False
        return True

    def closeEvent(self, event):
        """Close widget."""
        try:
            self.wthread.quit()
            super().closeEvent(event)
        except Exception:
            _traceback.print_exc(file=_sys.stdout)
            event.accept()

    def configure_devices(self):
        """Configure device."""
        if not self.check_connection():
            return

        try:
            self.blockSignals(True)
            _QApplication.setOverrideCursor(_Qt.WaitCursor)

            _multimeter.send_command('CONF:RES 100,0.0001')

            self.blockSignals(False)
            _QApplication.restoreOverrideCursor()

        except Exception:
            self.blockSignals(False)
            _QApplication.restoreOverrideCursor()
            _traceback.print_exc(file=_sys.stdout)

    def get_reading(self):
        """Get reading from worker thread."""
        try:
            ts = self.worker.timestamp
            r = self.worker.reading

            if ts is None:
                return

            if len(r) == 0 or all([_np.isnan(ri) for ri in r]):
                return

            self._timestamp.append(ts)
            for i, label in enumerate(self._data_labels):
                self._readings[label].append(r[i])
            self.add_last_value_to_table()
            self.update_plot()

        except Exception:
            _traceback.print_exc(file=_sys.stdout)

    def read_value(self, monitor=False):
        """Read value."""
        if len(self._data_labels) == 0:
            return

        if not self.check_connection(monitor=monitor):
            return

        try:
            self.worker.cable_resistance = self.sbd_resistance.value()
            self.wthread.start()

        except Exception:
            _traceback.print_exc(file=_sys.stdout)


class ReadValueWorker(_QObject):
    """Read values worker."""

    finished = _Signal([bool])

    def __init__(self):
        """Initialize object."""
        self.cable_resistance = None
        self.timestamp = None
        self.reading = []
        super().__init__()

    def run(self):
        """Read values from devices."""
        try:
            self.timestamp = None
            self.reading = []

            ts = _time.time()

            if self.dcct_enabled:
                reading = _multimeter.read_current()
            else:
                reading = _np.nan

            temperature = (reading - 100)/self.cable_resistance

            self.timestamp = ts
            self.reading.append(temperature)
            self.finished.emit(True)

        except Exception:
            _traceback.print_exc(file=_sys.stdout)
            self.timestamp = None
            self.reading = []
            self.finished.emit(True)
