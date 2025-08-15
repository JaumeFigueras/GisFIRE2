#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytz
from dateutil.tz import tzoffset  # Do not remove, necessary for eval tzoffset in run-time

from sqlalchemy.orm import declarative_mixin

from typing import List
from typing import Dict
from typing import Any


@declarative_mixin
class DateTimeMixIn(object):
    """
    Mixin for managing date/time attributes with associated timezone information.

    This mixin is intended for SQLAlchemy models that need to store one or more
    datetime fields along with their timezone specifications, and to provide
    consistent comparison and iteration over these fields.

    Attributes
    ----------
    __date__ : list of dict of str to Any
        List of dictionaries, each defining a datetime attribute.
        Each dictionary must include at least the key ``'name'`` to specify
        the attribute name (e.g., ``{"name": "created_at"}``).
        For each datetime attribute, a corresponding ``tzinfo_<name>`` attribute
        should store the timezone information as a string.
    """
    __date__: List[Dict[str, Any]]

    def __eq__(self, other):
        """
        Compare equality of datetime and timezone attributes between objects.

        Equality is determined by comparing all attributes listed in
        ``__date__`` along with their corresponding timezone attributes
        (``tzinfo_<name>``) in both instances.

        Parameters
        ----------
        other : object
            Another object to compare against. Must have the same datetime and
            timezone attributes as this instance.

        Returns
        -------
        bool
            True if all datetime and timezone pairs match; False otherwise.
        """
        equals: bool = True
        for cls in self.__class__.mro():
            if hasattr(cls, '__date__'):
                dates = cls.__date__
                for attribute in dates:
                    attribute_name = attribute['name']
                    tzinfo_attribute_name = 'tzinfo_' + attribute_name
                    date_time = getattr(self, attribute_name)
                    tzinfo = getattr(self, tzinfo_attribute_name)
                    if hasattr(other, attribute_name) and getattr(other, tzinfo_attribute_name):
                        date_time_other = getattr(other, attribute_name)
                        tzinfo_other = getattr(other, tzinfo_attribute_name)
                        equals = equals and (date_time == date_time_other and tzinfo == tzinfo_other)
                    else:
                        return False
        return equals

    def __iter__(self):
        """
        Iterate over datetime attributes and yield their values in a standardized string format.

        For each attribute defined in ``__date__``, yields a tuple of the attribute
        name and its formatted value according to its timezone information.

        Formatting rules:
            - If ``tzinfo`` starts with ``tzoffset``:
              Convert to UTC, then format in the given offset's timezone.
            - If ``tzinfo`` starts with ``UTC+`` or ``UTC-``:
              Append the offset manually in ``±HHMM`` format.
            - Otherwise:
              Convert using the timezone specified by ``tzinfo``.
            - If the datetime is None, yield None for that attribute.

        Yields
        ------
        tuple of (str, str or None)
            The attribute name and the formatted datetime string (or None if missing).
        """
        for cls in self.__class__.mro():
            if hasattr(cls, '__date__'):
                dates = cls.__date__
                for attribute in dates:
                    attribute_name = attribute['name']
                    tzinfo_attribute_name = 'tzinfo_' + attribute_name
                    date_time = getattr(self, attribute_name)
                    tzinfo = getattr(self, tzinfo_attribute_name)
                    if date_time is None:
                        yield attribute_name, None
                    else:
                        if tzinfo.startswith('tzoffset'):
                            tmp = date_time.astimezone(pytz.UTC)
                            yield attribute_name, tmp.astimezone(eval(tzinfo)).strftime("%Y-%m-%dT%H:%M:%S.%f%z")
                        elif tzinfo.startswith('UTC+') or tzinfo.startswith('UTC-'):
                            yield attribute_name, date_time.strftime("%Y-%m-%dT%H:%M:%S.%f") + str(tzinfo[3:6]) + str(tzinfo[7:9])
                        else:
                            yield attribute_name, date_time.astimezone(pytz.timezone(tzinfo)).strftime("%Y-%m-%dT%H:%M:%S.%f%z")
