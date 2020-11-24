# -*- coding: utf-8 -*-

"""Implementation of classes to handle measurement data."""

import collections as _collections
import numpy as _np

from imautils.db import database as _database


class MeasurementData(_database.DatabaseAndFileDocument):
    """Read, write and stored measurement data."""

    label = 'Measurement'
    collection_name = 'measurement'
    db_dict = _collections.OrderedDict([
        ('idn', {'field': 'id', 'dtype': int, 'not_null': True}),
        ('date', {'dtype': str, 'not_null': True}),
        ('hour', {'dtype': str, 'not_null': True}),
        ('block_name', {'dtype': str, 'not_null': True}),
        ('main_component', {'dtype': str, 'not_null': True}),
        ('block_temperature', {'dtype': float, 'not_null': True}),
        ('block_volume', {'dtype': float, 'not_null': True}),
        ('motor_integrator_id', {'dtype': int}),
        ('offset_id', {'dtype': int}),
        ('configuration_id', {'dtype': int}),
        ('mx_avg', {'dtype': float}),
        ('my_avg', {'dtype': float}),
        ('mz_avg', {'dtype': float}),
        ('mx_std', {'dtype': float}),
        ('my_std', {'dtype': float}),
        ('mz_std', {'dtype': float}),
        ('integrated_voltage', {'dtype': str}),
    ])

    @staticmethod
    def calc_magnetization(
            integrated_voltage, offset, coil_turns,
            radius, dist_center, block_volume):
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
            geometric_factor = coil_turns*(
                radius**2)/((radius**2 + dist_center**2)**(3/2))
            s = _np.sin(dtheta)
            c = 1 - _np.cos(dtheta)

            moment_axis = (1/(mu0*geometric_factor))*(a1*s + b1*c)/(2*c)
            moment_perp = (1/(mu0*geometric_factor))*(-b1*s + a1*c)/(2*c)

            mag_axis = mu0*moment_axis/block_volume
            mag_perp = mu0*moment_perp/block_volume

            mag_axis_list.append(mag_axis)
            mag_perp_list.append(mag_perp)

        mag_axis_avg = _np.mean(mag_axis_list)
        mag_perp_avg = _np.mean(mag_perp_list)

        mag_axis_std = _np.std(mag_axis_list)
        mag_perp_std = _np.std(mag_perp_list)

        return mag_axis_avg, mag_perp_avg, mag_axis_std, mag_perp_std

    @classmethod
    def get_magnetization_components(
            cls, main_component,
            integrated_voltage_position_1, integrated_voltage_position_2,
            offset_position_1, offset_position_2,
            coil_turns, radius, dist_center, block_volume):
        mx1, my, mx1_std, my_std = cls.calc_magnetization(
            integrated_voltage_position_1, offset_position_1,
            coil_turns, radius,
            dist_center, block_volume)

        mz, mx2, mz_std, mx2_std = cls.calc_magnetization(
            integrated_voltage_position_2, offset_position_2,
            coil_turns, radius,
            dist_center, block_volume)

        if mx1 == 0:
            mx = mx2
            mx_std = mx2_std
        elif mx2 == 0:
            mx = mx1
            mx_std = mx1_std
        elif main_component.lower() == 'vertical':
            mx = mx2
            mx_std = mx2_std
        else:
            mx = mx1
            mx_std = mx1_std

        m = [mx, my, mz]
        mstd = [mx_std, my_std, mz_std]

        return m, mstd
