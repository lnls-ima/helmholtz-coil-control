# -*- coding: utf-8 -*-

"""Implementation of classes to handle configuration data."""

import collections as _collections

from imautils.db import database as _database


class ConnectionConfig(_database.DatabaseAndFileDocument):
    """Read, write and stored connection configuration data."""

    label = 'Connection'
    collection_name = 'connection'
    db_dict = _collections.OrderedDict([
        ('idn', {'field': 'id', 'dtype': int, 'not_null': True}),
        ('date', {'dtype': str, 'not_null': True}),
        ('hour', {'dtype': str, 'not_null': True}),
        ('display_enable', {'dtype': int, 'not_null': True}),
        ('display_port', {'dtype': str}),
        ('display_baudrate', {'dtype': int, 'not_null': True}),
        ('display_bytesize', {'dtype': int, 'not_null': True}),
        ('display_parity', {'dtype': str, 'not_null': True}),
        ('display_stopbits', {'dtype': str, 'not_null': True}),
        ('driver_enable', {'dtype': int, 'not_null': True}),
        ('driver_port', {'dtype': str}),
        ('driver_baudrate', {'dtype': int, 'not_null': True}),
        ('driver_bytesize', {'dtype': int, 'not_null': True}),
        ('driver_parity', {'dtype': str, 'not_null': True}),
        ('driver_stopbits', {'dtype': str, 'not_null': True}),
        ('multimeter_enable', {'dtype': int, 'not_null': True}),
        ('multimeter_port', {'dtype': str}),
        ('multimeter_baudrate', {'dtype': int, 'not_null': True}),
        ('multimeter_bytesize', {'dtype': int, 'not_null': True}),
        ('multimeter_parity', {'dtype': str, 'not_null': True}),
        ('multimeter_stopbits', {'dtype': str, 'not_null': True}),
        ('integrator_enable', {'dtype': int, 'not_null': True}),
        ('integrator_address', {'dtype': int, 'not_null': True}),
        ('integrator_board', {'dtype': int, 'not_null': True}),
        ('balance_enable', {'dtype': int, 'not_null': True}),
        ('balance_port', {'dtype': str}),
        ('balance_baudrate', {'dtype': int, 'not_null': True}),
        ('balance_bytesize', {'dtype': int, 'not_null': True}),
        ('balance_parity', {'dtype': str, 'not_null': True}),
        ('balance_stopbits', {'dtype': str, 'not_null': True}),
    ])


class AdvancedOptions(_database.DatabaseAndFileDocument):
    """Read, write and stored advanced options data."""

    label = 'Advanced_Options'
    collection_name = 'advanced_options'
    db_dict = _collections.OrderedDict([
        ('idn', {'field': 'id', 'dtype': int, 'not_null': True}),
        ('date', {'dtype': str, 'not_null': True}),
        ('hour', {'dtype': str, 'not_null': True}),
        ('motor_driver_address', {'dtype': int, 'not_null': True}),
        ('motor_velocity', {'dtype': float, 'not_null': True}),
        ('motor_acceleration', {'dtype': float, 'not_null': True}),
        ('motor_rotation_direction', {'dtype': str, 'not_null': True}),
        ('motor_resolution', {'dtype': int, 'not_null': True}),
        ('integrator_channel', {'dtype': str, 'not_null': True}),
        ('integrator_encoder_direction', {'dtype': str, 'not_null': True}),
        ('integrator_encoder_resolution', {'dtype': int, 'not_null': True}),
        ('integration_trigger', {'dtype': int, 'not_null': True}),
        ('integration_points', {'dtype': int, 'not_null': True}),
        ('integration_nr_turns', {'dtype': int, 'not_null': True}),
        ('coil_radius', {'dtype': float, 'not_null': True}),
        ('coil_distance_center', {'dtype': float, 'not_null': True}),
        ('coil_turns', {'dtype': int, 'not_null': True}),
        ('temperature_nr_readings', {'dtype': int, 'not_null': True}),
        ('temperature_reading_frequency', {'dtype': float, 'not_null': True}),
    ])


class MeasurementConfig(_database.DatabaseAndFileDocument):
    """Read, write and stored measurement configuration data."""

    label = 'Configuration'
    collection_name = 'configuration'
    db_dict = _collections.OrderedDict([
        ('idn', {'field': 'id', 'dtype': int, 'not_null': True}),
        ('date', {'dtype': str, 'not_null': True}),
        ('hour', {'dtype': str, 'not_null': True}),
        ('block_name', {'dtype': str, 'not_null': True}),
        ('comments', {'dtype': str}),
        ('block_temperature', {'dtype': float, 'not_null': True}),
        ('volume_input', {'dtype': str, 'not_null': True}),
        ('block_volume', {'dtype': float, 'not_null': True}),
        ('block_dimension1', {'dtype': float, 'not_null': True}),
        ('block_dimension2', {'dtype': float, 'not_null': True}),
        ('block_dimension3', {'dtype': float, 'not_null': True}),
        ('block_mass', {'dtype': float, 'not_null': True}),
        ('density', {'dtype': float, 'not_null': True}),
        ('gain_position_1', {'dtype': int, 'not_null': True}),
        ('gain_position_2', {'dtype': int, 'not_null': True}),
        ('gain_position_3', {'dtype': int}),
        ('measure_position_1', {'dtype': int}),
        ('measure_position_2', {'dtype': int}),
        ('measure_position_3', {'dtype': int}),
    ])
