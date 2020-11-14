"""Sub-package for hall bench devices."""

import os as _os
import time as _time

from imautils.devices.utils import configure_logging
from imautils.devices import HeidenhainLib as _HeidenhainLib
from imautils.devices import ParkerDriverLib as _ParkerDriverLib
from imautils.devices import Agilent34401ALib as _Agilent34401ALib
from imautils.devices import PDI5150Lib as _PDI5150Lib


class Integrator(_PDI5150Lib.PDI5150GPIB):

    def configure_measurement(
            self, channel, encoder_resolution, direction,
            start_trigger, nr_intervals,
            interval_size, gain, wait=0.1):
        if not self.connected:
            return False

        # Parar todas as coletas e preparar integrador
        self.send_command(self.commands.stop_measurement)
        _time.sleep(wait)

        # Configurar canal a ser utilizado
        self.send_command(self.commands.channel + channel)
        _time.sleep(wait)

        # Configura trigger
        self.config_encoder_trigger(
            encoder_resolution, direction,
            start_trigger, nr_intervals,
            interval_size, wait=wait)

        # Configurar para leitura imediata
        self.send_command(self.commands.immediate_reading)
        _time.sleep(wait)

        # Preparar para armazenamento
        self.send_command(self.commands.cumulative)
        _time.sleep(wait)

        # Configurar End of Data
        self.send_command(self.commands.end_of_data)
        _time.sleep(wait)

        # Configura ganho
        cmd = self.commands.gain + str(gain)
        self.send_command(cmd)
        _time.sleep(wait)
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
integrator = Integrator(log=True)
