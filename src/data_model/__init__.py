#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

from sqlalchemy import TypeDecorator
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.dialects.postgresql import HSTORE

from src.data_model.metaclass.model_metaclass import ModelMeta

class Base(object):

    @staticmethod
    def is_defined_in_parents(cls, attr):
        return any(attr in base.__dict__ for base in cls.__bases__)

# Creation of a declarative base for the SQL Alchemy models to inherit from
Base = declarative_base(cls=Base, metaclass=ModelMeta)

class HashableMutableDict(MutableDict):
    """
    A hashable variant of SQLAlchemy's :class:`MutableDict`.

    This class serializes its contents to a JSON string (with sorted keys)
    and uses the resulting string's hash as its own hash value. This allows
    mutable dictionaries to be used as keys in sets or dictionaries.

    Notes
    -----
    - This is particularly useful when working with PostgreSQL HSTORE columns
      that need to be stored in mutable form and also compared or hashed.
    - Sorting keys ensures deterministic hashing.

    Examples
    --------
    >>> d = HashableMutableDict({'b': 2, 'a': 1})
    >>> hash(d) == hash(HashableMutableDict({'a': 1, 'b': 2}))
    True
    """

    def __hash__(self):
        """
        Compute the hash value of the dictionary.

        The dictionary is serialized to JSON with sorted keys, and the
        resulting string's hash is returned.

        Returns
        -------
        int
            The hash value of the serialized dictionary.

        Examples
        --------
        >>> d = HashableMutableDict({'x': 42})
        >>> isinstance(hash(d), int)
        True
        """
        text = json.dumps(self, sort_keys=True)
        return hash(text)

class HashableHSTORE(TypeDecorator):
    """
    SQLAlchemy type decorator for a hashable PostgreSQL HSTORE column.

    Wraps SQLAlchemy's :class:`HSTORE` type so that retrieved values are
    returned as :class:`HashableMutableDict` objects, making them hashable.

    Attributes
    ----------
    impl : type
        The underlying SQLAlchemy type implementation, set to :class:`HSTORE`.
    cache_ok : bool
        Flag indicating whether the type is safe to cache, set to True.

    """
    impl = HSTORE
    cache_ok = True

    def process_result_value(self, value, dialect):
        """
        Process the value returned from the database.

        Converts the HSTORE value fetched from PostgreSQL into a
        :class:`HashableMutableDict` so that it can be compared and hashed.

        Parameters
        ----------
        value : dict or None
            The HSTORE value retrieved from the database. May be ``None``.
        dialect : Dialect
            The SQLAlchemy dialect in use (e.g., PostgreSQL dialect).

        Returns
        -------
        HashableMutableDict or None
            The converted mutable dictionary if ``value`` is not ``None``,
            otherwise ``None``.
        """
        return HashableMutableDict(value)


from src.data_model.data_provider import DataProvider
from src.data_model.lightning import Lightning
from src.data_model.api_request_log import APIRequestLog
from src.data_model.thunderstorm import Thunderstorm
from src.data_model.thunderstorm import ThunderstormLightningAssociation
from src.data_model.thunderstorm_experiment import ThunderstormExperiment
# from src.meteocat.data_model.lightning import MeteocatLightning  # noqa: F401

