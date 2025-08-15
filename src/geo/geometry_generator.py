#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Any

class PointGeometryGenerator(object):
    """
    Generates a WKT point geometry string for a given object
    based on its X and Y coordinate attributes and EPSG code.

    This helper is typically used in ORM models to automatically
    update the geometry column when coordinates change.
    """

    def __init__(self, src_x_attr: str, src_y_attr: str, src_epsg: str, src_geom_attr: str) -> None:
        """
        Initialize the PointGeometryGenerator.

        Parameters
        ----------
        src_x_attr : str
            Name of the attribute containing the X coordinate.
        src_y_attr : str
            Name of the attribute containing the Y coordinate.
        src_epsg : str
            EPSG code for the coordinate reference system.
        src_geom_attr : str
            Name of the attribute where the generated geometry
            string should be stored.
        """
        self.src_x_attr = src_x_attr
        self.src_y_attr = src_y_attr
        self.src_epsg = src_epsg
        self.src_geom_attr = src_geom_attr

    def generate(self, obj: Any):
        """
        Generate and set the WKT point geometry string on the given object.

        If both X and Y coordinates are present, sets the target geometry
        attribute to a WKT ``POINT`` string prefixed with the ``SRID``.
        Otherwise, sets the geometry attribute to ``None``.

        Parameters
        ----------
        obj : Any
            Object containing the X, Y, and geometry attributes.

        Examples
        --------
        >>> class Dummy:
        ...     x = 1.23
        ...     y = 4.56
        ...     geom = None
        ...
        >>> gen = PointGeometryGenerator('x', 'y', '4326', 'geom')
        >>> dummy = Dummy()
        >>> gen.generate(dummy)
        >>> dummy.geom
        'SRID=4326;POINT(1.23 4.56)'
        """
        if (getattr(obj, self.src_x_attr) is not None) and (getattr(obj, self.src_y_attr) is not None):
            setattr(obj, self.src_geom_attr, "SRID={2:};POINT({0:} {1:})".format(getattr(obj, self.src_x_attr), getattr(obj, self.src_y_attr), self.src_epsg))
        else:
            setattr(obj, self.src_geom_attr, None)

