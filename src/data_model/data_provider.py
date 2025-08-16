#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations  # Needed to allow returning type of enclosing class PEP 563

import datetime

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from src.data_model import Base
from src.data_model.mixins.time_stamp import TimeStampMixIn

from typing import List
from typing import TypedDict
from typing_extensions import NotRequired
from typing_extensions import Unpack


class DataProviderParams(TypedDict):
    """
    Typed dictionary for `DataProvider` initialization parameters.

    Parameters
    ----------
    name : str
        Name of the data provider.
    description : str
        Description of the data provider.
    url : str, optional
        URL of the data provider's website or API.
    """
    name: str
    description: str
    url: NotRequired[str]

class DataProvider(Base, TimeStampMixIn):
    """
    SQLAlchemy ORM model representing a data provider in the GisFIRE
    system.

    This class stores metadata about data providers, including their
    name, description, optional URL, and a timestamp of creation through the
    TimeStamp mixin. It also maintains relationships to associated lightning
    records.

    Attributes
    ----------
    __tablename__ : str
        Name of the database table for this model (`data_provider`).
    name : Mapped[str]
        Primary key. The unique name of the data provider.
    description : Mapped[str]
        A description of the data provider.
    url : Mapped[str]
        Optional URL for the data provider.
    ts : Mapped[datetime.datetime]
        Timestamp of creation, automatically set by the database.
    lightnings : Mapped[List["Lightning"]]
        Relationship to associated `Lightning` records.
    """
    # Table metadata
    __tablename__ = 'data_provider'
    # Columns
    name: Mapped[str] = mapped_column('name', primary_key=True)
    description: Mapped[str] = mapped_column('description')
    url: Mapped[str] = mapped_column('url')
    # Relations
    # lightnings: Mapped[List["Lightning"]] = relationship(back_populates="data_provider")


    def __init__(self, **kwargs: Unpack[DataProviderParams]) -> None:
        """
        Initialize a `DataProvider` instance.

        Parameters
        ----------
        **kwargs : Unpack[DataProviderParams]
            Keyword arguments matching the `DataProviderParams` typed
            dictionary. Unrecognized keys are ignored.

        Examples
        --------
        >>> DataProvider(
        ...     name="NOAA",
        ...     description="US National Weather Service",
        ...     url="https://www.weather.gov"
        ... )
        <DataProvider(name='NOAA')>
        """
        super().__init__()
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
