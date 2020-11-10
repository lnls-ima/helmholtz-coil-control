# -*- coding: utf-8 -*-

"""Run the control application."""

from helmholtzcoil.gui import mainapp


THREAD = False


if THREAD:
    thread = mainapp.run_in_thread()
else:
    mainapp.run()
