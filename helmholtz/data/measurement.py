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
        ('temperature',
            {'field': 'temperature', 'dtype': float, 'not_null': True}),
        ('volume',
            {'field': 'volume', 'dtype': float, 'not_null': True}),
        ('coil_config', {'field': 'coil_config', 'dtype': int}),
        ('motor_integrator_config',
            {'field': 'motor_integrator_config', 'dtype': int}),
        ('offset_config', {'field': 'offset_config', 'dtype': int}),
        ('measurement_config',
            {'field': 'measurement_config', 'dtype': int}),
        ('mx_avg', {'field': 'mx_avg', 'dtype': float}),
        ('my_avg', {'field': 'my_avg', 'dtype': float}),
        ('mz_avg', {'field': 'mz_avg', 'dtype': float}),
        ('mx_std', {'field': 'mx_std', 'dtype': float}),
        ('my_std', {'field': 'my_std', 'dtype': float}),
        ('mz_std', {'field': 'mz_std', 'dtype': float}),
        ('raw_data',
            {'field': 'raw_data', 'dtype': str}),
    ])
