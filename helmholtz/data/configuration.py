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
        ('block_temperature',
            {'field': 'block_temperature', 'dtype': float, 'not_null': True}),
        ('volume_input',
            {'field': 'volume_input', 'dtype': str, 'not_null': True}),
        ('block_volume',
            {'field': 'block_volume', 'dtype': float, 'not_null': True}),
        ('block_dimension1',
            {'field': 'block_dimension1', 'dtype': float, 'not_null': True}),
        ('block_dimension2',
            {'field': 'block_dimension2', 'dtype': float, 'not_null': True}),
        ('block_dimension3',
            {'field': 'block_dimension3', 'dtype': float, 'not_null': True}),
        ('block_mass',
            {'field': 'block_mass', 'dtype': float, 'not_null': True}),
        ('density',
            {'field': 'density', 'dtype': float, 'not_null': True}),
        ('main_component_gain',
            {'field': 'main_component_gain', 'dtype': int, 'not_null': True}),
        ('residual_component_gain',
            {'field': 'residual_component_gain', 'dtype': int, 'not_null': True}),
        ('trigger',
            {'field': 'trigger', 'dtype': int, 'not_null': True}),
        ('integration_points',
            {'field': 'integration_points', 'dtype': int, 'not_null': True}),
        ('nr_turns',
            {'field': 'nr_turns', 'dtype': int, 'not_null': True}),
        ('coil_radius',
            {'field': 'coil_radius', 'dtype': float, 'not_null': True}),
        ('coil_distance_center',
            {'field': 'coil_distance_center', 'dtype': float, 'not_null': True}),
        ('coil_turns',
            {'field': 'coil_turns', 'dtype': int, 'not_null': True}),
    ])
