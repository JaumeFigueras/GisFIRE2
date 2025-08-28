#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pytest fixture module for creating sample `DataProvider` entries in the database.

This module provides a utility function and a pytest fixture for initializing
test data in the database. It is intended for use in functional or integration
tests that require sample `DataProvider` records.

Functions
---------
create_data_providers(session: Session) -> List[DataProvider]
    Creates and commits two sample `DataProvider` instances to the database.

Fixtures
--------
data_provider(db_session: Session)
    Pytest fixture that yields the sample `DataProvider` instances for use in tests.
    Cleans up the session after each test function.
"""

import pytest

from src.data_model.data_provider import DataProvider

from typing import List
from sqlalchemy.orm import Session

def create_data_providers(session: Session) -> List[DataProvider]:
    """
    Create and persist sample `DataProvider` records in the database.

    This function creates two sample data providers:

    1. 'Meteo.cat' - Servei Meteorològic de Catalunya
    2. 'Bombers.cat' - Bombers de la Generalitat de Catalunya

    Args:
        session (Session): SQLAlchemy session connected to the test database.

    Returns:
        List[DataProvider]: The list of created `DataProvider` instances.
    """
    dp1 = DataProvider(
        data_provider_name='Meteo.cat',
        data_provider_description='Servei Meteorològic de Catalunya',
        data_provider_url='https://www.meteo.cat/'
    )
    dp2 = DataProvider(
        data_provider_name='Bombers.cat',
        data_provider_description='Bombers de la Generalitat de Catalunya',
        data_provider_url='https://interior.gencat.cat/ca/arees_dactuacio/bombers'
    )
    session.add_all([dp1, dp2])
    session.commit()
    return [dp1, dp2]

@pytest.fixture(scope='function')
def data_provider(db_session: Session):
    """
    Pytest fixture that provides sample `DataProvider` instances for tests.

    This fixture:
    - Uses `create_data_providers` to insert sample records into the test database.
    - Yields the list of `DataProvider` objects to the test.
    - Commits the session after each test function.

    Args:
        db_session (Session): The SQLAlchemy session fixture for the test database.

    Yields:
        List[DataProvider]: The sample `DataProvider` instances.
    """
    yield create_data_providers(db_session)
    db_session.commit()

