#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations  # Needed to allow returning type of enclosing class PEP 563

import enum
import datetime
import json

from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Enum
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from shapely.geometry import Point

from src.data_model import Base
from src.data_model.weather_station import WeatherStation
from src.data_model.weather_station import WeatherStationParams
from src.data_model.state import State
from src.data_model.state import StateParams

from typing import Union
from typing import Dict
from typing import Tuple
from typing import Any
from typing import List
from typing import Iterator
from typing import NotRequired
from typing import Unpack


class MeteocatWeatherStationCategory(enum.Enum):
    """
    Enum for Meteocat weather station types.

    Attributes
    ----------
    AUTO : int
        Automatic weather stations.
    OTHER : int
        Non-automatic weather stations.
    """
    AUTO = 0
    OTHER = 1


class MeteocatWeatherStationStateCategory(enum.Enum):
    """
    Enum for Meteocat weather station state categories.

    Attributes
    ----------
    ACTIVE : int
        Active station.
    DISMANTLED : int
        Dismantled station.
    REPAIR : int
        Station under repair or temporarily inactive.
    """
    ACTIVE = 2
    DISMANTLED = 1
    REPAIR = 3

class MeteocatWeatherStationStateParams(StateParams):
    """
    TypedDict for Meteocat weather station state initialization parameters.

    Attributes
    ----------
    meteocat_weather_station_state_code : MeteocatWeatherStationStateCategory
        State category of the station.
    meteocat_weather_station : int or MeteocatWeatherStation, optional
        Associated Meteocat weather station (object or ID).
    """
    meteocat_weather_station_state_code: MeteocatWeatherStationStateCategory
    meteocat_weather_station: NotRequired[Union[MeteocatWeatherStation, int]]

class MeteocatWeatherStationState(State):
    """
    SQLAlchemy model for Meteocat weather station states.

    Attributes
    ----------
    meteocat_weather_station_state_code : MeteocatWeatherStationStateCategory
        State category of the station.
    meteocat_weather_station_id : int
        Foreign key to MeteocatWeatherStation.
    meteocat_weather_station : MeteocatWeatherStation
        Relationship to MeteocatWeatherStation.
    """
    # SQLAlchemy columns
    __tablename__ = "meteocat_weather_station_state"
    meteocat_weather_station_state_code = mapped_column('meteocat_weather_station_state_code', Enum(MeteocatWeatherStationStateCategory, name='meteocat_weather_station_state_category'), nullable=False)
    # SQLAlchemy relations
    meteocat_weather_station_id: Mapped[int] = mapped_column(Integer, ForeignKey('weather_station.weather_station_id'))
    meteocat_weather_station: Mapped["MeteocatWeatherStation"] = relationship(back_populates='meteocat_weather_station_states')

    def __init__(self, **kwargs: Unpack[MeteocatWeatherStationStateParams]) -> None:
        """
        Initialize a MeteocatWeatherStationState.

        Parameters
        ----------
        **kwargs : Unpack[MeteocatWeatherStationStateParams]
            Initialization arguments.
        """
        super().__init__(**kwargs)
        for key, value in kwargs.items():
            if hasattr(self, key) and not Base.is_defined_in_parents(MeteocatWeatherStationState, key):
                setattr(self, key, value)

    def __iter__(self) -> Iterator[Tuple[str, Any]]:
        """
        Iterate over the attributes as key-value pairs.

        Yields
        ------
        tuple of (str, Any)
            Attribute name and its value.
        """
        yield from super().__iter__()
        yield 'meteocat_weather_station_state_code', self.meteocat_weather_station_state_code.name
        yield 'weather_station_id', self.meteocat_weather_station_id

    @staticmethod
    def object_hook_meteocat_api(dct: Dict[str, Any]) -> Union[MeteocatWeatherStationState, None]:
        """
        Decode a Meteocat API state JSON into a MeteocatWeatherStationState.

        Parameters
        ----------
        dct : dict
            JSON dictionary from Meteocat API.

        Returns
        -------
        MeteocatWeatherStationState or None
        """
        if all(k in dct for k in ('codi', 'dataInici', 'dataFi')):
            state = MeteocatWeatherStationState(
                meteocat_weather_station_state_code=MeteocatWeatherStationStateCategory(dct['codi']),
                state_valid_from_utc_date_time=datetime.datetime.strptime(dct['dataInici'], "%Y-%m-%dT%H:%M%z")
            )
            if dct['dataFi'] is not None:
                state.state_valid_until_utc_date_time = datetime.datetime.strptime(dct['dataFi'], "%Y-%m-%dT%H:%M%z")
            return state
        return None  # pragma: no cover

    @staticmethod
    def object_hook_gisfire_api(dct: Dict[str, Any]) -> Union[MeteocatWeatherStationState, None]:
        """
        Decode a GISFire API state JSON into a MeteocatWeatherStationState.

        Parameters
        ----------
        dct : dict
            JSON dictionary from GISFire API.

        Returns
        -------
        MeteocatWeatherStationState or None
        """
        if all(k in dct for k in ('meteocat_weather_station_state_code',
                                  'state_valid_from_utc_date_time',
                                  'state_valid_until_utc_date_time',
                                  'weather_station_id')):
            state = MeteocatWeatherStationState(
                meteocat_weather_station_state_code=MeteocatWeatherStationStateCategory[dct['meteocat_weather_station_state_code']],
                state_valid_from_utc_date_time=datetime.datetime.strptime(dct['state_valid_from_utc_date_time'], "%Y-%m-%dT%H:%M:%S%z"),
                meteocat_weather_station=dct['weather_station_id']
            )
            if dct['valid_until'] is not None:
                state.state_valid_until_utc_date_time = datetime.datetime.strptime(dct['state_valid_until_utc_date_time'], "%Y-%m-%dT%H:%M:%S%z")
            return state
        return None  # pragma: no cover

class MeteocatWeatherStationStateJSONEncoder(json.JSONEncoder):
    """
    JSON encoder for MeteocatWeatherStationState.
    """

    def default(self, obj: object) -> Dict[str, Any]:
        """
        Encode MeteocatWeatherStationState as a JSON-compatible dict.

        Parameters
        ----------
        obj : object
            Object to encode.

        Returns
        -------
        dict
            JSON representation.
        """
        if isinstance(obj, MeteocatWeatherStationState):
            obj: MeteocatWeatherStationState
            dct_weather_station_state = dict(obj)
            return dct_weather_station_state
        return json.JSONEncoder.default(self, obj)  # pragma: no cover


class MeteocatWeatherStationParams(WeatherStationParams):
    """
    TypedDict for Meteocat weather station initialization parameters.

    Attributes
    ----------
    x_4258, y_4258 : float
        Coordinates in EPSG:4258.
    meteocat_weather_station_code : str
        Unique code.
    meteocat_weather_station_category : MeteocatWeatherStationCategory
        Station type.
    meteocat_weather_station_placement : str
        Placement description.
    meteocat_weather_station_municipality_code, meteocat_weather_station_municipality_name : str
        Municipality information.
    meteocat_weather_station_county_code, meteocat_weather_station_county_name : str
        County information.
    meteocat_weather_station_province_code, meteocat_weather_station_province_name : str
        Province information.
    meteocat_weather_station_network_code, meteocat_weather_station_network_name : str
        Network information.
    """
    x_4258: float
    y_4258: float
    meteocat_weather_station_code: str
    meteocat_weather_station_category: MeteocatWeatherStationCategory
    meteocat_weather_station_placement: str
    meteocat_weather_station_municipality_code: str
    meteocat_weather_station_municipality_name: str
    meteocat_weather_station_county_code: str
    meteocat_weather_station_county_name: str
    meteocat_weather_station_province_code: str
    meteocat_weather_station_province_name: str
    meteocat_weather_station_network_code: str
    meteocat_weather_station_network_name: str

class MeteocatWeatherStation(WeatherStation):
    """
    SQLAlchemy model for Meteocat weather stations.

    Attributes
    ----------
    meteocat_weather_station_code : str
        Station code.
    meteocat_weather_station_category : MeteocatWeatherStationCategory
        Station type.
    meteocat_weather_station_placement : str
        Placement description.
    meteocat_weather_station_municipality_code, meteocat_weather_station_municipality_name : str
        Municipality information.
    meteocat_weather_station_county_code, meteocat_weather_station_county_name : str
        County information.
    meteocat_weather_station_province_code, meteocat_weather_station_province_name : str
        Province information.
    meteocat_weather_station_network_code, meteocat_weather_station_network_name : str
        Network information.
    meteocat_weather_station_states : list of MeteocatWeatherStationState
        Related station states.
    """
    # Metaclass location attributes
    __location__ = [
        {'epsg': 4258, 'validation': 'geographic', 'conversion': [
            {'src': 4258, 'dst': 4326},
            {'src': 4258, 'dst': 25831}
        ], 'nullable': False},
        {'epsg': 25831, 'validation': False, 'conversion': False, 'nullable': False}
    ]
    # Type hint fot generated attributes by the metaclass
    x_4258: float
    y_4258: float
    geometry_4258: Union[str, Point]
    x_25831: float
    y_25831: float
    geometry_25831: Union[str, Point]
    # SQLAlchemy columns
    meteocat_weather_station_code: Mapped[str] = mapped_column('meteocat_code', String, nullable=False, unique=True)
    meteocat_weather_station_category: Mapped[MeteocatWeatherStationCategory] = mapped_column('meteocat_type', Enum(MeteocatWeatherStationCategory, name='meteocat_weather_station_category'), nullable=False)
    meteocat_weather_station_placement: Mapped[str] = mapped_column('meteocat_placement', String, nullable=False)
    meteocat_weather_station_municipality_code: Mapped[str] = mapped_column('meteocat_municipality_code', String, nullable=False)
    meteocat_weather_station_municipality_name: Mapped[str] = mapped_column('meteocat_municipality_name', String, nullable=False)
    meteocat_weather_station_county_code: Mapped[str] = mapped_column('meteocat_county_code', String, nullable=False)
    meteocat_weather_station_county_name: Mapped[str] = mapped_column('meteocat_county_name', String, nullable=False)
    meteocat_weather_station_province_code: Mapped[str] = mapped_column('meteocat_province_code', String, nullable=False)
    meteocat_weather_station_province_name: Mapped[str] = mapped_column('meteocat_province_name', String, nullable=False)
    meteocat_weather_station_network_code: Mapped[str] = mapped_column('meteocat_network_code', String, nullable=False)
    meteocat_weather_station_network_name: Mapped[str] = mapped_column('meteocat_network_name', String, nullable=False)
    # SQLAlchemy Relations
    meteocat_weather_station_states: Mapped[List[MeteocatWeatherStationState]] = relationship("MeteocatWeatherStationState", back_populates='meteocat_weather_station', lazy='joined')
    meteocat_variable_states: Mapped[List["MeteocatVariableState"]] = relationship('MeteocatVariableState', back_populates='meteocat_weather_station')
    meteocat_variable_time_bases: Mapped[List["MeteocatVariableTimeBase"]] = relationship('MeteocatVariableTimeBase', back_populates='meteocat_weather_station')
    # measures: Mapped[List["MeteocatMeasure"]] = relationship('MeteocatMeasure', back_populates='weather_station')
    # SQLAlchemy Inheritance options
    __mapper_args__ = {
        "polymorphic_identity": "meteocat_weather_station",
    }

    def __init__(self, **kwargs: Unpack[MeteocatWeatherStationParams]) -> None:
        """
        Initialize a MeteocatWeatherStation.

        Parameters
        ----------
        **kwargs : Unpack[MeteocatWeatherStationParams]
            Initialization arguments.
        """
        super().__init__(**kwargs)
        for key, value in kwargs.items():
            if hasattr(self, key) and not Base.is_defined_in_parents(MeteocatWeatherStation, key):
                setattr(self, key, value)

    def __iter__(self) -> Iterator[Any]:
        """
        Iterate over the attributes as key-value pairs.

        Yields
        ------
        tuple of (str, Any)
            Attribute name and its value.
        """
        yield from super().__iter__()
        yield 'meteocat_weather_station_code', self.meteocat_weather_station_code
        yield 'meteocat_weather_station_category', self.meteocat_weather_station_category.name
        yield 'meteocat_weather_station_placement', self.meteocat_weather_station_placement
        yield 'meteocat_weather_station_municipality_name', self.meteocat_weather_station_municipality_name
        yield 'meteocat_weather_station_county_code', self.meteocat_weather_station_county_code
        yield 'meteocat_weather_station_county_name', self.meteocat_weather_station_county_name
        yield 'meteocat_weather_station_province_code', self.meteocat_weather_station_province_code
        yield 'meteocat_weather_station_province_name', self.meteocat_weather_station_province_name
        yield 'meteocat_weather_station_network_code', self.meteocat_weather_station_network_code
        yield 'meteocat_weather_station_network_name', self.meteocat_weather_station_network_name
        # yield 'states', [dict(state) for state in self.meteocat_weather_station_states]

    # @property
    # def meteocat_variables(self) -> List[MeteocatVariable]:
    #     return list(object_session(self).execute(select(MeteocatVariable).
    #                                              join(MeteocatVariableState).
    #                                              where(MeteocatVariable.id == MeteocatVariableState.meteocat_variable_id).
    #                                              where(MeteocatVariableState.meteocat_weather_station_id == self.id)).
    #                 unique().scalars().all())

    @staticmethod
    def object_hook_meteocat_api(dct: Dict[str, Any]) -> Union[WeatherStation, Dict[str, Any], MeteocatWeatherStation, MeteocatWeatherStationState, None]:
        """
        Decode a Meteocat API JSON into a MeteocatWeatherStation or related objects.

        Parameters
        ----------
        dct : dict
            JSON dictionary from Meteocat API.

        Returns
        -------
        MeteocatWeatherStation, MeteocatWeatherStationState, dict, or None
        """
        # 'municipi', 'comarca', 'provincia' or 'xarxa' dict of the Meteocat API JSON
        if all(k in dct for k in ('codi', 'nom')) and len(dct) == 2:
            return dct
        # weather station status dict of the Meteocat API JSON
        if all(k in dct for k in ('codi', 'dataInici', 'dataFi')):
            state = MeteocatWeatherStationState.object_hook_meteocat_api(dct)
            return state
        # Lat-lon coordinates dict of the Meteocat API JSON
        if all(k in dct for k in ('latitud', 'longitud')):
            return dct
        if not (all(k in dct for k in ('codi', 'nom', 'tipus', 'coordenades', 'emplacament', 'altitud', 'municipi',
                                       'comarca', 'provincia', 'xarxa', 'estats'))):
            return None  # pragma: no cover
        station = MeteocatWeatherStation(
            meteocat_weather_station_code=str(dct['codi']),
            weather_station_name=str(dct['nom']),
            meteocat_weather_station_category=MeteocatWeatherStationCategory.AUTO if str(dct['tipus']) == 'A' else MeteocatWeatherStationCategory.OTHER,
            meteocat_weather_station_placement=str(dct['emplacament']),
            weather_station_altitude=float(dct['altitud']),
            x_4258=float(dct['coordenades']['longitud']),
            y_4258=float(dct['coordenades']['latitud']),
            meteocat_weather_station_municipality_code=str(dct['municipi']['codi']),
            meteocat_weather_station_municipality_name=str(dct['municipi']['nom']),
            meteocat_weather_station_county_code=str(dct['comarca']['codi']),
            meteocat_weather_station_county_name=str(dct['comarca']['nom']),
            meteocat_weather_station_province_code=str(dct['provincia']['codi']),
            meteocat_weather_station_province_name=str(dct['provincia']['nom']),
            meteocat_weather_station_network_code=str(dct['xarxa']['codi']),
            meteocat_weather_station_network_name=str(dct['xarxa']['nom']),
            data_provider="Meteo.cat"
        )
        for state in dct['estats']:
            state: MeteocatWeatherStationState
            station.meteocat_weather_station_states.append(state)
        return station

    @staticmethod
    def object_hook_gisfire_api(dct: Dict[str, Any]) -> Union[WeatherStation, Dict[str, Any], MeteocatWeatherStation, MeteocatWeatherStationState, None]:
        """
        Decode a GISFire API JSON into a MeteocatWeatherStation.

        Parameters
        ----------
        dct : dict
            JSON dictionary from GISFire API.

        Returns
        -------
        MeteocatWeatherStation or None
        """
        # weather station status dict of the Meteocat API JSON
        # if all(k in dct for k in ('id', 'valid_from', 'valid_until', 'ts', 'code', 'weather_station_id')):
        #     state = MeteocatWeatherStationState.object_hook_gisfire_api(dct)
        #     return state
        if all(k in dct for k in ('weather_station_name',
                                  'weather_station_altitude',
                                  'x_4258',
                                  'y_4258',
                                  'data_provider_name',
                                  'meteocat_weather_station_code',
                                  'meteocat_weather_station_category',
                                  'meteocat_weather_station_placement',
                                  'meteocat_weather_station_municipality_code',
                                  'meteocat_weather_station_municipality_name',
                                  'meteocat_weather_station_county_code',
                                  'meteocat_weather_station_county_name',
                                  'meteocat_weather_station_province_code',
                                  'meteocat_weather_station_province_name',
                                  'meteocat_weather_station_network_code',
                                  'meteocat_weather_station_network_name')):
            station = MeteocatWeatherStation(
                meteocat_weather_station_code=str(dct['meteocat_weather_station_code']),
                weather_station_name=str(dct['weather_station_name']),
                meteocat_weather_station_category=MeteocatWeatherStationCategory[dct['meteocat_weather_station_category']],
                meteocat_weather_station_placement=str(dct['meteocat_weather_station_placement']),
                weather_station_altitude=float(dct['weather_station_altitude']),
                x_4258=float(dct['x_4258']),
                y_4258=float(dct['y_4258']),
                meteocat_weather_station_municipality_code=str(dct['meteocat_weather_station_municipality_code']),
                meteocat_weather_station_municipality_name=str(dct['meteocat_weather_station_municipality_name']),
                meteocat_weather_station_county_code=str(dct['meteocat_weather_station_county_code']),
                meteocat_weather_station_county_name=str(dct['meteocat_weather_station_county_name']),
                meteocat_weather_station_province_code=str(dct['meteocat_weather_station_province_code']),
                meteocat_weather_station_province_name=str(dct['meteocat_weather_station_province_name']),
                meteocat_weather_station_network_code=str(dct['meteocat_weather_station_network_code']),
                meteocat_weather_station_network_name=str(dct['meteocat_weather_station_network_name']),
                data_provider=dct['data_provider_name']
            )
            # for state in dct['states']:
            #     state: MeteocatWeatherStationState
            #     station.meteocat_weather_station_states.append(state)
            return station
        return None  # pragma: no cover

class MeteocatWeatherStationJSONEncoder(json.JSONEncoder):
    """
    JSON encoder for MeteocatWeatherStation.
    """

    def default(self, obj: object) -> Dict[str, Any]:
        """
        Encode MeteocatWeatherStation as a JSON-compatible dict.

        Parameters
        ----------
        obj : object
            Object to encode.

        Returns
        -------
        dict
            JSON representation.
        """
        if isinstance(obj, MeteocatWeatherStation):
            obj: MeteocatWeatherStation
            dct_weather_station = dict(obj)
            return dct_weather_station
        return json.JSONEncoder.default(self, obj)  # pragma: no cover

# class MeteocatWeatherStationGeoJSONEncoder(json.JSONEncoder):
#
#     def default(self, obj: object) -> Dict[str, Any]:
#         if isinstance(obj, WeatherStation):
#             obj: WeatherStation
#             dct = dict()
#             dct['type'] = 'Feature'
#             dct['id'] = obj.id
#             dct['geometry'] = dict()
#             dct['geometry']['type'] = 'Point'
#             dct['geometry']['coordinates'] = [obj.x_4326, obj.y_4326]
#             dct['properties'] = dict(obj)
#             return dct
#         return json.JSONEncoder.default(self, obj)  # pragma: no cover