#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQLAlchemy ORM model for Lightning events.

This module defines the `Lightning` class representing lightning occurrences
recorded by various data providers. It uses several mixins to provide common
functionality such as timestamps, geospatial location, and datetime handling.

Classes
-------
LightningParams : TypedDict
    Type hints for parameters accepted by the Lightning constructor.
Lightning : Base, LocationMixIn, DateTimeMixIn, TimeStampMixIn
    ORM-mapped class for lightning events, including relationships to
    data providers and polymorphic identity support.
"""

from __future__ import annotations  # Needed to allow returning type of enclosing class PEP 563

import datetime

from sqlalchemy import Integer
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from shapely.geometry import Point

from src.data_model import Base
from src.data_model.mixins.time_stamp import TimeStampMixIn
from src.data_model.mixins.location import LocationMixIn
from src.data_model.data_provider import DataProvider

from typing import Union
from typing import List
from typing import TypedDict
from typing_extensions import Unpack
from typing_extensions import NotRequired

class LightningParams(TypedDict):
    """
    TypedDict defining the accepted parameters for initializing a Lightning instance.

    Attributes
    ----------
    x_4326 : float, optional
        Longitude in EPSG:4326 coordinates.
    y_4326 : float, optional
        Latitude in EPSG:4326 coordinates.
    lightning_utc_date_time : datetime.datetime  # noinspection GrammarInspection
        Datetime of the lightning event.
    data_provider : DataProvider, optional
        The data provider that recorded the lightning event.
    """
    x_4326: NotRequired[float]
    y_4326: NotRequired[float]
    lightning_utc_date_time: datetime.datetime
    data_provider: Union[DataProvider, str]

class Lightning(Base, LocationMixIn, TimeStampMixIn):
    """
    ORM-mapped class representing a lightning event.

    This class combines several mixins to provide:
    - Geospatial location (LocationMixIn)
    - Datetime handling (DateTimeMixIn)
    - Automatic timestamping (TimeStampMixIn)

    Attributes
    ----------
    lightning_id : int
        Primary key for the lightning table.
    data_provider_name : str
        Foreign key linking to the DataProvider name.
    data_provider : DataProvider
        SQLAlchemy relationship to the DataProvider object.
    type : str
        Polymorphic type column to support inheritance.
    x_4326 : float
        Longitude in EPSG:4326 coordinates (from LocationMixIn).
    y_4326 : float
        Latitude in EPSG:4326 coordinates (from LocationMixIn).
    geometry_4326 : str or Point
        Geometric representation of the lightning location.
    lightning_utc_date_time : datetime.datetime  # noinspection GrammarInspection
        Datetime of the lightning event.
    tzinfo_date_time : str
        Timezone information for the event datetime.
    """
    # Metaclass location attributes
    __location__ = [
        {'epsg': 4326, 'validation': 'geographic', 'conversion': False, 'nullable': False}
    ]
    # Type hint for generated attributes by the metaclass
    x_4326: float
    y_4326: float
    geometry_4326: Union[str, Point]
    # Metaclass date_time attributes
    __date__ = [
        {'name': 'date_time', 'nullable': False}
    ]
    # SQLAlchemy columns
    __tablename__ = "lightning"
    lightning_id: Mapped[int] = mapped_column('lightning_id', Integer, primary_key=True, autoincrement=True)
    lightning_utc_date_time: Mapped[datetime.datetime] = mapped_column('lightning_utc_date_time', DateTime(timezone=True), nullable=False)
    # SQLAlchemy relations
    data_provider_name: Mapped[str] = mapped_column('data_provider_name', ForeignKey('data_provider.data_provider_name'), nullable=False)
    data_provider: Mapped["DataProvider"] = relationship(back_populates="lightnings")
    # many-to-many relationship to Parent, bypassing the `Association` class
    thunderstorms: Mapped[List["Thunderstorm"]] = relationship(secondary="thunderstorm_lightning_association", back_populates="lightnings")  # type: ignore
    # association between Child -> Association -> Parent
    thunderstorm_associations: Mapped[List["ThunderstormLightningAssociation"]] = relationship(back_populates="lightning", viewonly=True)  # type: ignore

    type: Mapped[str]
    __mapper_args__ = {
        "polymorphic_identity": "lightning",
        "polymorphic_on": "type",
    }

    def __init__(self, **kwargs: Unpack[LightningParams]) -> None:
        """
        Initialize a Lightning instance.

        Parameters
        ----------
        **kwargs : LightningParams
            Keyword arguments matching LightningParams TypedDict. Only attributes
            present in the class are set.

        Notes
        -----
        The constructor initializes the Base and TimeStampMixIn classes.
        """
        Base.__init__(self)
        TimeStampMixIn.__init__(self)
        for key, value in kwargs.items():
            if hasattr(self, key):
                if key == "data_provider" and isinstance(value, str):
                    self.data_provider_name = value
                else:
                    setattr(self, key, value)

    def __iter__(self):
        """
        Iterate over Lightning attributes.

        Yields
        ------
        tuple
            (attribute_name, value) pairs including id, data_provider_name,
            location, and datetime fields.
        """
        yield "lightning_id", self.lightning_id
        yield "lightning_utc_date_time", self.lightning_utc_date_time.strftime("%Y-%m-%dT%H:%M:%S.%f%z")
        yield "data_provider", self.data_provider.data_provider_name
        yield from LocationMixIn.__iter__(self)

