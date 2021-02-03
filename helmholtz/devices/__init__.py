"""Sub-package for hall bench devices."""

import os as _os
import time as _time

from imautils.devices.utils import configure_logging
from imautils.devices import HeidenhainLib as _HeidenhainLib
from imautils.devices import ParkerDriverLib as _ParkerDriverLib
from imautils.devices import Agilent34401ALib as _Agilent34401ALib
from imautils.devices import PDI5150Lib as _PDI5150Lib
from imautils.devices import FDI2056Lib as _FDI2056Lib


class PDIIntegrator(_PDI5150Lib.PDI5150GPIB):

    def configure_measurement(
            self, channel, encoder_resolution, direction,
            start_trigger, integration_points, nr_turns,
            gain, wait=0.1):
        if not self.connected:
            return False

        nr_intervals = int(integration_points * nr_turns)
        interval_size = int(encoder_resolution / integration_points)

        # Parar todas as coletas e preparar integrador
        self.send_command(self.commands.stop)
        _time.sleep(wait)

        r = 'A'
        while 'A' in r:
            r = self.read_from_device()

        # Configurar canal a ser utilizado
        self.send_command(self.commands.channel + channel)
        _time.sleep(wait)

        # Configura ganho
        cmd = self.commands.gain + str(gain)
        self.send_command(cmd)
        _time.sleep(wait)

        # Configurar para leitura imediata
        self.send_command(self.commands.immediate_reading)
        _time.sleep(wait)

        # Preparar para armazenamento
        self.send_command(self.commands.cumulative)
        _time.sleep(wait)

        # Configurar End of Data
        self.send_command(self.commands.end_of_data)
        _time.sleep(wait)

        # Configura trigger
        self.configure_trig_encoder(
            encoder_resolution, direction,
            start_trigger, nr_intervals,
            interval_size, wait=wait)

        self.send_command(self.commands.stop)
        _time.sleep(wait)

        return True

    def start_measurement(self, wait=0.1):
        self.send_command(self.commands.stop)
        _time.sleep(wait)

        self.send_command(self.commands.start)
        _time.sleep(wait)

        reading = self.read_from_device()
        if reading == '\x1a':
            return False

        return True


class FDIIntegrator(_FDI2056Lib.FDI2056Ethernet):

    def configure_measurement(
            self, channel, encoder_resolution, direction,
            start_trigger, integration_points, nr_turns,
            gain):
        if not self.connected:
            return False

        if channel != 'A':
            return False

        self.configure_gain(gain)

        self.configure_trig_encoder(
            encoder_resolution, direction,
            start_trigger, integration_points, nr_turns)

        return True


_timestamp = _time.strftime('%Y-%m-%d_%H-%M-%S', _time.localtime())

_logs_path = _os.path.join(
    _os.path.dirname(_os.path.dirname(
        _os.path.dirname(
            _os.path.abspath(__file__)))), 'logs')

if not _os.path.isdir(_logs_path):
    _os.mkdir(_logs_path)

logfile = _os.path.join(
    _logs_path, '{0:s}_helmholtz_coil.log'.format(_timestamp))
configure_logging(logfile)

display = _HeidenhainLib.HeidenhainSerial(log=True)
driver = _ParkerDriverLib.ParkerDriverSerial(log=True)
multimeter = _Agilent34401ALib.Agilent34401ASerial(log=True)
integrator = FDIIntegrator(log=True)
