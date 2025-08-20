#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test suite for multiprocessing-based Meteocat lightning import functionality.

This module validates the correct behavior of the multiprocessing pool
initialization, lightning CSV row processing, and API request handling.
It ensures that the Meteocat lightning import pipeline produces the expected
objects and database side effects under normal and erroneous conditions.

Tests
-----
- `test_init_pool_00` : Verifies that the multiprocessing pool initializes and sets globals.
- `test_process_lightnings_00` : Ensures correct parsing of CSV rows into MeteocatLightning objects.
- `test_process_lightnings_01` : Validates error handling for invalid CSV row data.
- `test_process_requests_00` : Checks correct request logging for a full leap year.
- `test_process_requests_01` : Ensures repeated request processing raises an error.

Dependencies
------------
- pytest
- SQLAlchemy
- MeteocatLightning data model
- APIRequestLog data model
- Meteocat lightning import utilities
"""

import pytest

from sqlalchemy import select
from sqlalchemy import func

from src.meteocat.data_model.lightning import MeteocatLightning
from src.data_model.api_request_log import APIRequestLog
from src.apps.meteocat.import_lightnings_from_csv_mp import process_lightnings
from src.apps.meteocat.import_lightnings_from_csv_mp import init_pool
from src.apps.meteocat.import_lightnings_from_csv_mp import process_requests

from typing import Dict
from typing import Any

def test_init_pool_00(mp_data):
    """
    Test multiprocessing pool initialization.

    This test ensures that calling `init_pool` correctly sets
    the global process ID and other shared resources.

    Parameters
    ----------
    mp_data : dict
        Fixture providing multiprocessing-related shared resources
        such as lock, logger, result list, and process ID container.
    """
    init_pool(
        mp_data["lock"],
        mp_data["logger"],
        mp_data["shared_result_list"],
        mp_data["process_id"]
    )

    # Just check that globals are set (implicitly via side effects)
    assert mp_data["process_id"][0] == 0

def test_process_lightnings_00(mp_data: Dict[str, Any], lightnings_csv_rows):
    """
    Test processing of valid lightning CSV rows.

    This test verifies that `process_lightnings` correctly
    converts CSV rows into `MeteocatLightning` objects
    and appends them to the shared result list.

    Parameters
    ----------
    mp_data : dict
        Multiprocessing fixture with shared result list.
    lightnings_csv_rows : list of list
        Fixture providing CSV-formatted lightning rows.
    """
    init_pool(
        mp_data["lock"],
        mp_data["logger"],
        mp_data["shared_result_list"],
        mp_data["process_id"]
    )
    process_lightnings(lightnings_csv_rows)
    assert mp_data["shared_result_list"] is not None
    assert len(mp_data["shared_result_list"][0]) == 1000
    for lightning in mp_data["shared_result_list"][0]:
        assert isinstance(lightning, MeteocatLightning)

def test_process_lightnings_01(logger, caplog, mp_data: Dict[str, Any], lightnings_csv_rows):
    """
    Test processing of invalid lightning CSV row.

    This test modifies one CSV row to include an invalid value
    and ensures that `process_lightnings` appends an error
    message (string) instead of a `MeteocatLightning` object.

    Parameters
    ----------
    logger : logging.Logger
        Fixture providing a test logger.
    caplog : pytest.LogCaptureFixture
        Fixture to capture log messages.
    mp_data : dict
        Multiprocessing fixture with shared result list.
    lightnings_csv_rows : list of list
        Fixture providing CSV-formatted lightning rows.
    """
    init_pool(
        mp_data["lock"],
        mp_data["logger"],
        mp_data["shared_result_list"],
        mp_data["process_id"]
    )
    lightnings_csv_rows[0][6] = -1
    process_lightnings(lightnings_csv_rows)
    assert mp_data["shared_result_list"] is not None
    assert len(mp_data["shared_result_list"][0]) == 1000
    assert not isinstance(mp_data["shared_result_list"][0][0], MeteocatLightning)
    assert isinstance(mp_data["shared_result_list"][0][0], str)

def test_process_requests_00(db_session, data_provider):
    """
    Test processing of requests for a leap year.

    This test ensures that `process_requests` correctly logs
    all hourly requests for 2016 (a leap year), resulting
    in `366 * 24` entries in the database.

    Parameters
    ----------
    db_session : sqlalchemy.orm.Session
        Database session fixture.
    data_provider : Any
        Fixture providing Meteocat API data provider configuration.
    """
    process_requests(db_session, 2016)
    assert db_session.scalar(select(func.count(APIRequestLog.id))) == 366 * 24 # Leap year!

def test_process_requests_01(db_session, data_provider):
    """
    Test repeated processing of requests for the same year.

    This test verifies that calling `process_requests` twice
    for the same year raises a `ValueError`, preventing
    duplicate API request logging.

    Parameters
    ----------
    db_session : sqlalchemy.orm.Session
        Database session fixture.
    data_provider : Any
        Fixture providing Meteocat API data provider configuration.
    """
    process_requests(db_session, 2016)
    with pytest.raises(ValueError):
        process_requests(db_session, 2016)
