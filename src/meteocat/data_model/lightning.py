#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations  # Needed to allow returning type of enclosing class PEP 563

import datetime
import json

from src.data_model.lightning import LightningParams
from src.data_model.lightning import Lightning
from src.data_model.data_provider import DataProvider

from sqlalchemy import Integer
from sqlalchemy import Float
from sqlalchemy import Boolean
from sqlalchemy import String
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from shapely.geometry import Point

from typing import Optional
from typing import Union
from typing import Dict
from typing import Any
from typing import TypedDict
from typing_extensions import Unpack
from typing_extensions import NotRequired

class MeteocatLightningParams(LightningParams):
    """
    Typed parameter specification for initializing a :class:`MeteocatLightning`.

    Extends the generic :class:`~src.data_model.lightning.LightningParams`
    with Meteocat-specific fields. These parameters are used for
    type-checking and keyword unpacking when creating
    :class:`MeteocatLightning` instances.

    Attributes
    ----------
    meteocat_id : int
        Unique Meteocat identifier for the lightning event.
    peak_current : float
        Peak current of the lightning discharge, in kiloamperes.
    multiplicity : int, optional
        Number of strokes in the same flash (may be ``None``).
    chi_squared : float
        Chi-squared value from location quality estimation.
    ellipse_major_axis : float
        Length of the confidence ellipse major axis.
    ellipse_minor_axis : float
        Length of the confidence ellipse minor axis.
    ellipse_angle : float
        Angle (degrees) of the ellipse orientation.
    number_of_sensors : int
        Number of sensors that detected the event (must be > 0).
    hit_ground : bool
        Whether the lightning stroke reached ground.
    municipality_code : str, optional
        Code of the municipality where the event was located.
    x_4258 : float
        X coordinate (longitude/easting) in EPSG:4258.
    y_4258 : float
        Y coordinate (latitude/northing) in EPSG:4258.
    """
    meteocat_id: int
    peak_current: float
    multiplicity: NotRequired[int]
    chi_squared: float
    ellipse_major_axis: float
    ellipse_minor_axis: float
    ellipse_angle: float
    number_of_sensors: int
    hit_ground: bool
    municipality_code: NotRequired[str]
    x_4258: float
    y_4258: float

class MeteocatLightning(Lightning):
    """
    ORM model for lightning events from the Meteocat dataset.

    Inherits from :class:`~src.data_model.lightning.Lightning` and adds
    Meteocat-specific attributes, validation rules, and JSON decoding
    support. Coordinates are managed through metaclass-provided
    location attributes, supporting EPSG:4258 and EPSG:25831.

    Location systems
    ----------------
    - EPSG:4258 (ETRS89 geographic)
    - EPSG:25831 (ETRS89 / UTM zone 31N)

    Attributes
    ----------
    meteocat_id : int
        Unique Meteocat identifier for the lightning event.
    peak_current : float
        Peak current of the lightning discharge, in kiloamperes.
    chi_squared : float
        Chi-squared value from location quality estimation.
    ellipse_major_axis : float
        Length of the confidence ellipse major axis.
    ellipse_minor_axis : float
        Length of the confidence ellipse minor axis.
    ellipse_angle : float
        Angle (degrees) of the ellipse orientation.
    number_of_sensors : int
        Number of sensors that detected the event (must be > 0).
    hit_ground : bool
        Whether the lightning stroke reached ground.
    multiplicity : int, optional
        Number of strokes in the same flash (may be ``None``).
    municipality_code : str, optional
        Code of the municipality where the event was located.
    x_25831, y_25831 : float
        Projected coordinates in EPSG:25831.
    x_4258, y_4258 : float
        Geographic coordinates in EPSG:4258.
    geometry_4258, geometry_25831 : shapely.geometry.Point or str
        Shapely point or WKT representation of the geometry.
    """
    # Metaclass location attributes
    __location__ = [
        {'epsg': 4258, 'validation': 'geographic', 'conversion': [
            {'src': 4258, 'dst': 4326},
            {'src': 4258, 'dst': 25831}
        ]},
        {'epsg': 25831, 'validation': False, 'conversion': False}
    ]
    # Type hint fot generated attributes by the metaclass
    x_25831: float
    y_25831: float
    x_4258: float
    y_4258: float
    geometry_4258: Union[str, Point]
    geometry_25831: Union[str, Point]
    # SQLAlchemy columns
    meteocat_id: Mapped[int] = mapped_column('meteocat_id', Integer, nullable=False)
    peak_current: Mapped[float] = mapped_column('meteocat_peak_current', Float, nullable=False)
    chi_squared: Mapped[float] = mapped_column('meteocat_chi_squared', Float, nullable=False)
    ellipse_major_axis: Mapped[float] = mapped_column('meteocat_ellipse_major_axis', Float, nullable=False)
    ellipse_minor_axis: Mapped[float] = mapped_column('meteocat_ellipse_minor_axis', Float, nullable=False)
    ellipse_angle: Mapped[float] = mapped_column('meteocat_ellipse_angle', Float, nullable=False)
    number_of_sensors: Mapped[Union[int, None]] = mapped_column('meteocat_number_of_sensors', Integer, nullable=False)
    hit_ground: Mapped[bool] = mapped_column('meteocat_hit_ground', Boolean, nullable=False, default=False)
    multiplicity: Mapped[int] = mapped_column('meteocat_multiplicity', Integer, nullable=True, default=None)
    municipality_code: Mapped[str] = mapped_column('meteocat_municipality_code', String, nullable=True, default=None)
    # SQLAlchemy Inheritance options
    __mapper_args__ = {
        "polymorphic_identity": "meteocat_lightning",
    }

    def __init__(self, **kwargs: Unpack[MeteocatLightningParams]) -> None:
        """
        Initialize a MeteocatLightning instance.

        Parameters
        ----------
        **kwargs : Unpack[MeteocatLightningParams]
            Keyword arguments matching the Meteocat-specific lightning parameters.
            See :class:`MeteocatLightningParams` for details.

        Raises
        ------
        ValueError
            If ``number_of_sensors`` is provided and is less than 1.
        """
        super().__init__(**kwargs)
        for key, value in kwargs.items():
            if hasattr(self, key):
                if (key == 'number_of_sensors') and (value < 1):
                    raise ValueError("Number of sensors must be a positive integer")
                setattr(self, key, value)

    def __iter__(self):
        """
        Yield key-value pairs of object attributes.

        Returns
        -------
        Iterator[Tuple[str, Any]]
            An iterator producing attribute names and values,
            allowing dict-like unpacking of the instance.

        Examples
        --------
        >>> lightning = MeteocatLightning(meteocat_id=1, peak_current=5.0, chi_squared=1.0,
        ...                               ellipse_major_axis=2.0, ellipse_minor_axis=1.0,
        ...                               ellipse_angle=45.0, number_of_sensors=3,
        ...                               hit_ground=True, x_4258=2.1, y_4258=41.3)
        >>> dict(lightning)["meteocat_id"]
        1
        """
        yield from super().__iter__()
        yield "meteocat_id", self.meteocat_id
        yield "peak_current", self.peak_current
        yield "multiplicity", self.multiplicity
        yield "chi_squared", self.chi_squared
        yield "ellipse_major_axis", self.ellipse_major_axis
        yield "ellipse_minor_axis", self.ellipse_minor_axis
        yield "ellipse_angle", self.ellipse_angle
        yield "number_of_sensors", self.number_of_sensors
        yield "hit_ground", self.hit_ground
        yield "municipality_code", self.municipality_code

    @staticmethod
    def object_hook_gisfire_api(dct: Dict[str, Any]) -> Union[MeteocatLightning, Dict[str, Any], None]:
        """
        Decode a GisFIRE API JSON dictionary into a MeteocatLightning object.

        This method is intended to be passed as the ``object_hook``
        argument of :func:`json.loads`.

        Parameters
        ----------
        dct : dict
            A dictionary parsed from JSON by the standard library.

        Returns
        -------
        MeteocatLightning or dict or None
            - A :class:`MeteocatLightning` instance if all required
              fields are present.
            - A dictionary if the keys ``lightning`` and ``distance``
              are detected (used for nested structures).
            - ``None`` if the dictionary does not match known formats.

        Examples
        --------
        >>> import json
        >>> json_str = '{"meteocat_id": "1", "peak_current": "5.0", "multiplicity": "1", ... }'
        >>> obj = json.loads(json_str, object_hook=MeteocatLightning.object_hook_gisfire_api)
        >>> isinstance(obj, MeteocatLightning)
        True
        """
        if all(k in dct for k in ('lightning', 'distance')):
            return dct
        if all(k in dct for k in ("meteocat_id", "peak_current", "multiplicity", "chi_squared",
                                  "ellipse_major_axis", "ellipse_minor_axis", "ellipse_angle",
                                  "number_of_sensors", "hit_ground", "municipality_code", "id",
                                  "data_provider", "x_25831", "y_25831", "x_4258", "y_4258",
                                  "date_time")):
            lightning = MeteocatLightning()
            lightning.meteocat_id = int(dct['meteocat_id'])
            lightning.peak_current = float(dct['peak_current'])
            lightning.multiplicity = int(dct['multiplicity']) if dct['multiplicity'] is not None else None
            lightning.chi_squared = float(dct['chi_squared'])
            lightning.ellipse_major_axis = float(dct['ellipse_major_axis'])
            lightning.ellipse_minor_axis = float(dct['ellipse_minor_axis'])
            lightning.ellipse_angle = float(dct['ellipse_angle'])
            lightning.number_of_sensors = int(dct['number_of_sensors'])
            lightning.hit_ground = bool(dct['hit_ground'])
            lightning.municipality_code = dct['municipality_code']
            lightning.id = int(dct['id'])
            lightning.data_provider_name = dct['data_provider']
            lightning.x_4258 = float(dct['x_4258'])
            lightning.y_4258 = float(dct['y_4258'])
            lightning.date_time = datetime.datetime.strptime(dct['date_time'], "%Y-%m-%dT%H:%M:%S.%f%z")
            return lightning
        return None  # pragma: no cover


