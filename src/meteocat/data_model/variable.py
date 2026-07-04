#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations  # Needed to allow returning type of enclosing class PEP 563

import enum
import datetime
import json

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import Enum
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import relationship

from src.data_model import Base
from src.data_model.state import State
from src.data_model.state import StateParams
from src.data_model.variable import Variable
from src.data_model.variable import VariableParams
from src.meteocat.data_model.weather_station import MeteocatWeatherStation

from typing import Union
from typing import Dict
from typing import Optional
from typing import Any
from typing import List
from typing import Iterator
from typing import Unpack
from typing import NotRequired
from typing import Tuple

class MeteocatVariableCategory(str, enum.Enum):
    """
    Enumeration of Meteocat variable categories.

    Categories
    ----------
    DAT : str
        Real measured data.
    AUX : str
        Auxiliary data.
    CMV : str
        Compound multivariate data calculated from others.
    """
    DAT = 'DAT'  #: Real measured data
    AUX = 'AUX'  #: Auxiliary data
    CMV = 'CMV'  #: Compound multivariate data


class MeteocatVariableStateCategory(enum.Enum):
    """
    Enumeration of Meteocat variable state categories.

    Categories
    ----------
    ACTIVE : int
        Active station.
    DISMANTLED : int
        Dismantled station.
    REPAIR : int
        Station under repair or temporary inactivity.
    """
    ACTIVE = 2  #: Active station
    DISMANTLED = 1  #: Dismantled station
    REPAIR = 3  #: Station under repair or temporarily inactive


class MeteocatVariableTimeBaseCategory(str, enum.Enum):
    """
    Enumeration of Meteocat variable time bases.

    Categories
    ----------
    HO : str
        Hourly data.
    SH : str
        Semi-hourly data (30 minutes).
    DM : str
        Ten-minutely data.
    MI : str
        Minutely data.
    D5 : str
        Five-minutely data.
    """
    HO = 'HO'  #: Hourly data
    SH = 'SH'  #: Semi-hourly (30 minutes) data
    DM = 'DM'  #: Ten-minutely data
    MI = 'MI'  #: Minutely data
    D5 = 'D5'  #: Five-minutely data

class MeteocatVariableStateParams(StateParams):
    """
    TypedDict for initialization parameters of `MeteocatVariableState`.

    Attributes
    ----------
    meteocat_variable_state_code : MeteocatVariableStateCategory
        State category (active, dismantled, repair).
    meteocat_weather_station : MeteocatWeatherStation or int, optional
        Weather station instance or its ID.
    meteocat_variable : MeteocatVariable or int, optional
        Variable instance or its ID.
    """
    meteocat_variable_state_code: MeteocatVariableStateCategory
    meteocat_weather_station: NotRequired[Union[MeteocatWeatherStation, int]]
    meteocat_variable: NotRequired[Union[MeteocatVariable, int]]

class MeteocatVariableState(State):
    """
    SQLAlchemy ORM model for Meteocat variable state.

    Attributes
    ----------
    meteocat_variable_state_code : MeteocatVariableStateCategory
        Code indicating the state of the variable.
    meteocat_weather_station_id : int
        Foreign key to the associated weather station.
    meteocat_weather_station : MeteocatWeatherStation
        Relationship to the associated weather station.
    meteocat_variable_id : int
        Foreign key to the associated variable.
    meteocat_variable : MeteocatVariable
        Relationship to the associated variable.
    """
    __tablename__ = 'meteocat_variable_state'
    # SQLAlchemy columns
    meteocat_variable_state_code = mapped_column('meteocat_variable_state_code', Enum(MeteocatVariableStateCategory, name='meteocat_variable_state_category'), nullable=False)
    # SQLAlchemy relations
    meteocat_weather_station_id: Mapped[int] = mapped_column(Integer, ForeignKey('weather_station.weather_station_id'))
    meteocat_weather_station: Mapped["MeteocatWeatherStation"] = relationship('MeteocatWeatherStation', back_populates='meteocat_variable_states')
    meteocat_variable_id: Mapped[int] = mapped_column(Integer, ForeignKey('variable.variable_id'), nullable=False)
    meteocat_variable: Mapped["MeteocatVariable"] = relationship('MeteocatVariable', back_populates='meteocat_variable_states')

    def __init__(self, **kwargs: Unpack[MeteocatVariableStateParams]) -> None:
        """
        Initialize a MeteocatVariableState instance.

        Parameters
        ----------
        **kwargs : Unpack[MeteocatVariableStateParams]
            Initialization parameters including state code, variable, and station.
        """
        super().__init__(**kwargs)
        for key, value in kwargs.items():
            if hasattr(self, key) and not Base.is_defined_in_parents(MeteocatVariableState, key):
                if key == "meteocat_weather_station" and isinstance(value, int):
                    self.meteocat_weather_station_id = value
                elif key == "meteocat_variable" and isinstance(value, int):
                    self.meteocat_variable_id = value
                else:
                    setattr(self, key, value)

    def __iter__(self):
        """
        Iterate over the object's attributes as key-value pairs.

        Yields
        ------
        tuple of (str, Any)
            Attribute name and its value.
        """
        yield from super().__iter__()
        yield 'meteocat_variable_state_code', self.meteocat_variable_state_code.name
        yield 'meteocat_variable_id', self.meteocat_variable_id
        yield 'meteocat_weather_station_id', self.meteocat_weather_station_id

    @staticmethod
    def object_hook_meteocat_api(dct: Dict[str, Any]) -> Union[MeteocatVariableState, None]:
        """
        Deserialize Meteocat API dictionary into a `MeteocatVariableState`.

        Parameters
        ----------
        dct : dict of str to Any
            Dictionary from Meteocat API containing keys 'codi', 'dataInici', 'dataFi'.

        Returns
        -------
        MeteocatVariableState or None
            Deserialized object or None if input is invalid.
        """
        if all(k in dct for k in ('codi', 'dataInici', 'dataFi')):
            state = MeteocatVariableState(
                meteocat_variable_state_code=MeteocatVariableStateCategory(dct['codi']),
                state_valid_from_utc_date_time=datetime.datetime.strptime(dct['dataInici'], "%Y-%m-%dT%H:%M%z")
            )
            if dct['dataFi'] is not None:
                state.state_valid_until_utc_date_time = datetime.datetime.strptime(dct['dataFi'], "%Y-%m-%dT%H:%M%z")
            return state
        return None  # pragma: no cover

    @staticmethod
    def object_hook_gisfire_api(dct: Dict[str, Any]) -> Union[MeteocatVariableState, None]:
        """
        Deserialize GISFire API dictionary into a `MeteocatVariableState`.

        Parameters
        ----------
        dct : dict of str to Any
            Dictionary from GISFire API containing state attributes.

        Returns
        -------
        MeteocatVariableState or None
            Deserialized object or None if input is invalid.
        """
        if all(k in dct for k in ('meteocat_variable_state_code',
                                  'state_valid_from_utc_date_time',
                                  'state_valid_until_utc_date_time',
                                  'meteocat_variable_id',
                                  'meteocat_weather_station_id')):
            variable_state = MeteocatVariableState(
                state_valid_from_utc_date_time=datetime.datetime.strptime(dct['state_valid_from_utc_date_time'], "%Y-%m-%dT%H:%M:%S%z"),
                meteocat_variable_state_code=MeteocatVariableStateCategory(dct['meteocat_variable_state_code']),
                meteocat_variable=dct['meteocat_variable_id'],
                meteocat_weather_station=dct['meteocat_weather_station_id'],
            )
            if dct['state_valid_until_utc_date_time'] is not None:
                variable_state.state_valid_until_utc_date_time = datetime.datetime.strptime(dct['state_valid_until_utc_date_time'], "%Y-%m-%dT%H:%M:%S%z")
            return variable_state
        return None  # pragma: no cover

class MeteocatVariableStateJSONEncoder(json.JSONEncoder):
    """
    JSON encoder for `MeteocatVariableState`.

    Methods
    -------
    default(obj)
        Encode `MeteocatVariableState` as a dictionary.
    """

    def default(self, obj: object) -> Dict[str, Any]:
        """
        Encode MeteocatVariableState to a serializable dictionary.

        Parameters
        ----------
        obj : object
            Object to encode.

        Returns
        -------
        dict of str to Any
            Dictionary representation of the variable state.
        """
        if isinstance(obj, MeteocatVariableState):
            obj: MeteocatVariableState
            dct_variable_state = dict(obj)
            return dct_variable_state
        return json.JSONEncoder.default(self, obj)  # pragma: no cover

class MeteocatVariableTimeBaseParams(StateParams):
    """
    TypedDict for initialization parameters of `MeteocatVariableTimeBase`.

    Attributes
    ----------
    meteocat_variable_time_base_code : MeteocatVariableTimeBaseCategory
        Code indicating the time base type (HO, SH, DM, MI, D5).
    meteocat_weather_station : MeteocatWeatherStation or int, optional
        Weather station instance or its ID.
    meteocat_variable : MeteocatVariable or int, optional
        Variable instance or its ID.
    """
    meteocat_variable_time_base_code: MeteocatVariableTimeBaseCategory
    meteocat_weather_station: NotRequired[Union[MeteocatWeatherStation, int]]
    meteocat_variable: NotRequired[Union[MeteocatVariable, int]]

class MeteocatVariableTimeBase(State):
    """
    SQLAlchemy ORM model for Meteocat variable time base.

    Attributes
    ----------
    meteocat_variable_time_base_code : MeteocatVariableTimeBaseCategory
        Enum code indicating the type of sampling time.
    meteocat_weather_station_id : int
        Foreign key to the associated weather station.
    meteocat_weather_station : MeteocatWeatherStation
        Relationship to the associated weather station.
    meteocat_variable_id : int
        Foreign key to the associated variable.
    meteocat_variable : MeteocatVariable
        Relationship to the associated variable.
    """
    __tablename__ = 'meteocat_variable_time_base'
    meteocat_variable_time_base_code = mapped_column('meteocat_variable_time_base_code', Enum(MeteocatVariableTimeBaseCategory, name='meteocat_variable_time_base_category'), nullable=False)
    # SQLAlchemy relations
    meteocat_weather_station_id: Mapped[int] = mapped_column(Integer, ForeignKey('weather_station.weather_station_id'))
    meteocat_weather_station: Mapped["MeteocatWeatherStation"] = relationship('MeteocatWeatherStation', back_populates='meteocat_variable_time_bases')
    meteocat_variable_id: Mapped[int] = mapped_column(Integer, ForeignKey('variable.variable_id'), nullable=False)
    meteocat_variable: Mapped["MeteocatVariable"] = relationship('MeteocatVariable', back_populates='meteocat_variable_time_bases')

    def __init__(self, **kwargs: Unpack[MeteocatVariableTimeBaseParams]) -> None:
        """
        Initialize a MeteocatVariableTimeBase instance.

        Parameters
        ----------
        **kwargs : Unpack[MeteocatVariableTimeBaseParams]
            Initialization parameters including time base code, variable, and station.
        """
        super().__init__(**kwargs)
        for key, value in kwargs.items():
            if hasattr(self, key) and not Base.is_defined_in_parents(MeteocatVariableTimeBase, key):
                if key == "meteocat_weather_station" and isinstance(value, int):
                    self.meteocat_weather_station_id = value
                elif key == "meteocat_variable" and isinstance(value, int):
                    self.meteocat_variable_id = value
                else:
                    setattr(self, key, value)


    def __iter__(self):
        """
        Iterate over the object's attributes as key-value pairs.

        Yields
        ------
        tuple of (str, Any)
            Attribute name and its value.
        """
        yield from super().__iter__()
        yield 'meteocat_variable_time_base_code', self.meteocat_variable_time_base_code.name
        yield 'meteocat_variable_id', self.meteocat_variable_id
        yield 'meteocat_weather_station_id', self.meteocat_weather_station_id

    @staticmethod
    def object_hook_meteocat_api(dct: Dict[str, Any]) -> Optional[MeteocatVariableTimeBase]:
        """
        Deserialize Meteocat API dictionary into a `MeteocatVariableTimeBase`.

        Parameters
        ----------
        dct : dict of str to Any
            Dictionary from Meteocat API containing keys 'codi', 'dataInici', 'dataFi'.

        Returns
        -------
        MeteocatVariableTimeBase or None
            Deserialized object or None if input is invalid.
        """
        if all(k in dct for k in ('codi', 'dataInici', 'dataFi')):
            time_base = MeteocatVariableTimeBase(
                meteocat_variable_time_base_code=MeteocatVariableTimeBaseCategory(dct['codi']),
                state_valid_from_utc_date_time=datetime.datetime.strptime(dct['dataInici'], "%Y-%m-%dT%H:%M%z")
            )
            if dct['dataFi'] is not None:
                time_base.state_valid_until_utc_date_time = datetime.datetime.strptime(dct['dataFi'], "%Y-%m-%dT%H:%M%z")
            return time_base
        return None  # pragma: no cover

    @staticmethod
    def object_hook_gisfire_api(dct: Dict[str, Any]) -> Optional[MeteocatVariableTimeBase]:
        """
        Deserialize GISFire API dictionary into a `MeteocatVariableTimeBase`.

        Parameters
        ----------
        dct : dict of str to Any
            Dictionary from GISFire API containing time base attributes.

        Returns
        -------
        MeteocatVariableTimeBase or None
            Deserialized object or None if input is invalid.
        """
        if all(k in dct for k in ('meteocat_variable_time_base_code',
                                  'state_valid_from_utc_date_time',
                                  'state_valid_until_utc_date_time',
                                  'meteocat_variable_id',
                                  'meteocat_weather_station_id')):
            variable_time_base = MeteocatVariableTimeBase(
                state_valid_from_utc_date_time=datetime.datetime.strptime(dct['state_valid_from_utc_date_time'], "%Y-%m-%dT%H:%M:%S%z"),
                meteocat_variable_time_base_code=MeteocatVariableTimeBaseCategory(dct['meteocat_variable_time_base_code']),
                meteocat_variable=dct['meteocat_variable_id'],
                meteocat_weather_station=dct['meteocat_weather_station_id'],
            )
            if dct['state_valid_until_utc_date_time'] is not None:
                variable_time_base.state_valid_until_utc_date_time = datetime.datetime.strptime(dct['state_valid_until_utc_date_time'], "%Y-%m-%dT%H:%M:%S%z")
            return variable_time_base
        return None  # pragma: no cover


class MeteocatVariableTimeBaseJSONEncoder(json.JSONEncoder):
    """
    JSON encoder for `MeteocatVariableTimeBase`.

    Methods
    -------
    default(obj)
        Encode `MeteocatVariableTimeBase` as a dictionary.
    """

    def default(self, obj: object) -> Dict[str, Any]:
        """
        Encode MeteocatVariableTimeBase to a serializable dictionary.

        Parameters
        ----------
        obj : object
            Object to encode.

        Returns
        -------
        dict of str to Any
            Dictionary representation of the variable time base.
        """
        if isinstance(obj, MeteocatVariableTimeBase):
            obj: MeteocatVariableTimeBase
            dct_variable_time_base = dict(obj)
            return dct_variable_time_base
        return json.JSONEncoder.default(self, obj)  # pragma: no cover

class MeteocatVariableParams(VariableParams):
    """
    TypedDict for initialization parameters of `MeteocatVariable`.

    Attributes
    ----------
    meteocat_variable_code : int
        Meteocat variable code.
    meteocat_variable_unit : str
        Unit of measurement.
    meteocat_variable_acronym : str
        Acronym used by Meteocat.
    meteocat_variable_category : MeteocatVariableCategory
        Variable category (e.g., temperature, wind).
    meteocat_variable_decimal_positions : int
        Number of decimal positions for values.
    """
    meteocat_variable_code: int
    meteocat_variable_unit: str
    meteocat_variable_acronym: str
    meteocat_variable_category: MeteocatVariableCategory
    meteocat_variable_decimal_positions: int

class MeteocatVariable(Variable):
    """
    SQLAlchemy ORM model for Meteocat variables.

    Attributes
    ----------
    meteocat_variable_code : int
        Unique Meteocat variable code.
    meteocat_variable_unit : str
        Unit of the variable.
    meteocat_variable_acronym : str
        Acronym of the variable.
    meteocat_variable_category : MeteocatVariableCategory
        Category of the variable.
    meteocat_variable_decimal_positions : int
        Decimal precision of the variable values.
    meteocat_variable_states : list of MeteocatVariableState
        Relationship to associated states.
    meteocat_variable_time_bases : list of MeteocatVariableTimeBase
        Relationship to associated time bases.
    """
    # SQLAlchemy columns
    meteocat_variable_code: Mapped[int] = mapped_column('meteocat_variable_code', Integer, nullable=False, unique=True)
    meteocat_variable_unit: Mapped[str] = mapped_column('meteocat_variable_unit', String, nullable=False)
    meteocat_variable_acronym: Mapped[str] = mapped_column('meteocat_variable_acronym', String, nullable=False)
    meteocat_variable_category: Mapped[MeteocatVariableCategory] = mapped_column('meteocat_variable_category', Enum(MeteocatVariableCategory, name='meteocat_variable_category'), nullable=False)
    meteocat_variable_decimal_positions: Mapped[int] = mapped_column('meteocat_variable_decimal_positions', Integer, nullable=False)
    # SQLAlchemy relations
    meteocat_variable_states: Mapped[List["MeteocatVariableState"]] = relationship('MeteocatVariableState', back_populates='meteocat_variable')
    meteocat_variable_time_bases: Mapped[List["MeteocatVariableTimeBase"]] = relationship('MeteocatVariableTimeBase', back_populates='meteocat_variable')
    # measures: Mapped[List["MeteocatMeasure"]] = relationship('MeteocatMeasure', back_populates='meteocat_variable')
    # SQLAlchemy Inheritance options
    __mapper_args__ = {
        "polymorphic_identity": "meteocat_variable",
    }

    def __init__(self, **kwargs: Unpack[MeteocatVariableParams]) -> None:
        """
        Initialize a MeteocatVariable instance.

        Parameters
        ----------
        **kwargs : Unpack[MeteocatVariableParams]
            Initialization parameters including code, unit, acronym, category, and decimals.
        """
        super().__init__(**kwargs)
        for key, value in kwargs.items():
            if hasattr(self, key) and not Base.is_defined_in_parents(MeteocatVariable, key):
                setattr(self, key, value)

    def __iter__(self) -> Iterator[Tuple[str, Any]]:
        """
        Iterate over the object's attributes as key-value pairs.

        Yields
        ------
        tuple of (str, Any)
            Attribute name and its value.
        """
        yield from super().__iter__()
        yield 'meteocat_variable_code', self.meteocat_variable_code
        yield 'meteocat_variable_unit', self.meteocat_variable_unit
        yield 'meteocat_variable_acronym', self.meteocat_variable_acronym
        yield 'meteocat_variable_category', self.meteocat_variable_category.name
        yield 'meteocat_variable_decimal_positions', self.meteocat_variable_decimal_positions

    @staticmethod
    def object_hook_variable_meteocat_api(dct: Dict[str, Any]) -> Union[MeteocatVariable, None]:
        """
        Deserialize Meteocat API dictionary into a `MeteocatVariable`.

        Parameters
        ----------
        dct : dict of str to Any
            Dictionary from Meteocat API with variable data.

        Returns
        -------
        MeteocatVariable or None
            Deserialized object or None if input is invalid.
        """
        if all(k in dct for k in ('codi', 'nom', 'unitat', 'acronim', 'tipus', 'decimals')):
            variable = MeteocatVariable(
                variable_name=str(dct['nom']),
                meteocat_variable_code=int(dct['codi']),
                meteocat_variable_unit=str(dct['unitat']),
                meteocat_variable_acronym=str(dct['acronim']),
                meteocat_variable_category=MeteocatVariableCategory(dct['tipus']),
                meteocat_variable_decimal_positions=int(dct['decimals']),
                data_provider="Meteo.cat"
            )
            return variable
        return None  # pragma: no cover

    @staticmethod
    def object_hook_gisfire_api(dct: Dict[str, Any]) -> Union[MeteocatVariable, None]:
        """
        Deserialize GISFire API dictionary into a `MeteocatVariable`.

        Parameters
        ----------
        dct : dict of str to Any
            Dictionary from GISFire API containing variable attributes.

        Returns
        -------
        MeteocatVariable or None
            Deserialized object or None if input is invalid.

        Notes
        -----
        The current implementation checks for keys like 'variable_name' but
        then accesses 'name', 'code', etc., which may be inconsistent.
        """
        if all(k in dct for k in (
                'variable_name',
                'meteocat_variable_code',
                'meteocat_variable_unit',
                'meteocat_variable_acronym',
                'meteocat_variable_category',
                'meteocat_variable_decimal_positions',
                'data_provider'
        )):
            variable = MeteocatVariable(
                variable_name=dct['variable_name'],
                meteocat_variable_code=dct['meteocat_variable_code'],
                meteocat_variable_unit=dct['meteocat_variable_unit'],
                meteocat_variable_acronym=dct['meteocat_variable_acronym'],
                meteocat_variable_category=MeteocatVariableCategory(dct['meteocat_variable_category']),
                meteocat_variable_decimal_positions=dct['meteocat_variable_decimal_positions'],
                data_provider=dct['data_provider']
            )
            return variable
        return None  # pragma: no cover


    @staticmethod
    def object_hook_variables_of_station_meteocat_api(dct: Dict[str, Any]) -> Union[MeteocatVariable, MeteocatVariableTimeBase, MeteocatVariableState, None]:
        """
        Deserialize API dictionary of variables for a given station.

        Parameters
        ----------
        dct : dict of str to Any
            Dictionary from Meteocat station API.

        Returns
        -------
        MeteocatVariable, MeteocatVariableTimeBase, MeteocatVariableState, or None
            Deserialized object depending on the structure of `dct`.
        """
        if all(k in dct for k in ('codi', 'dataInici', 'dataFi')):
            if isinstance(dct['codi'], str):
                time_base = MeteocatVariableTimeBase.object_hook_meteocat_api(dct)
                return time_base
            else:
                state = MeteocatVariableState.object_hook_meteocat_api(dct)
                return state
        if all(k in dct for k in ('codi', 'nom', 'unitat', 'acronim', 'tipus', 'decimals')):
            variable = MeteocatVariable(
                variable_name=str(dct['nom']),
                meteocat_variable_code=int(dct['codi']),
                meteocat_variable_unit=str(dct['unitat']),
                meteocat_variable_acronym=str(dct['acronim']),
                meteocat_variable_category=MeteocatVariableCategory(dct['tipus']),
                meteocat_variable_decimal_positions=int(dct['decimals']),
                data_provider="Meteo.cat"
            )
            if 'estats' in dct and variable.meteocat_variable_category != MeteocatVariableCategory.CMV:
                variable.meteocat_variable_states = dct['estats']
            if 'basesTemporals' in dct:
                variable.meteocat_variable_time_bases = dct['basesTemporals']
            return variable
        return None  # pragma: no cover

class MeteocatVariableJSONEncoder(json.JSONEncoder):
    """
    JSON encoder for `MeteocatVariable`.

    Methods
    -------
    default(obj)
        Encode `MeteocatVariable` as a dictionary.
    """

    def default(self, obj: object) -> Dict[str, Any]:
        """
        Encode MeteocatVariable to a serializable dictionary.

        Parameters
        ----------
        obj : object
            Object to encode.

        Returns
        -------
        dict of str to Any
            Dictionary representation of the variable.
        """
        if isinstance(obj, MeteocatVariable):
            obj: MeteocatVariable
            dct_variable = dict(obj)
            return dct_variable
        return json.JSONEncoder.default(self, obj)  # pragma: no cover
