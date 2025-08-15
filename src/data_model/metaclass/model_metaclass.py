#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import pytz

from sqlalchemy import DateTime, String
from sqlalchemy import Float
from sqlalchemy.orm import DeclarativeMeta
from sqlalchemy.orm import mapped_column
from geoalchemy2 import shape
from geoalchemy2 import Geometry
from shapely.geometry import Point

from src.geo.location_converter import PointLocationConverter
from src.geo.geometry_generator import PointGeometryGenerator

from typing import Optional
from typing import List
from typing import Union
from typing import Any


class ModelMeta(DeclarativeMeta):
    def __init__(cls, name, bases, dct):
        """
        Metaclass constructor for SQLAlchemy ORM models.

        Dynamically generates:

        - Location properties (x, y, geometry) with validation and conversion.
        - DateTime properties with timezone handling.
        - Default getter/setter properties.

        Parameters
        ----------
        name : str
            Class name being created.
        bases : tuple
            Base classes of the new class.
        dct : dict
            Class attributes and methods dictionary.

        Notes
        -----
        This method internally defines:

        - ``property_factory_xy()`` which handles location attributes.
        - ``property_factory_geometry()`` which handles geometry attributes bound with shapely and WKT.
        - ``property_factory_datetime()`` which handles datetime attributes with time zone handling.
        """

        def property_factory_xy(attr: str, generator_attr: Optional[str] = None,
                                converter_attrs: Optional[List[str]] = None,
                                validator: Optional[str] = None) -> property:
            """
            Factory to create a property for X or Y location coordinates.

            This includes optional validation, geometry generation, and conversions.

            Parameters
            ----------
            attr : str
                Attribute name (without underscore prefix).
            generator_attr : str, optional
                Name of the geometry generator attribute.
            converter_attrs : list of str, optional
                Names of location converter attributes.
            validator : str, optional
                Validation type ('longitude', 'latitude', or None).

            Returns
            -------
            property
                A property object with getter and setter.
            """

            def getter(self) -> float:
                """
                Get the X or Y coordinate.

                Returns
                -------
                float
                    The coordinate value.
                """
                return getattr(self, '_' + attr)

            def setter(self, value) -> None:
                """
                Set the X or Y coordinate.

                Performs validation, geometry regeneration, and optional coordinate conversion.

                Parameters
                ----------
                value : float
                    New coordinate value.

                Raises
                ------
                ValueError
                    If the value fails longitude/latitude validation.
                """
                if validator is not None and value is not None:
                    if validator == 'longitude':
                        if not (-180 <= value <= 180):
                            raise ValueError("Longitude out of range")
                    elif validator == 'latitude':
                        if not (-90 <= value <= 90):
                            raise ValueError("Latitude out of range")
                setattr(self, '_' + attr, value)
                if generator_attr is not None:
                    generator: PointGeometryGenerator = getattr(self, generator_attr)
                    generator.generate(self)
                if converter_attrs is not None:
                    for converter_attr in converter_attrs:
                        converter: PointLocationConverter = getattr(self, converter_attr)
                        converter.convert(self)

            return property(getter, setter)

        def property_factory_geometry(attr) -> property:
            """
            Factory to create a read-only geometry property.

            Parameters
            ----------
            attr : str
                Geometry attribute name (without underscore prefix).

            Returns
            -------
            property
                A property object with getter and no-op setter.
            """
            def getter(self) -> Union[str, Point, None]:
                """
                Get the geometry.

                Returns
                -------
                str or shapely.geometry.Point or None
                    Geometry as WKT string, Shapely Point, or None.
                """
                geometry = getattr(self, '_' + attr)
                if geometry is not None:
                    if isinstance(geometry, str):
                        return geometry
                    else:
                        return shape.to_shape(geometry)
                return None

            def setter(self, value) -> None:
                """
                Set the geometry.

                Notes
                -----
                This is a no-op because geometry is auto-generated
                from X/Y coordinates.
                """
                pass

            return property(getter, setter)

        def property_factory_datetime(attr: str) -> property:
            """
            Factory to create a DateTime property with timezone support.

            Parameters
            ----------
            attr : str
                Name of the protected DateTime attribute.

            Returns
            -------
            property
                A property object with getter and setter.
            """

            def getter(self) -> datetime.datetime:
                """
                Get the DateTime value.

                Returns
                -------
                datetime.datetime
                    The datetime value.
                """
                return getattr(self, attr)

            def setter(self, value) -> None:
                """
                Set the DateTime value.

                Ensures timezone info is present and stores the associated
                timezone in a separate column.

                Parameters
                ----------
                value : datetime.datetime
                    New datetime value.

                Raises
                ------
                ValueError
                    If datetime has no tzinfo.
                """
                if value is not None:
                    if value.tzinfo is None:
                        raise ValueError('Date must contain timezone information')
                    setattr(self, '_tzinfo' + attr, str(value.tzinfo))
                    setattr(self, attr, value)
                else:
                    setattr(self, '_tzinfo' + attr, None)
                    setattr(self, attr, None)

            return property(getter, setter)

        def property_factory_default(attr: str) -> property:
            """
            Factory to create a property with a default getter and setter.

            Parameters
            ----------
            attr : str
                Attribute name.

            Returns
            -------
            property
                A property object with getter and setter.
            """

            def getter(self) -> Any:
                """
                Get the attribute value.

                Returns
                -------
                Any
                    Attribute value.
                """
                return getattr(self, attr)

            def setter(self, value: Any) -> None:
                """
                Set the attribute value.

                Parameters
                ----------
                value : Any
                    New attribute value.
                """
                setattr(self, attr, value)

            return property(getter, setter)

        # Handle location properties
        if '__location__' in dct:
            location = dct.pop('__location__', [])
            for col_def in location:
                epsg = str(col_def['epsg'])
                validation = col_def['validation']
                conversion = col_def['conversion']
                # Base columns
                setattr(cls, '_x_' + epsg, mapped_column('x_' + epsg, Float, nullable=False))
                setattr(cls, '_y_' + epsg, mapped_column('y_' + epsg, Float, nullable=False))
                setattr(cls, '_geometry_' + epsg, mapped_column('geometry_' + epsg, Geometry(geometry_type='POINT', srid=int(epsg)), nullable=False))
                # Geometry property
                setattr(cls, 'geometry_' + epsg, property_factory_geometry('geometry_' + epsg))
                # Geometry generator
                generator = PointGeometryGenerator('_x_' + epsg, '_y_' + epsg,  epsg, '_geometry_' + epsg)
                setattr(cls, 'geometry_generator_' + epsg, generator)
                # Coordinate converters
                converter_attrs = None
                if conversion:
                    converter_attrs = list()
                    for conversion_parameters in conversion:
                        src = str(conversion_parameters['src'])
                        dst = str(conversion_parameters['dst'])
                        converter = PointLocationConverter('_x_' + src, '_y_' + src,  src, '_geometry_' + src, '_x_' + dst,
                                                      '_y_' + dst,  dst, '_geometry_' + dst)
                        setattr(cls, 'geometry_converter_' + src + '_' + dst, converter)
                        converter_attrs.append('geometry_converter_' + src + '_' + dst)
                # Coordinate properties with optional validation
                if validation == 'geographic':
                    setattr(cls, 'x_' + epsg, property_factory_xy('x_' + epsg, 'geometry_generator_' + epsg, converter_attrs, 'longitude'))
                    setattr(cls, 'y_' + epsg, property_factory_xy('y_' + epsg, 'geometry_generator_' + epsg, converter_attrs, 'latitude'))
                else:
                    setattr(cls, 'x_' + epsg, property_factory_xy('x_' + epsg, 'geometry_generator_' + epsg, converter_attrs))
                    setattr(cls, 'y_' + epsg, property_factory_xy('y_' + epsg, 'geometry_generator_' + epsg, converter_attrs))

        # Handle datetime properties
        if '__date__' in dct:
            dates = dct.pop('__date__', [])
            for attribute in dates:
                attribute_name = column_name = attribute['name']
                protected_attribute_name = '_' + attribute_name
                nullable = attribute['nullable']
                # DateTime column
                setattr(cls, protected_attribute_name, mapped_column(column_name, DateTime(timezone=True), nullable=nullable))
                setattr(cls, '_tzinfo' + protected_attribute_name, mapped_column('tzinfo_' + column_name, String, nullable=nullable))
                # Properties
                setattr(cls, attribute_name, property_factory_datetime(protected_attribute_name))
                setattr(cls, 'tzinfo_' + attribute_name, property_factory_default('_tzinfo' + protected_attribute_name))

        super().__init__(name, bases, dct)
