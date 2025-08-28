#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import dateutil.parser
import datetime
import pytz
import logging
import sys
import math

from logging.handlers import RotatingFileHandler

from numpy.f2py.crackfortran import previous_context
from sqlalchemy import create_engine
from sqlalchemy import URL
from sqlalchemy import Engine
from sqlalchemy import select
from sqlalchemy import func
from sqlalchemy import and_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.meteocat.data_model.lightning import MeteocatLightning
from src.data_model.thunderstorm_experiment import ThunderstormExperiment
from src.data_model.thunderstorm_experiment import ThunderstormExperimentAlgorithm
from src.meteocat.data_model.thunderstorm import MeteocatThunderstorm

from logging import Logger
from typing import List
from typing import Optional
from typing import Dict

def time_algorithm(session: Session, from_date: datetime.datetime, to_date: datetime.datetime, algorithm_time: float, data_provider: str, logger: Logger) -> None:
    alg_params = {"time": str(algorithm_time)}
    count = session.scalar(select(func.count(ThunderstormExperiment.thunderstorm_experiment_id)).where(and_(ThunderstormExperiment.thunderstorm_experiment_algorithm == ThunderstormExperimentAlgorithm.TIME, ThunderstormExperiment.thunderstorm_experiment_parameters == alg_params, ThunderstormExperiment.data_provider_name == data_provider)))
    if count > 0:
        logger.error(f"Experiment with: {data_provider} and algorithm: TIME and parameters: {alg_params} already exists")
        return
    experiment = ThunderstormExperiment(
        thunderstorm_experiment_algorithm=ThunderstormExperimentAlgorithm.TIME,
        thunderstorm_experiment_parameters=alg_params,
        data_provider=data_provider,
    )
    session.add(experiment)
    session.commit()
    previous_lightning: Union[MeteocatLightning, None] = None
    storm = MeteocatThunderstorm(thunderstorm_experiment=experiment)
    storm.lightnings = list()
    stmt = select(MeteocatLightning).where(and_(MeteocatLightning.lightning_utc_date_time >= from_date, MeteocatLightning.lightning_utc_date_time < to_date)).order_by(MeteocatLightning.lightning_utc_date_time).execution_options(yield_per=1)
    for current_lightning in session.scalars(stmt):
        if (previous_lightning is not None) and (current_lightning.lightning_utc_date_time - previous_lightning.lightning_utc_date_time).total_seconds() > algorithm_time:
            storm.on_lightnings_change()
            session.add(storm)
            print(len(storm.lightnings), storm.lightnings[0].lightning_utc_date_time, storm.lightnings[-1].lightning_utc_date_time)
            storm = MeteocatThunderstorm(thunderstorm_experiment=experiment)
            storm.lightnings = [current_lightning]
        else:
            storm.lightnings.append(current_lightning)
        previous_lightning = current_lightning
    storm.on_lightnings_change()
    session.add(storm)
    session.commit()

def create_thunderstorm_experiment(engine: Engine, experiment_params: Dict[str, str], experiment_type: ThunderstormExperimentAlgorithm, data_provider_name: str, process_id: int) -> Optional[int]:
    with Session(engine) as session:
        count = session.scalar(
            select(
                func.count(
                    ThunderstormExperiment.thunderstorm_experiment_id
                )
            ).where(
                and_(
                    ThunderstormExperiment.thunderstorm_experiment_algorithm == experiment_type,
                    ThunderstormExperiment.thunderstorm_experiment_parameters == experiment_params,
                    ThunderstormExperiment.data_provider_name == data_provider_name
                )
            )
        )
        if count > 0:
            logger.error(f"{process_id}: Experiment with: {data_provider_name} and algorithm: TIME and parameters: {experiment_params} already exists")
            return None
        experiment = ThunderstormExperiment(
            thunderstorm_experiment_algorithm=ThunderstormExperimentAlgorithm.TIME_DISTANCE,
            thunderstorm_experiment_parameters=experiment_params,
            data_provider=data_provider_name,
        )
        session.add(experiment)
        session.commit()
        return experiment.thunderstorm_experiment_id

def find_lightning_cluster(session: Session, from_date: datetime.datetime, to_date: datetime.datetime, gap: float) -> Optional[List[MeteocatLightning]]:
    lightnings: List[MeteocatLightning] = list()
    previous_lightning: Optional[MeteocatLightning] = None
    stmt = select(
        MeteocatLightning
    ).where(
        and_(
            MeteocatLightning.lightning_utc_date_time >= from_date,
            MeteocatLightning.lightning_utc_date_time < to_date
        )
    ).order_by(
        MeteocatLightning.lightning_utc_date_time
    ).execution_options(yield_per=1)
    for current_lightning in session.scalars(stmt):
        if (previous_lightning is None) or ((current_lightning.lightning_utc_date_time - previous_lightning.lightning_utc_date_time).total_seconds() <= gap):
            lightnings.append(current_lightning)
            previous_lightning = current_lightning
        else:
            return lightnings
    else:
        return lightnings if len(lightnings) > 0 else None

def process_cluster(lightnings: List[MeteocatLightning], distance: float, time: float, experiment_id: int, logger: Logger, process_id: int) -> List[MeteocatThunderstorm]:
    distance_squared = distance ** 2
    storms: List[MeteocatThunderstorm] = list()
    for j, lightning in enumerate(lightnings):
        found = False
        lightning_x, lightning_y = lightning.x_25831, lightning.y_25831
        for storm in storms:
            for lightning_in_storm in reversed(storm.lightnings):
                time_distance = (lightning.lightning_utc_date_time - lightning_in_storm.lightning_utc_date_time).total_seconds()
                if time_distance > time:
                    break
                storm_x, storm_y = lightning_in_storm.x_25831, lightning_in_storm.y_25831
                spatial_distance = (storm_x - lightning_x)**2 + (storm_y - lightning_y)**2
                if spatial_distance <= distance_squared:
                    storm.lightnings.append(lightning)
                    found = True
                    break
            if found:
                break
        else:
            s: MeteocatThunderstorm = MeteocatThunderstorm(thunderstorm_experiment=experiment_id)
            s.lightnings.append(lightning)
            storms.append(s)
        if j > 1 and j % 100 == 0:
            logger.info(f"{process_id}: Processed {j} lightnings in cluster checking with {len(storms)} storms")
    logger.info(f"{process_id}: Processed {len(lightnings)} lightnings in cluster and found {len(storms)} storms")
    for i, storm in enumerate(storms):
        storm.on_lightnings_change()
        if i > 1 and i % 100 == 0:
            logger.info(f"{process_id}: Processed {i} storms of {len(storms)}")
    logger.info(f"{process_id}: Processed {len(storms)} storms of {len(storms)}")
    return storms

def time_distance_algorithm(engine: Engine, from_date: datetime.datetime, to_date: datetime.datetime, algorithm_distance: float, algorithm_time: float, gap: float, data_provider_name: str, logger: Logger, process_id = 0) -> None:
    experiment_params = {"time": str(algorithm_time), "distance": str(algorithm_distance)}
    experiment_id = create_thunderstorm_experiment(engine, experiment_params, ThunderstormExperimentAlgorithm.TIME_DISTANCE, data_provider_name, process_id)
    if experiment_id is None:
        return

    while True:
        with Session(engine) as session:
            lightning_cluster = find_lightning_cluster(session, from_date, to_date, gap)
            if lightning_cluster is None:
                return
            from_date = lightning_cluster[-1].lightning_utc_date_time + datetime.timedelta(seconds=1)
            logger.info(f"Found lightning cluster of {len(lightning_cluster)} from {lightning_cluster[0].lightning_utc_date_time.strftime('%Y-%m-%d %H:%M:%S')} to {lightning_cluster[-1].lightning_utc_date_time.strftime('%Y-%m-%d %H:%M:%S')}")
            storms = process_cluster(lightning_cluster, algorithm_distance, algorithm_time, experiment_id, logger, process_id)
            session.add_all(storms)
            session.commit()

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
    parser.add_argument('-m', '--algorithm-time', help='Algorithm time parameter to consider a new storm (in seconds)', required=False, type=float, default=-1)
    parser.add_argument('-c', '--algorithm-distance', help='Algorithm distance parameter to consider a new storm (in meters)', required=False, type=float, default=-1)
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
    logger.info("Processing ignitions from 2009 to 2019")
    logger.info("Connecting to database")
    database_url: URL = URL.create('postgresql+psycopg', username=args.username, password=args.password, host=args.host,
                                   port=args.port, database=args.database)
    try:
        engine: Engine = create_engine(database_url)
        session: Session = Session(engine)
    except SQLAlchemyError as ex:
        logger.error("Can't connect to database")
        logger.error("Exception: {}".format(str(ex)))
        sys.exit(-1)

    args.from_date.replace(tzinfo=pytz.UTC)
    args.end_date.replace(tzinfo=pytz.UTC)

    if args.algorithm == 'TIME':
        time_algorithm(session, args.from_date, args.end_date, args.algorithm_time, args.data_provider, logger)
    if args.algorithm == 'TIME-DISTANCE':
        time_distance_algorithm(engine, args.from_date, args.end_date, args.algorithm_distance, args.algorithm_time, args.lightning_gap, args.data_provider, logger)
    elif args.algorithm == 'DBSCAN-D':
        dbscan_distance_algorithm(session, args.from_date, args.end_date, args.algorithm_time, args.algorithm_distance, args.storm_max_time, logger)
    elif args.algorithm == 'DBSCAN-TD':
        dbscan_time_distance_algorithm(session, args.from_date, args.end_date, args.algorithm_time, args.algorithm_distance, args.storm_max_time, logger)

    session.close()






