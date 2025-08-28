#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Pytest configuration for temporary PostgreSQL test database with SQLAlchemy.

This module provides fixtures and setup utilities for functional and
integration testing of a system using PostgreSQL and SQLAlchemy ORM.

Features
--------
- Creates a temporary PostgreSQL instance using `pytest_postgresql`.
- Initializes the database schema by executing SQL files.
- Provides a scoped SQLAlchemy session (`db_session`) for tests.
- Ensures proper cleanup after each test function by deleting table contents.

Intended Use
------------
- Functional or integration tests requiring a live PostgreSQL database.
- Tests that need isolated database environments to avoid affecting production data.

Fixtures
--------
db_session(postgresql_gisfire)
    Yields a SQLAlchemy scoped session connected to the temporary test database.
    Handles schema initialization and cleans up after each test function.

Notes
-----
- SQLAlchemy engine uses `NullPool` to avoid connection pooling issues in tests.
- Multiple SQL scripts are executed to initialize project-specific and third-party schemas.
- Additional pytest plugins can be loaded via `pytest_plugins`.
"""
# General imports
import tempfile
import pytest
import logging
# Specific imports
from pytest_postgresql import factories
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy.pool import NullPool
# Data model imports
from src.data_model import Base


test_folder: Path = Path(__file__).parent
socket_dir: tempfile.TemporaryDirectory = tempfile.TemporaryDirectory()
postgresql_proc_gisfire = factories.postgresql_proc(port=None, unixsocketdir=socket_dir.name, dbname='test')
postgresql_gisfire = factories.postgresql('postgresql_proc_gisfire')

@pytest.fixture(scope='function')
def db_session(postgresql_gisfire):
    """
    Provides a scoped SQLAlchemy session connected to a temporary PostgreSQL test database.

    This fixture:
    - Initializes the database schema using predefined SQL files.
    - Yields the session for use in tests.
    - Drops all tables and commits at the end of the test function scope.

    Args:
        postgresql_gisfire: The PostgreSQL test database provided by pytest_postgresql.

    Yields:
        session (scoped_session): SQLAlchemy session bound to the test database.
    """
    # Build PostgreSQL connection string
    connection = f'postgresql+psycopg://{postgresql_gisfire.info.user}:@{postgresql_gisfire.info.host}:{postgresql_gisfire.info.port}/{postgresql_gisfire.info.dbname}'
    # Create SQLAlchemy engine with no connection pool (safer for tests)
    engine = create_engine(connection, echo=False, poolclass=NullPool)
    session = scoped_session(sessionmaker(bind=engine))

    # List of SQL files to initialize the database schema
    sql_filenames = [
        str(test_folder) + '/database_init.sql',
        str(test_folder.parent) + '/src/data_model/database/data_provider.sql',
        str(test_folder.parent) + '/src/data_model/database/lightning.sql',
        str(test_folder.parent) + '/src/data_model/database/api_request_log.sql',
        str(test_folder.parent) + '/src/data_model/database/thunderstorm_experiment.sql',
        str(test_folder.parent) + '/src/data_model/database/thunderstorm.sql',
        str(test_folder.parent) + '/src/data_model/database/thunderstorm_lightning_association.sql',
    ]

    # Execute each SQL file to initialize the schema
    for sql_filename in sql_filenames:
        with open(sql_filename, 'r') as sql_file:
            sql = text(sql_file.read())
            session.execute(sql)
    yield session

    # Clean up: drop all tables and commit
    for tbl in reversed(Base.metadata.sorted_tables):
        tbl.delete()
    session.commit()

@pytest.fixture(scope="function")
def logger() -> logging.Logger:
    """
    Setups the logger configration and returns a configured logger for module 'test'. The fixture has a function scope

    :return: A configured logger for module 'test'
    :rtype: logging.Logger
    """
    logging.basicConfig(format='%(asctime)s.%(msecs)03d [%(levelname)s] %(message)s',
                        encoding='utf-8',
                        level=logging.INFO,
                        datefmt="%Y-%m-%d %H:%M:%S"
                        )
    return logging.getLogger('test')

# Optionally enable additional pytest fixture plugins
pytest_plugins = [
    'test.fixtures.data_model.data_provider',
    'test.fixtures.apps.mp',
    'test.fixtures.meteocat.data_model.lightnings',
]
