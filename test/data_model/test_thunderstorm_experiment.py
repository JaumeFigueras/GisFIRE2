#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for the ThunderstormExperiment data model.

This module contains tests that validate the behavior of the
`ThunderstormExperiment` class and its handling of initialization
parameters. The tests ensure that algorithm assignment, parameter
validation, and exclusion of unknown fields are working as intended.
"""
from src.data_model.data_provider import DataProvider
from src.data_model.thunderstorm_experiment import ThunderstormExperiment
from src.data_model.thunderstorm_experiment import ThunderstormExperimentAlgorithm

from sqlalchemy.orm import Session
from typing import List

def test_thunderstorm_experiment_00(db_session: Session, data_provider: List[DataProvider]):
    """
    Test initialization with TIME_DISTANCE algorithm and parameters.

    Ensures that when the `ThunderstormExperiment` is initialized
    with the TIME_DISTANCE algorithm and a parameter dictionary,
    both fields are correctly assigned.

    Parameters
    ----------
    db_session : Session
        Database session fixture (not directly used in this test).
    """
    experiment = ThunderstormExperiment(
        thunderstorm_experiment_algorithm=ThunderstormExperimentAlgorithm.TIME_DISTANCE,
        thunderstorm_experiment_parameters={"max_time_gap": "600", "max_distance": "10"},
        data_provider=data_provider[0],
    )
    assert experiment.thunderstorm_experiment_algorithm == ThunderstormExperimentAlgorithm.TIME_DISTANCE
    assert experiment.thunderstorm_experiment_parameters == {"max_time_gap": "600", "max_distance": "10"}
    assert experiment.data_provider == data_provider[0]


def test_thunderstorm_experiment_01(db_session: Session, data_provider: List[DataProvider]):
    """
    Test initialization with TIME algorithm without parameters.

    Ensures that when the `ThunderstormExperiment` is initialized
    with the TIME algorithm and no parameters, the `parameters`
    field remains unset (None).

    Parameters
    ----------
    db_session : Session
        Database session fixture (not directly used in this test).
    """
    experiment = ThunderstormExperiment(
        thunderstorm_experiment_algorithm=ThunderstormExperimentAlgorithm.TIME_DISTANCE,
        data_provider=data_provider[0],
    )
    db_session.add(experiment)
    db_session.commit()
    assert experiment.thunderstorm_experiment_algorithm == ThunderstormExperimentAlgorithm.TIME_DISTANCE
    assert experiment.data_provider_name == data_provider[0].data_provider_name
    assert experiment.data_provider == data_provider[0]
    assert experiment.thunderstorm_experiment_parameters is None

def test_thunderstorm_experiment_02(db_session: Session, data_provider: List[DataProvider]):
    """
    Test initialization with extra unrecognized fields.

    Ensures that when the `ThunderstormExperiment` is initialized
    with recognized fields (`algorithm`, `parameters`) and an
    unrecognized field, only the recognized fields are retained.

    Parameters
    ----------
    db_session : Session
        Database session fixture (not directly used in this test).
    """

    experiment = ThunderstormExperiment(
        thunderstorm_experiment_algorithm=ThunderstormExperimentAlgorithm.TIME_DISTANCE,
        thunderstorm_experiment_parameters={"max_time_gap": "600", "max_distance": "10"},
        data_provider=data_provider[0],
        extra_field="extra field"
    )
    db_session.add(experiment)
    db_session.commit()
    assert experiment.thunderstorm_experiment_algorithm == ThunderstormExperimentAlgorithm.TIME_DISTANCE
    assert experiment.thunderstorm_experiment_parameters == {"max_time_gap": "600", "max_distance": "10"}
    assert experiment.data_provider_name == data_provider[0].data_provider_name
    assert experiment.data_provider == data_provider[0]
    assert not hasattr(experiment, "extra_field")

def test_thunderstorm_experiment_03():
    """
    Test initialization without arguments.

    Ensures that when the `ThunderstormExperiment` is initialized
    without any arguments, both `algorithm` and `parameters` fields
    remain unset.

    """
    experiment = ThunderstormExperiment()
    assert getattr(experiment, "thunderstorm_experiment_algorithm", None) is None
    assert getattr(experiment, "thunderstorm_experiment_parameters", None) is None
    assert getattr(experiment, "data_provider", None) is None
    assert getattr(experiment, "data_provider_name", None) is None

