#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for the `MeteocatLightning` ORM model.

These tests validate initialization, iteration, validation rules, and
JSON decoding behavior of :class:`~src.meteocat.data_model.lightning.MeteocatLightning`.

Tested scenarios
----------------
- Initialization with all parameters provided.
- Initialization with optional parameters omitted.
- Initialization with unexpected extra fields.
- Initialization with no parameters.
- Validation rules for invalid input values.
- Iteration protocol via ``__iter__``.
- Decoding from GisFIRE API JSON via ``object_hook_gisfire_api``.

Fixtures
--------
db_session : Session
    SQLAlchemy database session fixture.
data_provider : list of DataProvider
    Fixture providing available data providers.
"""

import datetime
import pytz
import pytest
import json

from sqlalchemy.orm import Session

from src.meteocat.data_model.lightning import MeteocatLightning
from src.data_model.data_provider import DataProvider

from typing import List

def test_meteocat_lightning_init_00(db_session: Session, data_provider: List[DataProvider]) -> None:
    """
    Test initialization of `MeteocatLightning` with all parameters.

    This test ensures that when a `MeteocatLightning` instance is initialized
    with coordinates, timestamp, data provider, and additional lightning-specific
    attributes, all fields are correctly set and the geometry is properly constructed.

    Parameters
    ----------
    db_session : Session
        SQLAlchemy database session fixture.
    data_provider : list of DataProvider
        Fixture providing available data providers.


    Expected behavior
    -----------------
    - Coordinates (`x_4258`, `y_4258`, `x_4326`, `y_4326`, `x_25831`, `y_25831`) are correctly stored.
    - `date_time` is stored with correct timezone.
    - `data_provider` is correctly linked.
    - `geometry_4326` is generated as a valid WKT point with SRID 4326.
    - `geometry_4258` is generated as a valid WKT point with SRID 4258.
    - `geometry_25831` is generated as a valid WKT point with SRID 25831.
    - Meteocat-specific attributes (`meteocat_id`, `peak_current`, `multiplicity`,
      `chi_squared`, `ellipse_major_axis`, `ellipse_minor_axis`, `ellipse_angle`,
      `number_of_sensors`, `hit_ground`, `municipality_code`) are correctly set.
    """
    lightning = MeteocatLightning(
        date_time=datetime.datetime(2025, 6, 24, 17, 0, 0, tzinfo=pytz.UTC),
        data_provider=data_provider[0],
        x_4258=2.113066,
        y_4258=41.388147,
        meteocat_id=123456,
        peak_current=1.23,
        multiplicity=4,
        chi_squared=0.98,
        ellipse_major_axis=1234.56,
        ellipse_minor_axis=-654.321,
        ellipse_angle=25.86,
        number_of_sensors=2,
        hit_ground=True,
        municipality_code="08445"
    )
    # Coordinate and datetime checks
    assert lightning.x_4326 == 2.113066
    assert lightning.y_4326 == 41.388147
    assert lightning.geometry_4326 == 'SRID=4326;POINT(2.113066 41.388147)'
    assert lightning.date_time == datetime.datetime(2025, 6, 24, 17, 0, 0, tzinfo=pytz.UTC)
    assert lightning.data_provider == data_provider[0]
    # Meteocat-specific attribute checks
    assert lightning.x_4258 == 2.113066
    assert lightning.y_4258 == 41.388147
    assert lightning.geometry_4258 == 'SRID=4258;POINT(2.113066 41.388147)'
    assert lightning.x_25831 == 425846.42118526914
    assert lightning.y_25831 == 4582226.001558889
    assert lightning.geometry_25831 == 'SRID=25831;POINT(425846.42118526914 4582226.001558889)'
    assert lightning.meteocat_id == 123456
    assert lightning.peak_current == 1.23
    assert lightning.multiplicity == 4
    assert lightning.chi_squared == 0.98
    assert lightning.ellipse_major_axis == 1234.56
    assert lightning.ellipse_minor_axis == -654.321
    assert lightning.ellipse_angle == 25.86
    assert lightning.number_of_sensors == 2
    assert lightning.hit_ground is True
    assert lightning.municipality_code == "08445"

def test_meteocat_lightning_init_01(db_session: Session, data_provider: List[DataProvider]):
    """
    Test initialization of `MeteocatLightning` with only required parameters.

    Ensures that when optional fields (`multiplicity` and `municipality_code`)
    are omitted, the instance is still correctly initialized, with default
    `None` values for the missing attributes. Also verifies that coordinates
    in multiple reference systems and geometry fields are correctly computed.

    Parameters
    ----------
    db_session : Session
        SQLAlchemy database session fixture.
    data_provider : list of DataProvider
        Fixture providing available data providers.


    Expected behavior
    -----------------
    - Coordinates (`x_4258`, `y_4258`, `x_4326`, `y_4326`, `x_25831`, `y_25831`) are correctly set.
    - Geometry fields (`geometry_4258`, `geometry_4326`, `geometry_25831`) are correctly generated.
    - Date/time and data provider are stored correctly.
    - Meteocat-specific attributes (`meteocat_id`, `peak_current`, `chi_squared`,
      `ellipse_major_axis`, `ellipse_minor_axis`, `ellipse_angle`, `number_of_sensors`, `hit_ground`) are set correctly.
    - Optional attributes (`multiplicity`, `municipality_code`) default to `None`.
    """
    lightning = MeteocatLightning(
        date_time=datetime.datetime(2025, 6, 24, 17, 0, 0, tzinfo=pytz.UTC),
        data_provider=data_provider[0],
        x_4258=2.113066,
        y_4258=41.388147,
        meteocat_id=123456,
        peak_current=1.23,
        chi_squared=0.98,
        ellipse_major_axis=1234.56,
        ellipse_minor_axis=-654.321,
        ellipse_angle=25.86,
        number_of_sensors=2,
        hit_ground=True
    )
    # Coordinate and datetime checks
    assert lightning.x_4326 == 2.113066
    assert lightning.y_4326 == 41.388147
    assert lightning.geometry_4326 == 'SRID=4326;POINT(2.113066 41.388147)'
    assert lightning.date_time == datetime.datetime(2025, 6, 24, 17, 0, 0, tzinfo=pytz.UTC)
    assert lightning.data_provider == data_provider[0]
    # Meteocat-specific attribute checks
    assert lightning.x_4258 == 2.113066
    assert lightning.y_4258 == 41.388147
    assert lightning.geometry_4258 == 'SRID=4258;POINT(2.113066 41.388147)'
    assert lightning.x_25831 == 425846.42118526914
    assert lightning.y_25831 == 4582226.001558889
    assert lightning.geometry_25831 == 'SRID=25831;POINT(425846.42118526914 4582226.001558889)'
    assert lightning.meteocat_id == 123456
    assert lightning.peak_current == 1.23
    assert lightning.chi_squared == 0.98
    assert lightning.ellipse_major_axis == 1234.56
    assert lightning.ellipse_minor_axis == -654.321
    assert lightning.ellipse_angle == 25.86
    assert lightning.number_of_sensors == 2
    assert lightning.hit_ground is True
    assert lightning.multiplicity is None
    assert lightning.municipality_code is None

def test_meteocat_lightning_init_02(db_session: Session, data_provider: List[DataProvider]) -> None:
    """
    Test initialization of `MeteocatLightning` with unexpected extra fields.

    Verifies that the constructor ignores any unexpected keyword arguments,
    raising no errors, and that only valid attributes are set. All coordinate
    and Meteocat-specific fields are correctly initialized.

    Parameters
    ----------
    db_session : Session
        SQLAlchemy database session fixture.
    data_provider : list of DataProvider
        Fixture providing available data providers.


    Expected behavior
    -----------------
    - Extra keyword arguments are ignored.
    - All valid coordinates, geometries, date/time, data provider, and Meteocat-specific attributes are correctly initialized.
    - `extra_field` does not exist on the resulting instance.
    """
    lightning = MeteocatLightning(
        date_time=datetime.datetime(2025, 6, 24, 17, 0, 0, tzinfo=pytz.UTC),
        data_provider=data_provider[0],
        x_4258=2.113066,
        y_4258=41.388147,
        meteocat_id=123456,
        peak_current=1.23,
        multiplicity=4,
        chi_squared=0.98,
        ellipse_major_axis=1234.56,
        ellipse_minor_axis=-654.321,
        ellipse_angle=25.86,
        number_of_sensors=2,
        hit_ground=True,
        municipality_code="08445",
        extra_field="extra field"  # type: ignore
    )
    # Coordinate and datetime checks
    assert lightning.x_4326 == 2.113066
    assert lightning.y_4326 == 41.388147
    assert lightning.geometry_4326 == 'SRID=4326;POINT(2.113066 41.388147)'
    assert lightning.date_time == datetime.datetime(2025, 6, 24, 17, 0, 0, tzinfo=pytz.UTC)
    assert lightning.data_provider == data_provider[0]
    # Meteocat-specific attribute checks
    assert lightning.x_4258 == 2.113066
    assert lightning.y_4258 == 41.388147
    assert lightning.geometry_4258 == 'SRID=4258;POINT(2.113066 41.388147)'
    assert lightning.x_25831 == 425846.42118526914
    assert lightning.y_25831 == 4582226.001558889
    assert lightning.geometry_25831 == 'SRID=25831;POINT(425846.42118526914 4582226.001558889)'
    assert lightning.meteocat_id == 123456
    assert lightning.peak_current == 1.23
    assert lightning.multiplicity == 4
    assert lightning.chi_squared == 0.98
    assert lightning.ellipse_major_axis == 1234.56
    assert lightning.ellipse_minor_axis == -654.321
    assert lightning.ellipse_angle == 25.86
    assert lightning.number_of_sensors == 2
    assert lightning.hit_ground is True
    assert lightning.municipality_code == "08445"
    assert not hasattr(lightning, "extra_field")

def test_meteocat_lightning_init_03(db_session: Session, data_provider: List[DataProvider]) -> None:
    """
    Test initialization of `MeteocatLightning` with no parameters.

    Ensures that a default `MeteocatLightning` instance can be created with
    all attributes initialized to `None`.

    Parameters
    ----------
    db_session : Session
        SQLAlchemy database session fixture.
    data_provider : list of DataProvider
        Fixture providing available data providers.


    Expected behavior
    -----------------
    - All coordinate, geometry, date/time, data provider, and Meteocat-specific attributes are `None`.
    """
    lightning = MeteocatLightning()  # type: ignore
    # Coordinate and datetime checks
    assert getattr(lightning, "x_4326", None) is None
    assert getattr(lightning, "y_4326", None) is None
    assert getattr(lightning, "geometry_4326", None) is None
    assert getattr(lightning, "date_time", None) is None
    assert getattr(lightning, "data_provider", None) is None
    # Meteocat-specific attribute checks
    assert getattr(lightning, "x_4258", None) is None
    assert getattr(lightning, "y_4258", None) is None
    assert getattr(lightning, "geometry_4258", None) is None
    assert getattr(lightning, "x_25831", None) is None
    assert getattr(lightning, "y_25831", None) is None
    assert getattr(lightning, "geometry_25831", None) is None
    assert getattr(lightning, "meteocat_id", None) is None
    assert getattr(lightning, "peak_current", None) is None
    assert getattr(lightning, "multiplicity", None) is None
    assert getattr(lightning, "chi_squared", None) is None
    assert getattr(lightning, "ellipse_major_axis", None) is None
    assert getattr(lightning, "ellipse_minor_axis", None) is None
    assert getattr(lightning, "ellipse_angle", None) is None
    assert getattr(lightning, "number_of_sensors", None) is None
    assert getattr(lightning, "hit_ground", None) is None
    assert getattr(lightning, "municipality_code", None) is None

def test_meteocat_lightning_init_04(db_session: Session, data_provider: List[DataProvider]) -> None:
    """
    Test that `MeteocatLightning` raises a ValueError for invalid sensor count.

    Verifies that the class enforces a non-negative number of sensors. Attempting
    to initialize an instance with a negative `number_of_sensors` should raise a
    `ValueError`.

    Parameters
    ----------
    db_session : Session
        SQLAlchemy database session fixture.
    data_provider : list of DataProvider
        Fixture providing available data providers.

    Expected behavior
    -----------------
    - Initializing with `number_of_sensors < 0` raises a `ValueError`.
    """
    with pytest.raises(ValueError):
        _ = MeteocatLightning(
            date_time=datetime.datetime(2025, 6, 24, 17, 0, 0, tzinfo=pytz.UTC),
            data_provider=data_provider[0],
            x_4258=2.113066,
            y_4258=41.388147,
            meteocat_id=123456,
            peak_current=1.23,
            multiplicity=4,
            chi_squared=0.98,
            ellipse_major_axis=1234.56,
            ellipse_minor_axis=-654.321,
            ellipse_angle=25.86,
            number_of_sensors=-2,
            hit_ground=True,
            municipality_code="08445"
        )

def test_lightning_iter_00(db_session: Session, data_provider: List[DataProvider]):
    """
    Test iteration protocol of `MeteocatLightning` with full parameters.

    Ensures that `__iter__` yields expected key-value pairs when all
    attributes are populated.

    Parameters
    ----------
    db_session : Session
        SQLAlchemy session fixture.
    data_provider : list of DataProvider
        Fixture with available data providers.

    Expected behavior
    -----------------
    - Converting instance to `dict()` returns all expected keys.
    - Attribute values match initialization.
    """
    lightning = MeteocatLightning(
        date_time=datetime.datetime(2025, 6, 24, 17, 0, 0, tzinfo=pytz.UTC),
        data_provider=data_provider[0],
        x_4258=2.113066,
        y_4258=41.388147,
        meteocat_id=123456,
        peak_current=1.23,
        multiplicity=4,
        chi_squared=0.98,
        ellipse_major_axis=1234.56,
        ellipse_minor_axis=654.321,
        ellipse_angle=25.86,
        number_of_sensors=2,
        hit_ground=True,
        municipality_code="08445"
    )
    lightning.id = 1  # mimic a persisted object with PK

    iter_dict = dict(lightning)

    assert iter_dict["id"] == 1
    assert iter_dict["data_provider"] == data_provider[0].name
    assert iter_dict["x_4326"] == 2.113066
    assert iter_dict["y_4326"] == 41.388147
    assert iter_dict["date_time"] == datetime.datetime(2025, 6, 24, 17, 0, 0, tzinfo=pytz.UTC).strftime("%Y-%m-%dT%H:%M:%S.%f%z")
    assert iter_dict["x_4258"] == 2.113066
    assert iter_dict["y_4258"] == 41.388147
    assert iter_dict["x_25831"] == 425846.42118526914
    assert iter_dict["y_25831"] == 4582226.001558889
    assert iter_dict["meteocat_id"] == 123456
    assert iter_dict["peak_current"] == 1.23
    assert iter_dict["multiplicity"] == 4
    assert iter_dict["chi_squared"] == 0.98
    assert iter_dict["ellipse_major_axis"] == 1234.56
    assert iter_dict["ellipse_minor_axis"] == 654.321
    assert iter_dict["ellipse_angle"] == 25.86
    assert iter_dict["number_of_sensors"] == 2
    assert iter_dict["hit_ground"] == True
    assert iter_dict["municipality_code"] == "08445"

def test_lightning_iter_01(db_session: Session, data_provider: List[DataProvider]):
    """
    Test iteration protocol of `MeteocatLightning` with optional attributes omitted.

    Ensures that iteration still produces a dictionary with correct keys,
    but optional attributes yield `None`.

    Parameters
    ----------
    db_session : Session
        SQLAlchemy session fixture.
    data_provider : list of DataProvider
        Fixture with available data providers.

    Expected behavior
    -----------------
    - All required attributes present.
    - Optional attributes (`multiplicity`, `municipality_code`) are `None`.
    """
    lightning = MeteocatLightning(
        date_time=datetime.datetime(2025, 6, 24, 17, 0, 0, tzinfo=pytz.UTC),
        data_provider=data_provider[0],
        x_4258=2.113066,
        y_4258=41.388147,
        meteocat_id=123456,
        peak_current=1.23,
        chi_squared=0.98,
        ellipse_major_axis=1234.56,
        ellipse_minor_axis=654.321,
        ellipse_angle=25.86,
        number_of_sensors=2,
        hit_ground=True
    )
    lightning.id = 1  # mimic a persisted object with PK

    iter_dict = dict(lightning)

    assert iter_dict["id"] == 1
    assert iter_dict["data_provider"] == data_provider[0].name
    assert iter_dict["x_4326"] == 2.113066
    assert iter_dict["y_4326"] == 41.388147
    assert iter_dict["date_time"] == datetime.datetime(2025, 6, 24, 17, 0, 0, tzinfo=pytz.UTC).strftime("%Y-%m-%dT%H:%M:%S.%f%z")
    assert iter_dict["x_4258"] == 2.113066
    assert iter_dict["y_4258"] == 41.388147
    assert iter_dict["x_25831"] == 425846.42118526914
    assert iter_dict["y_25831"] == 4582226.001558889
    assert iter_dict["meteocat_id"] == 123456
    assert iter_dict["peak_current"] == 1.23
    assert iter_dict["multiplicity"] is None
    assert iter_dict["chi_squared"] == 0.98
    assert iter_dict["ellipse_major_axis"] == 1234.56
    assert iter_dict["ellipse_minor_axis"] == 654.321
    assert iter_dict["ellipse_angle"] == 25.86
    assert iter_dict["number_of_sensors"] == 2
    assert iter_dict["hit_ground"] == True
    assert iter_dict["municipality_code"] is None

def test_meteocat_lightning_object_hook_gisfire_api_json_loads_00():
    """
    Test JSON decoding of GisFIRE API dict with `lightning` and `distance`.

    Expected behavior
    -----------------
    - `json.loads` with `object_hook` returns the dictionary unchanged.
    """
    json_str = json.dumps({"lightning": 123, "distance": 45.6})
    result = json.loads(json_str, object_hook=MeteocatLightning.object_hook_gisfire_api)
    assert isinstance(result, dict)
    assert result == {"lightning": 123, "distance": 45.6}

def test_meteocat_lightning_object_hook_gisfire_api_json_loads_01():
    """
    Test JSON decoding of unrelated dict.

    Expected behavior
    -----------------
    - `json.loads` with `object_hook` returns `None`.
    """
    json_str = json.dumps({"foo": "bar"})
    result = json.loads(json_str, object_hook=MeteocatLightning.object_hook_gisfire_api)
    assert result is None

def test_meteocat_lightning_object_hook_gisfire_api_json_loads_02():
    """
    Test JSON decoding of a full MeteocatLightning dict.

    Expected behavior
    -----------------
    - Returns a `MeteocatLightning` instance.
    - All attributes correctly parsed and typed.
    - Date/time parsed with microsecond precision and correct timezone.
    - Coordinates and geometries computed correctly.
    """
    dct = {
        "meteocat_id": "101",
        "peak_current": "12.5",
        "multiplicity": "3",
        "chi_squared": "1.2",
        "ellipse_major_axis": "4.5",
        "ellipse_minor_axis": "2.3",
        "ellipse_angle": "45.0",
        "number_of_sensors": "7",
        "hit_ground": True,
        "municipality_code": "08019",
        "id": "555",
        "data_provider": "TestProvider",
        "x_25831": "425846.42118526914",
        "y_25831": "4582226.001558889",
        "x_4258": "2.113066",
        "y_4258": "41.388147",
        "date_time": "2024-08-15T12:34:56.000111+0000"
    }
    json_str = json.dumps(dct)
    result = json.loads(json_str, object_hook=MeteocatLightning.object_hook_gisfire_api)
    assert isinstance(result, MeteocatLightning)
    assert result.meteocat_id == 101
    assert result.peak_current == 12.5
    assert result.multiplicity == 3
    assert result.chi_squared == 1.2
    assert result.ellipse_major_axis == 4.5
    assert result.ellipse_minor_axis == 2.3
    assert result.ellipse_angle == 45.0
    assert result.number_of_sensors == 7
    assert result.hit_ground is True
    assert result.municipality_code == "08019"
    assert result.id == 555
    assert result.data_provider_name == "TestProvider"
    assert result.date_time == datetime.datetime(2024, 8, 15, 12, 34, 56, microsecond=111, tzinfo=datetime.timezone.utc)
    assert result.x_4326 == 2.113066
    assert result.y_4326 == 41.388147
    assert result.geometry_4326 == 'SRID=4326;POINT(2.113066 41.388147)'
    assert result.x_4258 == 2.113066
    assert result.y_4258 == 41.388147
    assert result.geometry_4258 == 'SRID=4258;POINT(2.113066 41.388147)'
    assert result.x_25831 == 425846.42118526914
    assert result.y_25831 == 4582226.001558889
    assert result.geometry_25831 == 'SRID=25831;POINT(425846.42118526914 4582226.001558889)'

def test_meteocat_lightning_object_hook_gisfire_api_json_loads_03():
    """
    Test JSON decoding of a list of dicts with `lightning` and `distance`.

    Expected behavior
    -----------------
    - Returns a list of dicts.
    - Each dict contains:
        - `"lightning"`: a `MeteocatLightning` instance with correctly parsed attributes.
        - `"distance"`: preserved as a float.
    """
    dct = {
        "meteocat_id": "101",
        "peak_current": "12.5",
        "multiplicity": "3",
        "chi_squared": "1.2",
        "ellipse_major_axis": "4.5",
        "ellipse_minor_axis": "2.3",
        "ellipse_angle": "45.0",
        "number_of_sensors": "7",
        "hit_ground": True,
        "municipality_code": "08019",
        "id": "555",
        "data_provider": "TestProvider",
        "x_25831": "425846.42118526914",
        "y_25831": "4582226.001558889",
        "x_4258": "2.113066",
        "y_4258": "41.388147",
        "date_time": "2024-08-15T12:34:56.000111+0000"
    }
    lst = [{"lightning": dct, "distance": 45.6}, {"lightning": dct, "distance": 45.6}]
    json_str = json.dumps(lst)
    results = json.loads(json_str, object_hook=MeteocatLightning.object_hook_gisfire_api)
    for result in results:
        lightning = result["lightning"]
        assert isinstance(lightning, MeteocatLightning)
        assert lightning.meteocat_id == 101
        assert lightning.peak_current == 12.5
        assert lightning.multiplicity == 3
        assert lightning.chi_squared == 1.2
        assert lightning.ellipse_major_axis == 4.5
        assert lightning.ellipse_minor_axis == 2.3
        assert lightning.ellipse_angle == 45.0
        assert lightning.number_of_sensors == 7
        assert lightning.hit_ground is True
        assert lightning.municipality_code == "08019"
        assert lightning.id == 555
        assert lightning.data_provider_name == "TestProvider"
        assert lightning.date_time == datetime.datetime(2024, 8, 15, 12, 34, 56, microsecond=111, tzinfo=datetime.timezone.utc)
        assert lightning.x_4326 == 2.113066
        assert lightning.y_4326 == 41.388147
        assert lightning.geometry_4326 == 'SRID=4326;POINT(2.113066 41.388147)'
        assert lightning.x_4258 == 2.113066
        assert lightning.y_4258 == 41.388147
        assert lightning.geometry_4258 == 'SRID=4258;POINT(2.113066 41.388147)'
        assert lightning.x_25831 == 425846.42118526914
        assert lightning.y_25831 == 4582226.001558889
        assert lightning.geometry_25831 == 'SRID=25831;POINT(425846.42118526914 4582226.001558889)'
        distance = result["distance"]
        assert distance == 45.6



