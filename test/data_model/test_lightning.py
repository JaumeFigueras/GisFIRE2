#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for the `Lightning` ORM model.

These tests validate the initialization and iteration behavior of the
:class:`~src.data_model.lightning.Lightning` class, ensuring that
attributes are correctly set, defaults are respected, and iteration
yields expected key-value pairs.

Tested scenarios
----------------
- Initialization with all parameters provided.
- Initialization with an unexpected extra field.
- Initialization with no parameters.
- Iteration protocol via ``__iter__``.

Fixtures
--------
db_session : Session
    SQLAlchemy database session fixture.
data_provider : list of DataProvider
    Fixture providing available data providers.
"""

import datetime
import pytz

from sqlalchemy.orm import Session

from src.data_model.lightning import Lightning
from src.data_model.data_provider import DataProvider

from typing import List


def test_lightning_init_00(db_session: Session, data_provider: List[DataProvider]) -> None:
    """
    Test initialization of `Lightning` with all parameters.

    This test ensures that when a `Lightning` instance is initialized
    with coordinates, timestamp, and data provider, all attributes are
    correctly set and the geometry is properly constructed.

    Parameters
    ----------
    db_session : Session
        SQLAlchemy database session fixture.
    data_provider : list of DataProvider
        Fixture providing available data providers.


    Expected behavior
    -----------------
    - `x_4326` and `y_4326` are stored as given.
    - `date_time` is stored with correct timezone.
    - `data_provider` is linked to the given provider.
    - `geometry_4326` is generated as a valid WKT point with SRID 4326.
    """
    lightning = Lightning(
        x_4326=2.113066,
        y_4326=41.388147,
        lightning_utc_date_time=datetime.datetime(2025, 6, 24, 17, 0, 0, tzinfo=pytz.UTC),
        data_provider=data_provider[1]
    )
    assert lightning.x_4326 == 2.113066
    assert lightning.y_4326 == 41.388147
    assert lightning.lightning_utc_date_time == datetime.datetime(2025, 6, 24, 17, 0, 0, tzinfo=pytz.UTC)
    assert lightning.data_provider == data_provider[1]
    assert lightning.geometry_4326 ==  'SRID=4326;POINT(2.113066 41.388147)'

def test_lightning_init_01(db_session: Session, data_provider: List[DataProvider]):
    """
    Test initialization with an unexpected extra field.

    This test ensures that if an unexpected keyword argument is passed
    to `Lightning`, it is ignored and does not become an attribute.

    Parameters
    ----------
    db_session : Session
        SQLAlchemy database session fixture.
    data_provider : list of DataProvider
        Fixture providing available data providers.


    Expected behavior
    -----------------
    - `x_4326` and `y_4326` are stored as given.
    - `date_time` is stored with correct timezone.
    - `data_provider` is linked to the given provider.
    - `geometry_4326` is generated as a valid WKT point with SRID 4326.
    - Unexpected fields (e.g., ``extra_field``) are ignored.
    """
    lightning = Lightning(
        x_4326=2.113066,
        y_4326=41.388147,
        lightning_utc_date_time=datetime.datetime(2025, 6, 24, 17, 0, 0, tzinfo=pytz.UTC),
        data_provider=data_provider[1],
        extra_field="extra field"  # type: ignore
    )
    assert lightning.x_4326 == 2.113066
    assert lightning.y_4326 == 41.388147
    assert lightning.lightning_utc_date_time == datetime.datetime(2025, 6, 24, 17, 0, 0, tzinfo=pytz.UTC)
    assert lightning.data_provider == data_provider[1]
    assert lightning.data_provider.data_provider_name == data_provider[1].data_provider_name
    assert lightning.geometry_4326 ==  'SRID=4326;POINT(2.113066 41.388147)'
    assert not hasattr(lightning, "extra_field")

def test_lightning_init_02():
    """
    Test initialization with no parameters.

    This test ensures that when `Lightning` is initialized without
    arguments, all attributes default to ``None``.


    Expected behavior
    -----------------
    - `x_4326` is ``None``.
    - `y_4326` is ``None``.
    - `geom_4326` is ``None``.
    - `date_time` is ``None``.
    - `data_provider` is ``None``.
    """
    lightning = Lightning()  # type: ignore
    assert getattr(lightning, "x_4326", None) is None
    assert getattr(lightning, "y_4326", None) is None
    assert getattr(lightning, "geometry_4326", None) is None
    assert getattr(lightning, "date_time", None) is None
    assert getattr(lightning, "data_provider", None) is None

def test_lightning_iter_00(db_session: Session, data_provider: List[DataProvider]):
    """
    Test the iteration protocol of `Lightning`.

    This test ensures that calling `dict()` on a `Lightning` instance
    returns a dictionary containing the expected attributes and values
    from `__iter__`.

    Parameters
    ----------
    db_session : Session
        SQLAlchemy database session fixture.
    data_provider : list of DataProvider
        Fixture providing available data providers.


    Expected behavior
    -----------------
    - `__iter__` yields key-value pairs for:
        - `id`
        - `data_provider`
        - location attributes from `LocationMixIn`
        - datetime attributes from `DateTimeMixIn`
    - Converting the instance to `dict(lightning)` should produce
      a dictionary with all expected keys and correct values.
    """
    lightning = Lightning(
        x_4326=2.113066,
        y_4326=41.388147,
        lightning_utc_date_time=datetime.datetime(2025, 6, 24, 17, 0, 0, tzinfo=pytz.UTC),
        data_provider=data_provider[0],
    )
    lightning.lightning_id = 1  # mimic a persisted object with PK

    iter_dict = dict(lightning)

    assert iter_dict["lightning_id"] == 1
    assert iter_dict["data_provider"] == data_provider[0].data_provider_name
    assert iter_dict["x_4326"] == 2.113066
    assert iter_dict["y_4326"] == 41.388147
    assert iter_dict["lightning_utc_date_time"] == datetime.datetime(2025, 6, 24, 17, 0, 0, tzinfo=pytz.UTC).strftime("%Y-%m-%dT%H:%M:%S.%f%z")



