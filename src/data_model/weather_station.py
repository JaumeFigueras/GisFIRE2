#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from shapely.geometry import Point

from src.data_model import Base
from src.data_model.mixins.location import LocationMixIn
from src.data_model.mixins.time_stamp import TimeStampMixIn
from src.data_model.data_provider import DataProvider

from typing import Optional
from typing import Union
from typing import TypedDict
from typing import NotRequired
from typing import Unpack
from typing import Iterator
from typing import Tuple
from typing import Any

class WeatherStationParams(TypedDict):
    """Typed dictionary specifying the parameters for initializing a WeatherStation.

    Attributes
    ----------
    weather_station_name : str
        Name of the weather station.
    weather_station_altitude : float, optional
        Altitude of the weather station in meters. If not provided, defaults to ``None``.
    x_4326 : float, optional
        Longitude in EPSG:4326 coordinate system.
    y_4326 : float, optional
        Latitude in EPSG:4326 coordinate system.
    data_provider : DataProvider or str
        Either a `DataProvider` instance or the name of the data provider to
        associate with this weather station.
    """
    weather_station_name: str
    weather_station_altitude: NotRequired[float]
    x_4326: NotRequired[float]
    y_4326: NotRequired[float]
    data_provider: Union[DataProvider, str]

class WeatherStation(Base, LocationMixIn, TimeStampMixIn):
    """SQLAlchemy model representing a weather station entity.

    This model includes metadata for geographic location, optional altitude,
    and an association with a data provider. It also supports polymorphic
    inheritance.

    Attributes
    ----------
    __location__ : list of dict
        Metadata describing location attributes handled by `LocationMixIn`.
    x_4326 : float
        Longitude of the weather station (EPSG:4326).
    y_4326 : float
        Latitude of the weather station (EPSG:4326).
    geometry_4326 : str or Point
        Geometry representation of the weather station location.
    weather_station_id : int
        Primary key of the weather station.
    weather_station_name : str
        Name of the weather station.
    weather_station_altitude : float or None
        Altitude of the weather station in meters.
    data_provider_name : str
        Foreign key reference to the associated data provider.
    data_provider : DataProvider
        Relationship to the associated `DataProvider` object.
    type : str
        Column used by SQLAlchemy to handle polymorphic inheritance.
    """
    # Metaclass location attributes
    __location__ = [
        {'epsg': 4326, 'validation': 'geographic', 'conversion': False, 'nullable': False}
    ]
    # Type hint fot generated attributes by the metaclass
    x_4326: float
    y_4326: float
    geometry_4326: Union[str, Point]
    # SQLAlchemy columns
    __tablename__ = "weather_station"
    weather_station_id: Mapped[int] = mapped_column('weather_station_id', Integer, primary_key=True, autoincrement=True)
    weather_station_name: Mapped[str] = mapped_column('weather_station_name', String, nullable=False)
    weather_station_altitude: Mapped[Optional[float]] = mapped_column('weather_station_altitude', Float, nullable=True)
    # SQLAlchemy relations
    data_provider_name: Mapped[str] = mapped_column('data_provider_name', ForeignKey('data_provider.data_provider_name'), nullable=False)
    data_provider: Mapped["DataProvider"] = relationship(back_populates="weather_stations")
    # SQLAlchemy Inheritance options
    type: Mapped[str]
    __mapper_args__ = {
        "polymorphic_identity": "weather_station",
        "polymorphic_on": "type",
    }

    def __init__(self, **kwargs: Unpack[WeatherStationParams]) -> None:
        """Initialize a WeatherStation instance.

        Parameters
        ----------
        **kwargs : Unpack[WeatherStationParams]
            Keyword arguments matching the `WeatherStationParams` TypedDict.
            If `data_provider` is given as a string, it is stored in
            `data_provider_name`. If a `DataProvider` object is provided,
            it is assigned directly to the `data_provider` relationship.
        """
        super().__init__()
        for key, value in kwargs.items():
            if hasattr(self, key):
                if key == "data_provider" and isinstance(value, str):
                    self.data_provider_name = value
                else:
                    setattr(self, key, value)

    def __iter__(self) -> Iterator[Tuple[str, Any]]:
        """Iterate over the weather station attributes as key-value pairs.

        Yields
        ------
        tuple of (str, Any)
            Pairs representing the attribute name and its value. Includes:

            - ``("weather_station_id", int)``
            - ``("weather_station_name", str)``
            - ``("weather_station_altitude", float or None)``
            - ``("data_provider_name", str)``
            - Location attributes yielded by `LocationMixIn.__iter__`
        """
        yield 'weather_station_id', self.weather_station_id
        yield 'weather_station_name', self.weather_station_name
        yield 'weather_station_altitude', self.weather_station_altitude
        yield 'data_provider_name', self.data_provider_name
        yield from LocationMixIn.__iter__(self)
