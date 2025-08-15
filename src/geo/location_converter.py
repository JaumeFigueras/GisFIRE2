#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pyproj import Transformer

from typing import Any
from typing import Optional


class PointLocationConverter:
    """
    Converts point coordinates between two coordinate reference systems (CRS)
    and generates corresponding WKT geometry strings.

    This helper is typically used in ORM models to keep both source and
    destination coordinates, as well as their geometries, in sync.
    """

    def __init__(self, src_x_attr: str, src_y_attr: str, src_epsg: str, src_geom_attr: str, dst_x_attr: Optional[str] = None,
                 dst_y_attr: Optional[str] = None, dst_epsg: Optional[str] = None, dst_geom_attr: Optional[str] = None) -> None:
        """
        Initialize the PointLocationConverter.

        Parameters
        ----------
        src_x_attr : str
            Name of the attribute containing the source X coordinate.
        src_y_attr : str
            Name of the attribute containing the source Y coordinate.
        src_epsg : str
            EPSG code for the source CRS.
        src_geom_attr : str
            Name of the attribute where the generated source geometry string is stored.
        dst_x_attr : str, optional
            Name of the attribute containing the destination X coordinate.
        dst_y_attr : str, optional
            Name of the attribute containing the destination Y coordinate.
        dst_epsg : str, optional
            EPSG code for the destination CRS.
        dst_geom_attr : str, optional
            Name of the attribute where the generated destination geometry string is stored.
        """
        self.src_x_attr = src_x_attr
        self.src_y_attr = src_y_attr
        self.src_epsg = src_epsg
        self.src_geom_attr = src_geom_attr
        self.dst_x_attr = dst_x_attr
        self.dst_y_attr = dst_y_attr
        self.dst_epsg = dst_epsg
        self.dst_geom_attr = dst_geom_attr

    def convert(self, obj: Any):
        """
        Convert the source location to the destination CRS and generate geometry strings.

        This method:
        - Reads the source X and Y coordinates from the object.
        - Generates a WKT geometry string for the source location.
        - Converts the coordinates to the destination CRS using `pyproj.Transformer`.
        - Sets the destination X and Y coordinates.
        - Generates a WKT geometry string for the destination location.

        If any of the source coordinates are missing, both source and destination
        attributes are set to ``None``.

        Parameters
        ----------
        obj : Any
            Object containing the coordinate and geometry attributes.

        Examples
        --------
        >>> class Dummy:
        ...     x1 = 2.0
        ...     y1 = 45.0
        ...     geom1 = None
        ...     x2 = None
        ...     y2 = None
        ...     geom2 = None
        ...
        >>> conv = PointLocationConverter(
        ...     'x1', 'y1', '4326', 'geom1',
        ...     'x2', 'y2', '3857', 'geom2'
        ... )
        >>> dummy = Dummy()
        >>> conv.convert(dummy)
        >>> dummy.geom1
        'SRID=4326;POINT(2.0 45.0)'
        >>> dummy.geom2.startswith('SRID=3857;POINT')
        True
        """
        if hasattr(obj, self.src_x_attr) and hasattr(obj, self.src_y_attr) and hasattr(obj, self.dst_x_attr) and hasattr(obj, self.dst_y_attr):
            if getattr(obj, self.src_x_attr) is None or getattr(obj, self.src_y_attr) is None:
                setattr(obj, self.dst_x_attr, None)
                setattr(obj, self.dst_y_attr, None)
                setattr(obj, self.src_geom_attr, None)
                setattr(obj, self.dst_geom_attr, None)
                return
        if (getattr(obj, self.src_x_attr) is not None) and (getattr(obj, self.src_y_attr) is not None):
            setattr(obj, self.src_geom_attr, "SRID={2:};POINT({0:} {1:})".format(getattr(obj, self.src_x_attr), getattr(obj, self.src_y_attr), self.src_epsg))
            transformer = Transformer.from_crs("EPSG:{0:}".format(self.src_epsg), "EPSG:{0:}".format(self.dst_epsg), always_xy=True)
            tmp_x, tmp_y = transformer.transform(getattr(obj, self.src_x_attr), getattr(obj, self.src_y_attr))
            setattr(obj, self.dst_x_attr, tmp_x)
            setattr(obj, self.dst_y_attr, tmp_y)
            setattr(obj, self.dst_geom_attr, "SRID={2};POINT({0:} {1:})".format(tmp_x, tmp_y, self.dst_epsg))


