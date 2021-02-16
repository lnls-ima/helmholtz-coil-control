# -*- coding: utf-8 -*-

"""Implementation of classes to handle measurement data."""

import collections as _collections
import numpy as _np

from imautils.db import database as _database


class MeasurementData(_database.DatabaseAndFileDocument):
    """Read, write and stored measurement data."""

    label = 'HelmholtzMeasurement'
    collection_name = 'helmholtz_measurement'
    db_dict = _collections.OrderedDict([
        ('idn', {'field': 'id', 'dtype': int, 'not_null': True}),
        ('date', {'dtype': str, 'not_null': True}),
        ('hour', {'dtype': str, 'not_null': True}),
        ('block_name', {'dtype': str, 'not_null': True}),
        ('comments', {'dtype': str}),
        ('advanced_options_id', {'dtype': int}),
        ('configuration_id', {'dtype': int}),
        ('mx_avg', {'dtype': float}),
        ('my_avg', {'dtype': float}),
        ('mz_avg', {'dtype': float}),
        ('mx_std', {'dtype': float}),
        ('my_std', {'dtype': float}),
        ('mz_std', {'dtype': float}),
        ('coil_radius', {'dtype': float}),
        ('coil_distance_center', {'dtype': float}),
        ('coil_turns', {'dtype': int}),
        ('block_volume', {'dtype': float}),
        ('block_temperature', {'dtype': float}),
        ('offset_position_1', {'dtype': float}),
        ('offset_position_2', {'dtype': float}),
        ('offset_position_3', {'dtype': float}),
        ('integrated_voltage_position_1', {'dtype': _np.ndarray}),
        ('integrated_voltage_position_2', {'dtype': _np.ndarray}),
        ('integrated_voltage_position_3', {'dtype': _np.ndarray}),
    ])

    @property
    def default_filename(self):
        """Return the default filename."""
        filename = super().default_filename

        if self.block_name is not None and len(self.block_name) != 0:
            filename = filename.replace(self.label, self.block_name)

        return filename

    @staticmethod
    def calc_magnetization(
            integrated_voltage, offset,
            coil_radius, coil_distance_center,
            coil_turns, block_volume):
        if len(integrated_voltage) == 0:
            return 0, 0, 0, 0

        ivoltage = _np.array(integrated_voltage)
        shape = ivoltage.shape
        if len(shape) == 1:
            ivoltage = _np.array([ivoltage]).transpose()

        npts = ivoltage.shape[0]
        mag_axis_list = []
        mag_perp_list = []
        for i in range(ivoltage.shape[1]):
            fft = _np.fft.fft(ivoltage[:, i])/(npts/2)
            a1 = fft[1].real
            b1 = fft[1].imag

            mu0 = 4*_np.pi*1e-7
            dtheta = 2*_np.pi/npts
            geometric_factor = (coil_turns/2)*(
                coil_radius**2)/(
                    (coil_radius**2 + coil_distance_center**2)**(3/2))
            s = _np.sin(dtheta)
            c = 1 - _np.cos(dtheta)

            moment_axis = (1/(mu0*geometric_factor))*(a1*s + b1*c)/(2*c)
            moment_perp = -(1/(mu0*geometric_factor))*(-b1*s + a1*c)/(2*c)

            mag_axis = mu0*moment_axis/block_volume
            mag_perp = mu0*moment_perp/block_volume

            mag_axis_list.append(mag_axis)
            mag_perp_list.append(mag_perp)

        mag_axis_avg = _np.mean(mag_axis_list)
        mag_perp_avg = _np.mean(mag_perp_list)

        mag_axis_std = _np.std(mag_axis_list)
        mag_perp_std = _np.std(mag_perp_list)

        return mag_axis_avg, mag_perp_avg, mag_axis_std, mag_perp_std

    def save_file(self, filename):
        """Save data to file.
        Args:
            filename (str): file fullpath.
        """
        if not self.valid_data():
            message = 'Invalid data.'
            raise ValueError(message)

        columns = [
            'integrated_voltage_position_1',
            'integrated_voltage_position_2',
            'integrated_voltage_position_3']
        return super().save_file(filename, columns=columns)

    def read_file(self, filename):
        """Read from file.

        Args:
        ----
            filename (str): filepath.

        """
        return super().read_file(filename, check_nr_columns=False)

    def set_magnetization_components(
            self,
            integrated_voltage_position_1,
            integrated_voltage_position_2,
            offset_position_1, offset_position_2,
            coil_radius, coil_distance_center, coil_turns,
            block_volume):
        self.integrated_voltage_position_1 = integrated_voltage_position_1
        self.integrated_voltage_position_2 = integrated_voltage_position_2
        self.integrated_voltage_position_3 = []
        self.offset_position_1 = offset_position_1
        self.offset_position_2 = offset_position_2
        self.offset_position_3 = 0
        self.coil_radius = coil_radius
        self.coil_distance_center = coil_distance_center
        self.coil_turns = coil_turns
        self.block_volume = block_volume

        mx1, my, mx1_std, my_std = self.calc_magnetization(
            self.integrated_voltage_position_1,
            self.offset_position_1,
            self.coil_radius,
            self.coil_distance_center,
            self.coil_turns,
            self.block_volume)

        mx2, mz, mx2_std, mz_std = self.calc_magnetization(
            self.integrated_voltage_position_2,
            self.offset_position_2,
            self.coil_radius,
            self.coil_distance_center,
            self.coil_turns,
            self.block_volume)

        mz = (-1)*mz

        npts1 = len(self.integrated_voltage_position_1)
        npts2 = len(self.integrated_voltage_position_2)
        npts3 = len(self.integrated_voltage_position_3)

        if npts1 != 0:
            shape = self.integrated_voltage_position_1.shape
        elif npts2 != 0:
            shape = self.integrated_voltage_position_2.shape
        else:
            shape = self.integrated_voltage_position_3.shape

        if npts1 == 0:
            self.integrated_voltage_position_1 = _np.zeros(shape)

        if npts2 == 0:
            self.integrated_voltage_position_2 = _np.zeros(shape)

        if npts3 == 0:
            self.integrated_voltage_position_3 = _np.zeros(shape)

        if mx1 == 0:
            mx = mx2
            mx_std = mx2_std
        elif mx2 == 0:
            mx = mx1
            mx_std = mx1_std
        elif _np.abs(my) >= _np.abs(mz):
            mx = mx1
            mx_std = mx1_std
        else:
            mx = mx2
            mx_std = mx2_std

        self.mx_avg = mx
        self.my_avg = my
        self.mz_avg = mz

        self.mx_std = mx_std
        self.my_std = my_std
        self.mz_std = mz_std

        m = [self.mx_avg, self.my_avg, self.mz_avg]
        mstd = [self.mx_std, self.my_std, self.mz_std]

        return m, mstd
