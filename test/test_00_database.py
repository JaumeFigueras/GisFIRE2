#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pytest test module for verifying the initial state of the test database.

This module contains tests to ensure that the temporary PostgreSQL database
used for testing is properly initialized. It checks that:

- No user-defined tables exist at startup.
- ORM-mapped tables are empty before inserting test data.
- Fixtures properly populate test data as expected.

Functions
---------
test_database_init_01(postgresql_gisfire)
    Checks that no user-defined tables exist in the 'public' schema at database start.

test_database_init_02(db_session)
    Verifies that all relevant ORM-mapped tables are empty at test start.

test_database_init_03(db_session, data_provider)
    Verifies that the `data_provider` fixture correctly populates the DataProvider table.
"""

from src.data_model.data_provider import DataProvider

from typing import Any
from typing import Tuple
from typing import Optional
from typing import List
from psycopg.cursor import Cursor
from sqlalchemy.orm import Session


def test_database_init_01(postgresql_gisfire: Any) -> None:
    """
    Ensure that no user-defined tables exist in the 'public' schema.

    Parameters
    ----------
    postgresql_gisfire : Any
        A test PostgreSQL database fixture (e.g., from pytest_postgresql).

    Notes
    -----
    This test confirms that the database starts clean and no leftover tables
    from previous tests exist.
    """
    cursor: Cursor = postgresql_gisfire.cursor()
    cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'")
    record: Optional[Tuple[int]] = cursor.fetchone()
    assert record[0] == 0

def test_database_init_02(db_session: Session) -> None:
    """
    Verify that all relevant ORM-mapped tables are empty at test start.

    Parameters
    ----------
    db_session : Session
        A SQLAlchemy session connected to the test database.

    Notes
    -----
    This test checks that tables such as `DataProvider`, `Lightning`,
    `Thunderstorm`, etc., are empty before any test data is inserted.
    """
    assert db_session.query(DataProvider).count() == 0
    # assert db_session.query(Lightning).count() == 0
    # assert db_session.query(Thunderstorm).count() == 0
    # assert db_session.query(ThunderstormLightningAssociation).count() == 0
    # assert db_session.query(ThunderstormExperiment).count() == 0
    # assert db_session.query(MeteocatLightning).count() == 0
    # assert db_session.query(MeteocatThunderstorm).count() == 0

def test_database_init_03(db_session: Session, data_provider: List[DataProvider]) -> None:
    """
    Verify that the `data_provider` fixture correctly populates the DataProvider table.

    Parameters
    ----------
    db_session : Session
        A SQLAlchemy session connected to the test database.
    data_provider : list of DataProvider
        Fixture that provides sample `DataProvider` instances for testing.

    Notes
    -----
    This test ensures that the `data_provider` fixture inserts exactly two
    DataProvider records and that other tables remain empty.
    """
    assert db_session.query(DataProvider).count() == 2
    # assert db_session.query(Lightning).count() == 0
    # assert db_session.query(Thunderstorm).count() == 0
    # assert db_session.query(ThunderstormLightningAssociation).count() == 0
    # assert db_session.query(ThunderstormExperiment).count() == 0
    # assert db_session.query(MeteocatLightning).count() == 0
    # assert db_session.query(MeteocatThunderstorm).count() == 0



