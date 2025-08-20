#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fixtures for providing Meteocat lightning CSV test data.

This module loads a zipped CSV file containing lightning data
and exposes a pytest fixture that yields a slice of rows
for use in test cases.
"""
import pytest
import zipfile
import csv
import io

from pathlib import Path
from sqlalchemy.orm import Session

def create_lightnings():
    """
    Load all lightning CSV rows from a zipped archive.

    This helper function extracts the CSV file
    `DATMET-12706_cg_cm_2016.csv` from the archive
    `DATMET-12706_cg_cm_2016.zip` and returns all rows.

    Returns
    -------
    list of list of str
        A list of CSV rows, where each row is represented as
        a list of strings.
    """
    archive_path: Path = Path(__file__).parent / 'DATMET-12706_cg_cm_2016.zip'
    csv_filename: str = 'DATMET-12706_cg_cm_2016.csv'

    with zipfile.ZipFile(archive_path, 'r') as archive:
        with archive.open(csv_filename, 'r') as file:
            text_file = io.TextIOWrapper(file)
            reader = csv.reader(text_file, delimiter=';')
            rows = list(reader)
            return rows


@pytest.fixture(scope='function')
def lightnings_csv_rows(db_session: Session):
    """
    Provide a slice of lightning CSV rows for testing.

    This fixture yields a subset of rows from the
    `DATMET-12706_cg_cm_2016.csv` file, loaded via
    :func:`create_lightnings`. It is intended to reduce
    memory usage and speed up test execution by only
    returning a fixed window of rows.

    Parameters
    ----------
    db_session : sqlalchemy.orm.Session
        Database session fixture. Included to ensure the
        database context is available in dependent tests,
        although not directly used.

    Yields
    ------
    list of list of str
        A slice of CSV rows (rows 10000–10999 inclusive),
        where each row is represented as a list of strings.
    """
    rows = create_lightnings()
    yield rows[10000:11000]