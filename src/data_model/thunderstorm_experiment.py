#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from src.data_model import Base
from src.data_model.mixins.time_stamp import TimeStampMixIn
from src.data_model.data_provider import DataProvider

from sqlalchemy import Integer
from sqlalchemy import Enum
from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy.dialects.postgresql import HSTORE
from enum import StrEnum

from sqlalchemy.orm import Mapped
from typing import Dict
from typing import Optional
from typing import List
from typing import Union
from typing import TypedDict
from typing import Unpack
from typing import NotRequired
from typing import Any

class ThunderstormExperimentAlgorithm(StrEnum):
    """
    Enumeration of algorithms used in thunderstorm experiments.

    This enum defines various strategies for analyzing thunderstorm data,
    including time-based, distance-based, and clustering approaches.

    Attributes
    ----------
    TIME : str
        Clustering algorithm that considers only temporal proximity of events.
    DISTANCE : str
        Clustering algorithm that considers only spatial proximity of events.
    TIME_DISTANCE : str
        Clustering algorithm that combines both temporal and spatial proximity.
    DBSCAN_TIME : str
        DBSCAN clustering algorithm applied using time as the feature.
    DBSCAN_TIME_DISTANCE : str
        DBSCAN clustering algorithm applied using both time and distance features.
    """
    TIME = "TIME"
    DISTANCE = "DISTANCE"
    TIME_DISTANCE = "TIME_DISTANCE"
    DBSCAN_TIME = "DBSCAN_TIME"
    DBSCAN_TIME_DISTANCE = "DBSCAN_TIME_DISTANCE"

class ThunderstormExperimentParams(TypedDict):
    """
    Typed dictionary for thunderstorm experiment configuration.

    This type defines the expected structure of keyword arguments
    used to initialize a :class:`ThunderstormExperiment` instance.

    Keys
    ----
    algorithm : ThunderstormExperimentAlgorithm
        The clustering algorithm applied in the experiment.
    parameters : dict of str, str
        A dictionary of configuration parameters for the algorithm,
        represented as key-value string pairs.

    Examples
    --------
    >>> from src.data_model.thunderstorm_experiment import (
    ...     ThunderstormExperiment,
    ...     ThunderstormExperimentAlgorithm,
    ...     ThunderstormExperimentParams
    ... )
    >>> params: ThunderstormExperimentParams = {
    ...     "algorithm": ThunderstormExperimentAlgorithm.TIME_DISTANCE,
    ...     "parameters": {"max_time_gap": "600", "max_distance": "10"}
    ... }
    >>> experiment = ThunderstormExperiment(**params)
    """
    thunderstorm_experiment_algorithm: ThunderstormExperimentAlgorithm
    thunderstorm_experiment_parameters: NotRequired[Dict[str, Any]]
    data_provider: Union[DataProvider, str]

class ThunderstormExperiment(Base, TimeStampMixIn):
    """
    Represents a thunderstorm experiment configuration and its associated data.

    This class models the metadata and relationships for a single thunderstorm
    experiment. Each experiment uses a specific clustering algorithm to
    analyze thunderstorm data and stores parameters relevant to the analysis.

    Attributes
    ----------
    thunderstorm_experiment_id : int
        Unique identifier for the experiment (primary key).
    thunderstorm_experiment_algorithm : :class:`~src.data_model.thunderstorm_experiment.ThunderstormExperimentAlgorithm`
        Clustering algorithm applied to the thunderstorm data.
    thunderstorm_experiment_parameters : dict of str, str
        Key-value pairs specifying configuration parameters for the experiment algorithm.
    thunderstorms : list of :class:`Thunderstorm`
        List of thunderstorm events associated with this experiment.

    See Also
    --------
    :class:`~src.data_model.thunderstorm_experiment.ThunderstormExperimentAlgorithm`
        Enum of available clustering algorithms used for analysis.
    :class:`~src.data_model.thunderstorm.Thunderstorm`
        Model representing individual thunderstorm records linked to an experiment.
    """
    # Metadata for SQLAlchemy
    __tablename__ = "thunderstorm_experiment"
    # Table columns
    thunderstorm_experiment_id: Mapped[int] = mapped_column('thunderstorm_experiment_id', Integer, primary_key=True, autoincrement=True)
    thunderstorm_experiment_algorithm: Mapped[ThunderstormExperimentAlgorithm] = mapped_column('thunderstorm_experiment_algorithm', Enum(ThunderstormExperimentAlgorithm, name="thunderstorm_experiment_algorithm_enum", native_enum=True))
    thunderstorm_experiment_parameters: Mapped[Optional[Dict[str, str]]] = mapped_column('thunderstorm_experiment_parameters', HSTORE, nullable=True)
    # Relations
    data_provider_name: Mapped[str] = mapped_column('data_provider_name', ForeignKey('data_provider.data_provider_name'), nullable=False)
    data_provider: Mapped["DataProvider"] = relationship(back_populates="thunderstorm_experiments")
    thunderstorms: Mapped[List["Thunderstorm"]] = relationship(back_populates="thunderstorm_experiment")

    def __init__(self, **kwargs: Unpack[ThunderstormExperimentParams]) -> None:
        """
        Initialize a ThunderstormExperiment instance with algorithm and parameters arguments.

        Parameters
        ----------
        algorithm : :class:`~src.data_model.thunderstorm_experiment.ThunderstormExperimentAlgorithm`
            Clustering algorithm to be applied during the experiment.
        parameters : dict of str, str
            Dictionary of configuration parameters relevant to the experiment algorithm.

        Notes
        -----
        This constructor sets up the base metadata for a thunderstorm experiment,
        including which algorithm is used to cluster thunderstorm data and any
        additional settings passed as key-value pairs.

        See Also
        --------
        :class:`~src.data_model.thunderstorm_experiment.ThunderstormExperimentAlgorithm`
            Enumeration of supported clustering strategies.
        :class:`~src.data_model.thunderstorm_experiment.ThunderstormExperiment`
            The enclosing experiment model class.
        """
        super().__init__()
        for key, value in kwargs.items():
            if hasattr(self, key):
                if key == "data_provider" and isinstance(value, str):
                    self.data_provider_name = value
                else:
                    setattr(self, key, value)