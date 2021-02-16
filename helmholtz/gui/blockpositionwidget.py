# -*- coding: utf-8 -*-

"""Block position widget for the control application."""

from qtpy.QtWidgets import QWidget as _QWidget
import qtpy.uic as _uic

from helmholtz.gui import utils as _utils


class BlockPositionWidget(_QWidget):
    """Block position widget class for the control application."""

    def __init__(self, parent=None):
        """Set up the ui."""
        super().__init__(parent)
        uifile = _utils.get_ui_file(self)
        self.ui = _uic.loadUi(uifile, self)