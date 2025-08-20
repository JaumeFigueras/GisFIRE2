#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parallel lightning data importer for Meteo.cat.

This script reads lightning strike data from a CSV file provided by
Meteo.cat, processes the data in parallel, validates it, and inserts it
into a PostgreSQL database using SQLAlchemy. It also populates
equivalent request logs for the imported year.

Features
--------
- Reads lightning data from a semicolon-delimited CSV file.
- Processes rows in parallel using multiprocessing.
- Converts rows into `MeteocatLightning` ORM objects.
- Validates input records, logging errors if found.
- Inserts valid records into the database in bulk.
- Populates `APIRequestLog` entries simulating hourly Meteo.cat requests.

Usage
-----

Run the script directly with the required arguments:

.. code-block:: bash

   python3 import_lightnings_from_csv_mp.py --host <DB_HOST> --port <DB_PORT> --database <DB_NAME> --username <DB_USER> --password <DB_PASS> --file <CSV_FILE> [--log-file <LOG_FILE>]

Named Arguments
---------------

| ``-H, --host``: Host name where the database cluster is located.
| ``-p, --port``: Database cluster port.
| ``-d, --database``: Database name.
| ``-u, --username``: Database username.
| ``-w, --password``: Database password.
| ``-f, --file``: CSV file containing lightning strike records.
| ``-l, --log-file``: File to log progress or errors. Defaults to console logging.

Dependencies
------------

- SQLAlchemy for ORM and database connectivity.
- `MeteocatLightning` ORM model (`src.meteocat.data_model.lightning`).
- `APIRequestLog` ORM model (`src.data_model.api_request_log`).
- Python `multiprocessing` for parallel processing.

Notes
-----

- CSV is expected to have a header and use `;` as the delimiter.
- Data chunks of 10,000 records are processed in parallel.
- All records must be valid `MeteocatLightning` objects before insertion.
- The script exits with a non-zero status on error.
"""

import time
import multiprocessing as mp
import datetime
import pytz
import argparse
import csv
import sys
import logging

from sqlalchemy import URL
from sqlalchemy import Engine
from sqlalchemy import create_engine
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy import and_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from logging.handlers import RotatingFileHandler

from src.meteocat.data_model.lightning import MeteocatLightning
from src.data_model.api_request_log import APIRequestLog
from src.meteocat.remote_api.lightnings import URL as URL_LIGHTNINGS

from typing import TextIO
from typing import Any
from typing import List

def init_pool(lock_instance, logger_instance, shared_result_list_instance, process_id_instance):
    """
    Initialize multiprocessing pool worker context.

    This function sets global variables in each worker process to share
    resources such as a multiprocessing lock, a logger, and a shared list.

    Parameters
    ----------
    lock_instance : multiprocessing.synchronize.Lock
        Multiprocessing lock to synchronize logging and shared list access.
    logger_instance : logging.Logger  # noinspection GrammarInspection
        Logger to be used by worker processes.
    shared_result_list_instance : multiprocessing.managers.ListProxy
        Shared list proxy for storing processed lightning results.
    process_id_instance : multiprocessing.managers.ListProxy
        Shared list proxy containing the current process ID counter.

    Returns
    -------
    None
    """
    global lock
    global logger
    global shared_result_list
    global process_id
    lock = lock_instance
    logger = logger_instance
    shared_result_list = shared_result_list_instance
    process_id = process_id_instance


def process_lightnings(rows: List[Any]):
    """
    Process a chunk of CSV lightning rows into ORM objects.

    Converts raw CSV rows into `MeteocatLightning` objects. Invalid rows
    are recorded as error messages. Results are appended to a shared list
    accessible across worker processes.

    Parameters
    ----------
    rows : list of list
        List of CSV row values, where each row represents a lightning
        strike record.

    Returns
    -------
    None

    Notes
    -----
    - Uses global shared objects (`lock`, `logger`, `shared_result_list`,
      `process_id`) initialized via `init_pool`.
    - Appends either a list of `MeteocatLightning` objects or error
      messages to the shared result list.
    """
    with lock:
        my_id = process_id[0]
        process_id[0] += 1
        logger.info("Process: {} - Processing lightning chunk of: {} lightnings".format(my_id, len(rows)))
    start_time = time.time()
    lightnings: List[Any] = list()
    for row in rows:
        try:
            lightning: MeteocatLightning = MeteocatLightning(
                meteocat_id=int(row[0]),
                date_time=datetime.datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S.%f').replace(tzinfo=pytz.UTC),
                peak_current=float(row[2]),
                chi_squared=float(row[3]),
                ellipse_major_axis=float(row[4]),
                ellipse_minor_axis=float(row[5]),
                ellipse_angle=0.0,
                number_of_sensors=int(row[6]),
                hit_ground=row[7] == 't',
                municipality_code=row[8] if row[8] != '' else None,
                x_4258=float(row[9]),
                y_4258=float(row[10]),
                data_provider='Meteo.cat'
            )
            lightnings.append(lightning)
        except ValueError as e:
            lightnings.append("Error found in record {0:}. Rolling back all changes. Exception text: {1:}".format(row[0], str(e)))
    with lock:
        shared_result_list.append(lightnings)
        logger.info("Process: {} - Finished processing in {} seconds".format(my_id, time.time() - start_time))


def process_requests(db_session, year):
    """
    Insert simulated Meteo.cat request logs for a given year.

    For each hour in the given year, creates an `APIRequestLog` entry
    with a simulated endpoint corresponding to Meteo.cat's lightning
    data service.

    Parameters
    ----------
    db_session : sqlalchemy.orm.Session
        Active SQLAlchemy session connected to the target database.
    year : int
        Year for which to generate equivalent request logs.

    Returns
    -------
    None

    Raises
    ------
    SQLAlchemyError
        If database operations fail, rolls back the transaction and re-raises.
    """
    logger.info("Starting population of equivalent requests to Meteo.cat")
    date = datetime.datetime(year, 1, 1, 0, 0, 0, tzinfo=pytz.UTC)
    i = 0
    try:
        while date.year == year:
            endpoint = URL_LIGHTNINGS.format(year=date.year, month=date.month, day=date.day, hour=date.hour)
            if db_session.scalar(select(func.count(APIRequestLog.id)).where(
                and_(APIRequestLog.endpoint == endpoint, APIRequestLog.http_status == 200, APIRequestLog.data_provider_name == 'Meteo.cat')
            )):
                logger.error(f"Error found in record {i}. Rolling back all changes")
                db_session.rollback()
                raise ValueError("Duplicated request.")
            simulated_request = APIRequestLog(endpoint=endpoint, http_status=200, data_provider='Meteo.cat')
            date = date + datetime.timedelta(hours=1)
            db_session.add(simulated_request)
            if i % 24 == 0:
                logger.info("Processing day: {0:}".format(date.strftime("%Y-%m-%d")))
            i += 1
        db_session.commit()
    except SQLAlchemyError as e:  # pragma: no cover
        logger.error("Error found in record {0:}. Rolling back all changes. Exception text: {1:}".format(i, str(e)))
        db_session.rollback()
        raise e


if __name__ == "__main__":  # pragma: no cover
    # Config the program arguments
    # noinspection DuplicatedCode
    parser = argparse.ArgumentParser()
    parser.add_argument('-H', '--host', help='Host name were the database cluster is located', required=True)
    parser.add_argument('-p', '--port', type=int, help='Database cluster port', required=True)
    parser.add_argument('-d', '--database', help='Database name', required=True)
    parser.add_argument('-u', '--username', help='Database username', required=True)
    parser.add_argument('-w', '--password', help='Database password', required=True)
    parser.add_argument('-f', '--file', help='File to retrieve data from', required=True)
    parser.add_argument('-l', '--log-file', help='File to log progress or errors', required=False)
    args = parser.parse_args()

    # Set up the Logger
    logger = logging.getLogger(__name__)
    if args.log_file is not None:
        handler = RotatingFileHandler(args.log_file, mode='a', maxBytes=5*1024*1024, backupCount=15, encoding='utf-8', delay=False)
        logging.basicConfig(format='%(asctime)s.%(msecs)03d [%(levelname)s] %(message)s', handlers=[handler], encoding='utf-8', level=logging.DEBUG, datefmt="%Y-%m-%d %H:%M:%S")
    else:
        handler = ch = logging.StreamHandler()
        logging.basicConfig(format='%(asctime)s.%(msecs)03d [%(levelname)s] %(message)s', handlers=[handler], encoding='utf-8', level=logging.DEBUG, datefmt="%Y-%m-%d %H:%M:%S")

    # Set up the CSV file
    logger.info("Starting read CSV File: {}".format(args.file))
    try:
        csv_file: TextIO = open(args.file)
        reader = csv.reader(csv_file, delimiter=';')
    except Exception as ex:
        logger.error("Error opening CSV file: {0:}".format(ex))
        sys.exit(-1)
    # Create the CSV rows to process
    csv_rows = list(reader)[1:]
    logger.info("Finished read CSV File with {} records".format(len(csv_rows)))
    # Create the chunks to process in parallel
    logger.info("Starting processing all lightnings in parallel")
    chunks = [csv_rows[i:i + 10000] for i in range(0, len(csv_rows), 10000)]
    mg = mp.Manager()
    lock = mg.Lock()
    shared_result_list = mg.list()
    process_id = mg.list()
    process_id.append(0)
    pool = mp.Pool(mp.cpu_count() - 1, initializer=init_pool, initargs=(lock, logger, shared_result_list, process_id))
    pool.map(func=process_lightnings, iterable=chunks)
    pool.close()
    pool.join()
    logger.info("Finished processing all lightnings in parallel")

    # Start preparing lightnings to process in database
    logger.info("Starting joining all lightnings ({0:} chunk results)".format(len(shared_result_list)))
    processed_lightnings = list()
    for item in shared_result_list:
        processed_lightnings += item
    # Check there are no errors
    for lightning in processed_lightnings:
        if not isinstance(lightning, MeteocatLightning):
            logger.info("Found error while testing all lightnings")
            logger.info("Error: {}".format(lightning))
            sys.exit(-1)
    logger.info("Finished joining all lightnings with a resulting list of: {} lightnings to store in the database".format(len(processed_lightnings)))

    # Create the database URL
    database_url: URL = URL.create('postgresql+psycopg', username=args.username, password=args.password, host=args.host,
                                   port=args.port, database=args.database)
    # Connect to the database
    try:
        engine: Engine = create_engine(database_url)
        session: Session = Session(engine)
    except SQLAlchemyError as ex:
        print(ex)
        sys.exit(-1)
    logger.info("Starting insert to the database")
    session.add_all(processed_lightnings)
    session.commit()
    logger.info("Finished insert to the database")

    # Set up requests equivalents
    process_requests(session, processed_lightnings[0].date_time.year)


