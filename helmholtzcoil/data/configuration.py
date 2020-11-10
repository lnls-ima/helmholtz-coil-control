# -*- coding: utf-8 -*-

"""Implementation of classes to handle configuration files."""

import sys as _sys
import numpy as _np
import json as _json
import traceback as _traceback
import collections as _collections

from imautils.db import database as _database


class ConnectionConfig(_database.DatabaseAndFileDocument):
    """Read, write and stored connection configuration data."""

    label = 'Connection'
    collection_name = 'connections'
    db_dict = _collections.OrderedDict([
        ('idn', {'field': 'id', 'dtype': int, 'not_null': True}),
        ('date', {'field': 'date', 'dtype': str, 'not_null': True}),
        ('hour', {'field': 'hour', 'dtype': str, 'not_null': True}),
        ('software_version',
            {'field': 'software_version', 'dtype': str, 'not_null': False}),
        ('display_enable',
            {'field': 'display_enable', 'dtype': int, 'not_null': True}),
        ('display_port',
            {'field': 'display_port', 'dtype': str, 'not_null': True}),
        ('display_baudrate',
            {'field': 'display_baudrate', 'dtype': int, 'not_null': True}),
        ('driver_enable',
            {'field': 'driver_enable', 'dtype': int, 'not_null': True}),
        ('driver_port',
            {'field': 'driver_port', 'dtype': str, 'not_null': True}),
        ('driver_baudrate',
            {'field': 'driver_baudrate', 'dtype': int, 'not_null': True}),
        ('multimeter_enable',
            {'field': 'multimeter_enable', 'dtype': int, 'not_null': True}),
        ('multimeter_port',
            {'field': 'multimeter_port', 'dtype': str, 'not_null': True}),
        ('multimeter_baudrate',
            {'field': 'multimeter_baudrate', 'dtype': int, 'not_null': True}),
        ('integrator_enable',
            {'field': 'integrator_enable', 'dtype': int, 'not_null': True}),
        ('integrator_address',
            {'field': 'integrator_address', 'dtype': int, 'not_null': True}),
    ])

    def __init__(
            self, database_name=None, mongo=False, server=None):
        """Initialize object.

        Args:
            filename (str): connection configuration filepath.
            database_name (str): database file path (sqlite) or name (mongo).
            idn (int): id in database table (sqlite) / collection (mongo).
            mongo (bool): flag indicating mongoDB (True) or sqlite (False).
            server (str): MongoDB server.

        """
        super().__init__(
            database_name=database_name, mongo=mongo, server=server)
