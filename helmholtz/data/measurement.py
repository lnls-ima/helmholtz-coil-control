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
    ])

