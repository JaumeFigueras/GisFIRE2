#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database initializer for default data providers.

This script connects to a PostgreSQL database and ensures that certain
default `DataProvider` records exist. Specifically, it checks for the
presence of:

- Meteo.cat (Servei Meteorològic de Catalunya)
- Bombers.cat (Bombers de la Generalitat de Catalunya)

If these providers are missing, the script inserts them into the database.

Usage
-----
Run the script directly with the required database connection arguments:

.. code-block:: bash

    python3 create_data_providers.py --host <DB_HOST> --port <DB_PORT> --database <DB_NAME> --username <DB_USER> --password <DB_PASSWORD>

Named Arguments
---------------
| :code:`-H, --host`: Hostname of the PostgreSQL database cluster.
| :code:`-p, --port`: Port number of the PostgreSQL database cluster.
| :code:`-d, --database`: Name of the target database.
| :code:`-u, --username`: Database username for authentication.
| :code:`-w, --password`: Password for authentication.

Raises
------
SQLAlchemyError
    If the database connection cannot be established.

Notes
-----
- The script commits changes only if new providers are added.
- Exits with a non-zero status code if the database connection fails.

Dependencies
------------
- SQLAlchemy for database connectivity and ORM functionality.
- A defined `DataProvider` ORM model located in
  `src.data_model.data_provider`.
"""  # noinspection GrammarInspection
import argparse
import sys

from sqlalchemy import create_engine
from sqlalchemy import select
from sqlalchemy import URL
from sqlalchemy import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.data_model.data_provider import DataProvider


def main(db_session: Session) -> None:
    """
    Ensure default data providers exist in the database.

    This function checks whether the `DataProvider` table contains
    specific entries ("Meteo.cat" and "Bombers.cat"). If they are missing,
    the function inserts them into the database and commits the changes.

    Parameters
    ----------
    db_session : sqlalchemy.orm.Session
        Active SQLAlchemy session connected to the target database.

    Returns
    -------
    None

    Notes
    -----
    - Only inserts records if they do not already exist.
    - Commits changes at the end of execution.
    - Intended to be used during database initialization or setup.
    """
    qty = db_session.scalar(select(func.count(DataProvider.data_provider_name)).where(DataProvider.data_provider_name == "Meteo.cat"))
    if qty == 0:
        meteo_cat = DataProvider(
            data_provider_name='Meteo.cat',
            data_provider_description='Servei Meteorològic de Catalunya',
            data_provider_url='https://www.meteo.cat/'
        )
        db_session.add(meteo_cat)
    qty = db_session.scalar(select(func.count(DataProvider.data_provider_name)).where(DataProvider.data_provider_name == "Bombers.cat"))
    if qty == 0:
        bombers_gencat = DataProvider(
            data_provider_name='Bombers.cat',
            data_provider_description='Bombers de la Generalitat de Catalunya',
            data_provider_url='https://interior.gencat.cat/ca/arees_dactuacio/bombers'
        )
        db_session.add(bombers_gencat)
    db_session.commit()


if __name__ == "__main__":  # pragma: no cover
    # Config the program arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-H', '--host', help='Host name were the database cluster is located', required=True)
    parser.add_argument('-p', '--port', type=int, help='Database cluster port', required=True)
    parser.add_argument('-d', '--database', help='Database name', required=True)
    parser.add_argument('-u', '--username', help='Database username', required=True)
    parser.add_argument('-w', '--password', help='Database password', required=True)
    args = parser.parse_args()

    database_url = URL.create('postgresql+psycopg', username=args.username, password=args.password, host=args.host,
                              port=args.port, database=args.database)

    try:
        engine: Engine = create_engine(database_url)
        session: Session = Session(engine)
    except SQLAlchemyError as ex:
        print(ex)
        sys.exit(-1)

    main(session)
