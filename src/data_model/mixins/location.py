#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytz
from dateutil.tz import tzoffset  # Do not remove, necessary for eval tzoffset in run-time

from sqlalchemy.orm import declarative_mixin

from typing import List
from typing import Dict
from typing import Any


@declarative_mixin
class LocationMixIn(object):
    """
    Mixin for iterating over location coordinates in different spatial reference systems.

    This mixin is intended for SQLAlchemy models that define one or more
    location attributes (coordinates) with associated EPSG codes.
    The mixin allows consistent iteration over these location attributes.

    Attributes
    ----------
    __location__ : list of dict of str to Any
        List of dictionaries defining location attributes.
        Each dictionary must contain an ``'epsg'`` key specifying the EPSG
        code for that location coordinate set.
        The model is expected to have attributes named ``x_<epsg>`` and ``y_<epsg>``.
    """
    __location__: List[Dict[str, Any]]

    def __iter__(self):
        """
        Iterate over location coordinates defined in ``__location__``.

        For each location dictionary in ``__location__``, yields a tuple for
        the X coordinate and another tuple for the Y coordinate, using the
        format ``('x_<epsg>', value)`` and ``('y_<epsg>', value)``.

        The order of yielded tuples is:
            1. X coordinate for the EPSG code
            2. Y coordinate for the EPSG code

        Yields
        ------
        tuple of (str, Any)
            The coordinate attribute name and its value.
        """
        for cls in self.__class__.mro():
            if hasattr(cls, '__location__'):
                locations = cls.__location__
                for location in locations:
                    epsg = str(location['epsg'])
                    yield 'x_' + epsg, getattr(self, 'x_' + epsg)
                    yield 'y_' + epsg, getattr(self, 'y_' + epsg)
