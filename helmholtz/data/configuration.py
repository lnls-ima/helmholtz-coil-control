# -*- coding: utf-8 -*-

"""Implementation of classes to handle configuration data."""

import sys as _sys
import numpy as _np
import json as _json
import traceback as _traceback
import collections as _collections

from imautils.db import database as _database


class ConnectionConfig(_database.DatabaseAndFileDocument):
    """Read, write and stored connection configuration data."""

    label = 'Connection'
    collection_name = 'connection'
    db_dict = _collections.OrderedDict([
        ('idn', {'field': 'id', 'dtype': int, 'not_null': True}),
        ('date', {'field': 'date', 'dtype': str, 'not_null': True}),
        ('hour', {'field': 'hour', 'dtype': str, 'not_null': True}),
        ('display_enable',
            {'field': 'display_enable', 'dtype': int, 'not_null': True}),
        ('display_port',
            {'field': 'display_port', 'dtype': str, 'not_null': True}),
        ('display_baudrate',
            {'field': 'display_baudrate', 'dtype': int, 'not_null': True}),
        ('display_bytesize',
            {'field': 'display_bytesize', 'dtype': int, 'not_null': True}),
        ('display_parity',
            {'field': 'display_parity', 'dtype': str, 'not_null': True}),
        ('display_stopbits',
            {'field': 'display_stopbits', 'dtype': str, 'not_null': True}),
        ('driver_enable',
            {'field': 'driver_enable', 'dtype': int, 'not_null': True}),
        ('driver_port',
            {'field': 'driver_port', 'dtype': str, 'not_null': True}),
        ('driver_baudrate',
            {'field': 'driver_baudrate', 'dtype': int, 'not_null': True}),
        ('driver_bytesize',
            {'field': 'driver_bytesize', 'dtype': int, 'not_null': True}),
        ('driver_parity',
            {'field': 'driver_parity', 'dtype': str, 'not_null': True}),
        ('driver_stopbits',
            {'field': 'driver_stopbits', 'dtype': str, 'not_null': True}),
        ('multimeter_enable',
            {'field': 'multimeter_enable', 'dtype': int, 'not_null': True}),
        ('multimeter_port',
            {'field': 'multimeter_port', 'dtype': str, 'not_null': True}),
        ('multimeter_baudrate',
            {'field': 'multimeter_baudrate', 'dtype': int, 'not_null': True}),
        ('multimeter_bytesize',
            {'field': 'multimeter_bytesize', 'dtype': int, 'not_null': True}),
        ('multimeter_parity',
            {'field': 'multimeter_parity', 'dtype': str, 'not_null': True}),
        ('multimeter_stopbits', {
            'field': 'multimeter_stopbits', 'dtype': str, 'not_null': True}),
        ('integrator_enable',
            {'field': 'integrator_enable', 'dtype': int, 'not_null': True}),
        ('integrator_address',
            {'field': 'integrator_address', 'dtype': int, 'not_null': True}),
        ('integrator_board',
            {'field': 'integrator_board', 'dtype': int, 'not_null': True}),
    ])


class CoilConfig(_database.DatabaseAndFileDocument):
    """Read, write and stored coil configuration data."""

    label = 'Coil'
    collection_name = 'coil'
    db_dict = _collections.OrderedDict([
        ('idn', {'field': 'id', 'dtype': int, 'not_null': True}),
        ('date', {'field': 'date', 'dtype': str, 'not_null': True}),
        ('hour', {'field': 'hour', 'dtype': str, 'not_null': True}),
        ('radius_1',
            {'field': 'radius_1', 'dtype': float, 'not_null': True}),
        ('radius_2',
            {'field': 'radius_2', 'dtype': float, 'not_null': True}),
        ('center_distance',
            {'field': 'center_distance', 'dtype': float, 'not_null': True}),
        ('nr_turns',
            {'field': 'nr_turns', 'dtype': int, 'not_null': True}),
    ])


class MotorIntegratorConfig(_database.DatabaseAndFileDocument):
    """Read, write and stored motor and integrator configuration data."""

    label = 'Motor_Integrator'
    collection_name = 'motor_integrator'
    db_dict = _collections.OrderedDict([
        ('idn', {'field': 'id', 'dtype': int, 'not_null': True}),
        ('date', {'field': 'date', 'dtype': str, 'not_null': True}),
        ('hour', {'field': 'hour', 'dtype': str, 'not_null': True}),
        ('driver_address',
            {'field': 'driver_address', 'dtype': int, 'not_null': True}),
        ('motor_velocity',
            {'field': 'motor_velocity', 'dtype': float, 'not_null': True}),
        ('motor_acceleration',
            {'field': 'motor_acceleration', 'dtype': float, 'not_null': True}),
        ('motor_direction',
            {'field': 'motor_direction', 'dtype': str, 'not_null': True}),
        ('motor_resolution',
            {'field': 'motor_resolution', 'dtype': int, 'not_null': True}),
        ('integrator_channel',
            {'field': 'integrator_channel', 'dtype': str, 'not_null': True}),
        ('encoder_direction',
            {'field': 'encoder_direction', 'dtype': str, 'not_null': True}),
        ('encoder_resolution',
            {'field': 'encoder_resolution', 'dtype': int, 'not_null': True}),
    ])


class MeasurementConfig(_database.DatabaseAndFileDocument):
    """Read, write and stored measurement configuration data."""

    label = 'Configuration'
    collection_name = 'configuration'
    db_dict = _collections.OrderedDict([
        ('idn', {'field': 'id', 'dtype': int, 'not_null': True}),
        ('date', {'field': 'date', 'dtype': str, 'not_null': True}),
        ('hour', {'field': 'hour', 'dtype': str, 'not_null': True}),
        ('block_name',
            {'field': 'block_name', 'dtype': str, 'not_null': True}),
        ('main_component',
            {'field': 'main_component', 'dtype': str, 'not_null': True}),
        ('temperature',
            {'field': 'temperature', 'dtype': float, 'not_null': True}),
        ('volume_input',
            {'field': 'volume_input', 'dtype': str, 'not_null': True}),
        ('volume',
            {'field': 'volume', 'dtype': float, 'not_null': True}),
        ('dimension1',
            {'field': 'dimension1', 'dtype': float, 'not_null': True}),
        ('dimension2',
            {'field': 'dimension2', 'dtype': float, 'not_null': True}),
        ('dimension3',
            {'field': 'dimension3', 'dtype': float, 'not_null': True}),
        ('mass',
            {'field': 'mass', 'dtype': float, 'not_null': True}),
        ('density',
            {'field': 'density', 'dtype': float, 'not_null': True}),
        ('main_gain',
            {'field': 'main_gain', 'dtype': int, 'not_null': True}),
        ('residual_gain',
            {'field': 'residual_gain', 'dtype': int, 'not_null': True}),
        ('trigger',
            {'field': 'trigger', 'dtype': int, 'not_null': True}),
        ('integration_points',
            {'field': 'integration_points', 'dtype': int, 'not_null': True}),
        ('nr_turns',
            {'field': 'nr_turns', 'dtype': int, 'not_null': True}),
    ])
