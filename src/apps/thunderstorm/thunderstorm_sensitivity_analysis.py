#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import dateutil.parser
import datetime
import pytz
import logging
import sys
import multiprocessing as mp
import time

from logging.handlers import RotatingFileHandler

from sqlalchemy import create_engine
from sqlalchemy import URL
from sqlalchemy import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.apps.thunderstorm.generate_thunderstorms import time_distance_algorithm

from typing import Dict
from typing import List
from typing import Any

def init_pool(lock_instance, logger_instance, db_engine_instance, process_id_instance):
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
    global db_engine
    global process_id
    lock = lock_instance
    logger = logger_instance
    db_engine = db_engine_instance
    process_id = process_id_instance

def process_configuration(configuration: Dict[str, Any]):
    with lock:
        my_id = process_id[0]
        process_id[0] += 1
        logger.info(f"Process: {my_id} - Processing analysis with configuration: {configuration}")
        engine: Engine = create_engine(db_engine[0], pool_size=30)
    time_distance_algorithm(
        engine,
        configuration["from_date"],
        configuration["to_date"],
        configuration["distance"],
        configuration["time"],
        configuration["gap"],
        configuration["data_provider"],
        logger,
        my_id
    )
    start_time = time.time()
    with lock:
        logger.info("Process: {} - Finished processing in {} seconds".format(my_id, time.time() - start_time))

if __name__ == "__main__":  # pragma: no cover
    # Config the program arguments
    # noinspection DuplicatedCode
    parser = argparse.ArgumentParser()
    parser.add_argument('-H', '--host', help='Host name were the database cluster is located', required=True)
    parser.add_argument('-p', '--port', type=int, help='Database cluster port', required=True)
    parser.add_argument('-d', '--database', help='Database name', required=True)
    parser.add_argument('-u', '--username', help='Database username', required=True)
    parser.add_argument('-w', '--password', help='Database password', required=True)
    parser.add_argument('-t', '--data-provider', help='Data provider name', required=True)
    parser.add_argument('-f', '--from-date', help='Initial date of storm clustering', required=False, type=dateutil.parser.isoparse, default=datetime.datetime(year=2006, month=1, day=1, hour=0, minute=0, second=0, tzinfo=pytz.UTC))
    parser.add_argument('-e', '--end-date', help='End date of storm clustering', required=False, type=dateutil.parser.isoparse, default=datetime.datetime(year=2021, month=1, day=1, hour=0, minute=0, second=1, tzinfo=pytz.UTC))
    parser.add_argument('-a', '--algorithm', help='Algorithm used for clustering (TIME, TIME-DISTANCE, DBSCAN-D, DBSCAN-TD)', required=True, choices=['TIME', 'TIME-DISTANCE', 'DBSCAN-T', 'DBSCAN-D', 'DBSCAN-TD'])
    parser.add_argument('-s', '--lightning-gap', help='Maximum gap between lightnings (in seconds)', required=False, type=float)
    parser.add_argument('-l', '--log-file', help='File to log progress or errors', required=False)
    args = parser.parse_args()

    logger = logging.getLogger(__name__)
    if args.log_file is not None:
        handler = RotatingFileHandler(args.log_file, mode='a', maxBytes=5*1024*1024, backupCount=15, encoding='utf-8', delay=False)
        logging.basicConfig(format='%(asctime)s.%(msecs)03d [%(levelname)s] %(message)s', handlers=[handler], encoding='utf-8', level=logging.DEBUG, datefmt="%Y-%m-%d %H:%M:%S")
    else:
        handler = ch = logging.StreamHandler()
        logging.basicConfig(format='%(asctime)s.%(msecs)03d [%(levelname)s] %(message)s', handlers=[handler], encoding='utf-8', level=logging.DEBUG, datefmt="%Y-%m-%d %H:%M:%S")

    # Process the CSV file and store it into the database
    logger.info("Connecting to database")
    database_url: URL = URL.create('postgresql+psycopg', username=args.username, password=args.password, host=args.host,
                                   port=args.port, database=args.database)
    try:
        engine: Engine = create_engine(database_url, pool_size=30)
    except SQLAlchemyError as ex:
        logger.error("Can't connect to database")
        logger.error("Exception: {}".format(str(ex)))
        sys.exit(-1)

    args.from_date.replace(tzinfo=pytz.UTC)
    args.end_date.replace(tzinfo=pytz.UTC)

    distances = [x * 1000 for x in [5, 10, 15, 20, 25]]
    times = [x * 60 for x in [10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30]]

    logger.info("Starting processing all lightnings in parallel")
    chunks: List[Dict[str, Any]] = list()
    for d in distances:
        for t in times:
            if args.algorithm == 'TIME-DISTANCE':
                chunks.append({
                    "from_date": args.from_date,
                    "to_date": args.end_date,
                    "distance": d,
                    "time": t,
                    "gap": args.lightning_gap,
                    "data_provider": args.data_provider
                })
    mg = mp.Manager()
    lock = mg.Lock()
    db_engine = mg.list()
    db_engine.append(database_url)
    process_id = mg.list()
    process_id.append(0)
    pool = mp.Pool(mp.cpu_count() - 2, initializer=init_pool, initargs=(lock, logger, db_engine, process_id))
    pool.map(func=process_configuration, iterable=chunks)
    pool.close()
    pool.join()
    logger.info("Finished processing all lightnings in parallel")


    # for d in distances:
    #     for t in times:
    #         if args.algorithm == 'TIME-DISTANCE':
    #             logger.info(f"{args.algorithm} sensitivity analysis for d={d}, t={t} started")
    #             time_distance_algorithm(session, args.from_date, args.to_date, d, t, args.lightning_gap, args.data_provider, logger)
    #             logger.info(f"{args.algorithm} sensitivity analysis for d={d}, t={t} finished")
