#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import pytz

from sqlalchemy.orm import Session

from src.meteocat.data_model.thunderstorm import MeteocatThunderstorm
from src.data_model.data_provider import DataProvider
from src.data_model.thunderstorm_experiment import ThunderstormExperiment
from src.data_model.thunderstorm_experiment import ThunderstormExperimentParams
from src.data_model.thunderstorm_experiment import ThunderstormExperimentAlgorithm
from src.meteocat.data_model.lightning import MeteocatLightning

from typing import List

def test_thunderstorm_number_of_lightnings(db_session: Session, data_provider: List[DataProvider]) -> None:
    experiment = ThunderstormExperiment(
        thunderstorm_experiment_algorithm=ThunderstormExperimentAlgorithm.TIME_DISTANCE,
        thunderstorm_experiment_parameters={"max_time_gap": "600", "max_distance": "10"},
        data_provider=data_provider[0],
    )
    db_session.add(experiment)
    lightnings: List[MeteocatLightning] = list()
    for i in range(4):
        lightning: MeteocatLightning = MeteocatLightning(
            x_4258=2.113066 + 0.01 * i,
            y_4258=41.388147 - 0.01 * i,
            lightning_utc_date_time=datetime.datetime(2025, 6, 24, 17, i, 0, tzinfo=pytz.UTC),
            data_provider=data_provider[1]
        )
        lightnings.append(lightning)
    db_session.add_all(lightnings)
    tstorm = MeteocatThunderstorm(
        thunderstorm_experiment=experiment,
    )
    db_session.add(tstorm)
    tstorm.lightnings = lightnings
    tstorm.on_lightnings_change()
    db_session.commit()
    assert tstorm.thunderstorm_number_of_lightnings == 4


