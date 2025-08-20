#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test suite for auxiliary data provider creation.

This module validates the behavior of the `main` function
from `src.apps.auxiliar.create_data_providers`, which is
responsible for populating the `DataProvider` table.

Tests
-----
- `test_main_00` : Ensures providers are created when the table is initially empty.
- `test_main_01` : Ensures running `main` again does not create duplicate providers.

Dependencies
------------
- SQLAlchemy
- DataProvider model
- Auxiliary data provider creation script
"""

from sqlalchemy import select
from sqlalchemy import func

from src.apps.auxiliar.create_data_providers import main
from src.data_model.data_provider import DataProvider

def test_main_00(db_session):
    """
    Test creation of data providers when table is empty.

    This test verifies that running `main` with an empty
    `DataProvider` table correctly inserts exactly two entries.

    Parameters
    ----------
    db_session : sqlalchemy.orm.Session
        Database session fixture.
    """
    assert db_session.scalar(select(func.count(DataProvider.name))) == 0
    main(db_session)
    assert db_session.scalar(select(func.count(DataProvider.name))) == 2

def test_main_01(db_session, data_provider):
    """
    Test idempotency of data provider creation.

    This test ensures that running `main` when the
    `DataProvider` table is already populated does not
    create duplicate entries.

    Parameters
    ----------
    db_session : sqlalchemy.orm.Session
        Database session fixture.
    data_provider : DataProvider
        Fixture ensuring that the `DataProvider` table
        is pre-populated with entries.
    """
    assert db_session.scalar(select(func.count(DataProvider.name))) == 2
    main(db_session)
    assert db_session.scalar(select(func.count(DataProvider.name))) == 2
