#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Utility script for inspecting and printing SQLAlchemy ORM table definitions.

This script connects to a PostgreSQL database using SQLAlchemy and prints
the SQL statements for creating ORM-mapped tables. It is primarily used for
debugging and verifying schema generation of the project's data models.

Usage
-----
Run from the command line with the required connection arguments:

.. code-block:: bash

    python3 get_sql.py --host localhost --port 5432 --database testdb --username user --password pass

Named Arguments
---------------
| :code:`-H, --host`: Hostname of the PostgreSQL database cluster.
| :code:`-p, --port`: Port number of the PostgreSQL database cluster.
| :code:`-d, --database`: Name of the target database.
| :code:`-u, --username`: Database username for authentication.
| :code:`-w, --password`: Password for authentication.

""" # noinspection GrammarInspection

import argparse  # pragma: no cover
import sys  # pragma: no cover

from sqlalchemy import create_engine  # pragma: no cover
from sqlalchemy import URL  # pragma: no cover
from sqlalchemy import Engine  # pragma: no cover
from sqlalchemy.exc import SQLAlchemyError  # pragma: no cover
from sqlalchemy.schema import CreateTable  # pragma: no cover

from src.data_model import Base  # pragma: no cover
from src.data_model.data_provider import DataProvider  # pragma: no cover
from src.data_model.lightning import Lightning  # pragma: no cover
from src.data_model.api_request_log import APIRequestLog  # pragma: no cover
from src.meteocat.data_model.lightning import MeteocatLightning  # pragma: no cover # noqa: F401
from src.data_model.thunderstorm import Thunderstorm  # pragma: no cover
from src.data_model.thunderstorm import ThunderstormLightningAssociation  # pragma: no cover
from src.data_model.thunderstorm_experiment import ThunderstormExperiment  # pragma: no cover
from src.meteocat.data_model.thunderstorm import MeteocatThunderstorm  # pragma: no cover # noqa: F401


def main(e: Engine):  # pragma: no cover
    """
    Print SQLAlchemy table metadata and CREATE TABLE statements.

    Parameters
    ----------
    e : Engine
        A SQLAlchemy Engine connected to the target PostgreSQL database.

    Notes
    -----
    - Prints the list of all registered tables from `Base.metadata`.
    - Prints the CREATE TABLE SQL for `DataProvider` and `Lightning` tables.
    - Additional tables may be enabled by uncommenting their respective lines.
    """
    print(Base.metadata.tables.keys())
    # Base.metadata.create_all(e)
    print(CreateTable(DataProvider.__table__).compile(e))
    print(CreateTable(Lightning.__table__).compile(e))
    print(CreateTable(APIRequestLog.__table__).compile(e))
    print(CreateTable(Thunderstorm.__table__).compile(e))
    print(CreateTable(ThunderstormLightningAssociation.__table__).compile(e))
    print(CreateTable(ThunderstormExperiment.__table__).compile(e))
    # print(CreateTable(MeteocatLightning.__table__).compile(e))

    # print(CreateTable(Request.__table__).compile(e))
    # print(CreateTable(User.__table__).compile(e))
    # print(CreateTable(UserAccess.__table__).compile(e))
    # print(CreateTable(WeatherStation.__table__).compile(e))
    # print(CreateTable(MeteocatWeatherStation.__table__).compile(e))
    # print(CreateTable(MeteocatWeatherStationState.__table__).compile(e))
    # print(CreateTable(Variable.__table__).compile(e))
    # print(CreateTable(MeteocatVariable.__table__).compile(e))
    # print(CreateTable(MeteocatVariableState.__table__).compile(e))
    # print(CreateTable(MeteocatVariableTimeBase.__table__).compile(e))
    # print(CreateTable(Measure.__table__).compile(e))
    # print(CreateTable(MeteocatMeasure.__table__).compile(e))
    # print(CreateTable(WildfireIgnition.__table__).compile(e))
    # print(CreateTable(BomberscatWildfireIgnition.__table__).compile(e))
    # print(CreateTable(Experiment.__table__).compile(e))


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
        engine = create_engine(database_url)
    except SQLAlchemyError as ex:
        print(ex)
        sys.exit(-1)

    main(engine)
