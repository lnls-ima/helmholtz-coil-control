# -*- coding: utf-8 -*-

"""Implementation of classes to handle measurement data."""

import sys as _sys
import numpy as _np
import json as _json
import traceback as _traceback
import collections as _collections

from imautils.db import database as _database


class MeasurementData(_database.DatabaseAndFileDocument):
    """Read, write and stored measurement data."""

    label = 'Measurement'
    collection_name = 'measurement'
    db_dict = _collections.OrderedDict([
        ('idn', {'field': 'id', 'dtype': int, 'not_null': True}),
        ('date', {'field': 'date', 'dtype': str, 'not_null': True}),
        ('hour', {'field': 'hour', 'dtype': str, 'not_null': True}),
        ('block_name',
            {'field': 'block_name', 'dtype': str, 'not_null': True}),
        ('main_component',
            {'field': 'main_component', 'dtype': str, 'not_null': True}),
        ('block_temperature',
            {'field': 'block_temperature', 'dtype': float, 'not_null': True}),
        ('block_volume',
            {'field': 'block_volume', 'dtype': float, 'not_null': True}),
        ('motor_integrator_id',
            {'field': 'motor_integrator_id', 'dtype': int}),
        ('offset_id', {'field': 'offset_id', 'dtype': int}),
        ('configuration_id',
            {'field': 'configuration_id', 'dtype': int}),
        ('mx_avg', {'field': 'mx_avg', 'dtype': float}),
        ('my_avg', {'field': 'my_avg', 'dtype': float}),
        ('mz_avg', {'field': 'mz_avg', 'dtype': float}),
        ('mx_std', {'field': 'mx_std', 'dtype': float}),
        ('my_std', {'field': 'my_std', 'dtype': float}),
        ('mz_std', {'field': 'mz_std', 'dtype': float}),
        ('integrated_voltage',
            {'field': 'integrated_voltage', 'dtype': str}),
    ])

    @staticmethod
    def calc_magnetization(
            integrated_voltage, offset, coil_turns,
            radius, dist_center, block_volume):
        ivoltage = _np.array(integrated_voltage)
        shape = ivoltage.shape
        if len(shape) == 1:
            ivoltage = _np.array([ivoltage]).transpose()

        npts = ivoltage.shape[0]
        mag_axis_list = []
        mag_perp_list = []
        for i in range(ivoltage.shape[1]):
            fft = _np.fft.fft(ivoltage - offset)/npts/2
            a1 = fft[1].real
            b1 = fft[1].imag

            mu0 = 4*_np.pi*1e-7
            dtheta = 2*_np.pi/npts
            geometric_factor = coil_turns*(
                radius**2)/(radius**2 + dist_center**2)**(3/2)
            s = _np.sin(dtheta)
            c = 1 - _np.cos(dtheta)

            moment_axis = (1/mu0/geometric_factor)*(a1*s + b1*c)/2*c
            moment_perp = (1/mu0/geometric_factor)*(-b1*s + a1*c)/2*c

            mag_axis = moment_axis/block_volume
            mag_perp = moment_perp/block_volume

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
            integrated_voltage_step1, integrated_voltage_step2,
            offset_step1, offset_step2,
            coil_turns, radius, dist_center, block_volume):
        mx1, my, mx1_std, my_std = cls.calc_magnetization(
            integrated_voltage_step1, offset_step1,
            coil_turns, radius,
            dist_center, block_volume)

        mz, mx2, mz_std, mx2_std = cls.calc_magnetization(
            integrated_voltage_step2, offset_step2,
            coil_turns, radius,
            dist_center, block_volume)

        if main_component.lower() == 'y':
            m = [mx2, my, mz]
            mstd = [mx2_std, my_std, mz_std]
        elif main_component.lower() in ('x', 'z'):
            m = [mx1, my, mz]
            mstd = [mx1_std, my_std, mz_std]

        return m, mstd

