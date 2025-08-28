#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import pytz

from sqlalchemy.orm import Session

from src.data_model.thunderstorm import Thunderstorm
from src.data_model.data_provider import DataProvider
from src.data_model.thunderstorm_experiment import ThunderstormExperiment
from src.data_model.thunderstorm_experiment import ThunderstormExperimentParams
from src.data_model.thunderstorm_experiment import ThunderstormExperimentAlgorithm
from src.data_model.lightning import Lightning

from typing import List

def test_thunderstorm_init_00(db_session: Session, data_provider: List[DataProvider]) -> None:
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
    tstorm = Thunderstorm(
        x_4326=2.113066,
        y_4326=41.388147,
        thunderstorm_utc_date_time_start=datetime.datetime(2025, 6, 24, 17, 0, 0, tzinfo=pytz.UTC),
        thunderstorm_utc_date_time_end=datetime.datetime(2025, 6, 24, 21, 0, 0, tzinfo=pytz.UTC),
        thunderstorm_experiment=23,
        thunderstorm_lightnings_per_minute=12,
        thunderstorm_travelled_distance=123.25,
        thunderstorm_cardinal_direction=25,
        thunderstorm_speed=17
    )
    assert tstorm.x_4326 == 2.113066
    assert tstorm.y_4326 == 41.388147
    assert tstorm.geometry_4326 == 'SRID=4326;POINT(2.113066 41.388147)'
    assert tstorm.thunderstorm_utc_date_time_start == datetime.datetime(2025, 6, 24, 17, 0, 0, tzinfo=pytz.UTC)
    assert tstorm.thunderstorm_utc_date_time_end == datetime.datetime(2025, 6, 24, 21, 0, 0, tzinfo=pytz.UTC)
    assert tstorm.thunderstorm_experiment_id == 23
    assert tstorm.thunderstorm_lightnings_per_minute == 12
    assert tstorm.thunderstorm_travelled_distance == 123.25
    assert tstorm.thunderstorm_cardinal_direction == 25
    assert tstorm.thunderstorm_speed == 17

def test_thunderstorm_init_01(db_session: Session, data_provider: List[DataProvider]) -> None:
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
    tstorm = Thunderstorm(
        x_4326=2.113066,
        y_4326=41.388147,
        thunderstorm_experiment=23,
    )
    assert tstorm.x_4326 == 2.113066
    assert tstorm.y_4326 == 41.388147
    assert tstorm.geometry_4326 == 'SRID=4326;POINT(2.113066 41.388147)'
    assert tstorm.thunderstorm_utc_date_time_start is None
    assert tstorm.thunderstorm_utc_date_time_end is None
    assert tstorm.thunderstorm_experiment_id == 23
    assert tstorm.thunderstorm_lightnings_per_minute is None
    assert tstorm.thunderstorm_travelled_distance is None
    assert tstorm.thunderstorm_cardinal_direction is None
    assert tstorm.thunderstorm_speed is None

def test_thunderstorm_init_02(db_session: Session, data_provider: List[DataProvider]) -> None:
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
    tstorm = Thunderstorm(
        x_4326=2.113066,
        y_4326=41.388147,
        thunderstorm_experiment=23,
        extra_field="extra field"  # type: ignore
    )
    assert tstorm.x_4326 == 2.113066
    assert tstorm.y_4326 == 41.388147
    assert tstorm.geometry_4326 == 'SRID=4326;POINT(2.113066 41.388147)'
    assert tstorm.thunderstorm_utc_date_time_start is None
    assert tstorm.thunderstorm_utc_date_time_end is None
    assert tstorm.thunderstorm_experiment_id == 23
    assert tstorm.thunderstorm_lightnings_per_minute is None
    assert tstorm.thunderstorm_travelled_distance is None
    assert tstorm.thunderstorm_cardinal_direction is None
    assert tstorm.thunderstorm_speed is None
    assert not hasattr(tstorm, "extra_field")

def test_thunderstorm_init_03(db_session: Session, data_provider: List[DataProvider]) -> None:
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
    tstorm = Thunderstorm()
    assert getattr(tstorm, "x_4326", None) is None
    assert getattr(tstorm, "y_4326", None) is None
    assert getattr(tstorm, "geometry_4326", None) is None
    assert getattr(tstorm, "thunderstorm_utc_date_time_start", None) is None
    assert getattr(tstorm, "thunderstorm_utc_date_time_end", None) is None
    assert getattr(tstorm, "thunderstorm_experiment_id", None) is None
    assert getattr(tstorm, "thunderstorm_lightnings_per_minute", None) is None
    assert getattr(tstorm, "thunderstorm_travelled_distance", None) is None
    assert getattr(tstorm, "thunderstorm_cardinal_direction", None) is None
    assert getattr(tstorm, "thunderstorm_speed", None) is None
    assert getattr(tstorm, "thunderstorm_number_of_lightnings", None) is None

