#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import statistics
import math
import shapely

# General imports
from sqlalchemy.orm import mapped_column
from geoalchemy2 import shape
from geoalchemy2 import Geometry
from geoalchemy2.elements import WKBElement
from shapely.geometry import MultiPoint
from pyproj import Transformer

# Local project imports
from src.data_model.thunderstorm import Thunderstorm
from src.data_model.thunderstorm import ThunderstormParams
from src.data_model import Base

# Typing hints imports
from sqlalchemy.orm import Mapped
from typing import Optional
from typing import Tuple
from typing import Unpack
from typing import NotRequired
from typing import Union
from shapely.geometry import Point
from shapely.geometry import Polygon

class MeteocatThunderstormParams(ThunderstormParams):
    x_25831: NotRequired[float]
    y_25831: NotRequired[float]
    x_4258: NotRequired[float]
    y_4258: NotRequired[float]

class MeteocatThunderstorm(Thunderstorm):
    # Metaclass location attributes
    __location__ = [
        {'epsg': 4258, 'validation': 'geographic', 'conversion': [
            {'src': 4258, 'dst': 4326},
            {'src': 4258, 'dst': 25831}
        ], 'nullable': True},
        {'epsg': 25831, 'validation': False, 'conversion': False, 'nullable': True},
    ]
    # Type hint fot generated attributes by the metaclass
    x_25831: float
    y_25831: float
    x_4258: float
    y_4258: float
    geometry_4258: Union[str, Point]
    geometry_25831: Union[str, Point]
    # Class data
    _convex_hull_4258: Mapped[Optional[WKBElement]] = mapped_column('convex_hull_4258', Geometry(geometry_type='POLYGON', srid=int(4258)), nullable=True)
    _convex_hull_25831: Mapped[Optional[WKBElement]] = mapped_column('convex_hull_25831', Geometry(geometry_type='POLYGON', srid=int(25831)), nullable=True)
    # Inheritance
    __mapper_args__ = {
        "polymorphic_identity": "meteocat_thunderstorm",
    }

    def __init__(self, **kwargs: Unpack[MeteocatThunderstormParams]) -> None:
        """
        Initializes a Thunderstorm instance.

        This constructor delegates initialization to the base classes via `super()`.
        It does not perform any additional setup beyond inherited behavior.

        Notes
        -----
        The actual initialization must be done attribute by attribute after object creation.
        """
        super().__init__(**kwargs)
        for key, value in kwargs.items():
            if hasattr(self, key) and not Base.is_defined_in_parents(MeteocatThunderstorm, key):
                setattr(self, key, value)

    @property
    def convex_hull_4258(self) -> Polygon:
        """
        Converts the stored geometry to a Shapely Polygon object.

        Returns
        -------
        shapely.geometry.Polygon
            A Shapely representation of the region's geometry.
        """
        return shape.to_shape(self._convex_hull_4258)

    @property
    def convex_hull_25831(self) -> Polygon:
        """
        Converts the stored geometry to a Shapely Polygon object.

        Returns
        -------
        shapely.geometry.Polygon
            A Shapely representation of the region's geometry.
        """
        return shape.to_shape(self._convex_hull_25831)

    @property
    def location_4258(self) -> Tuple[float, float]:
        x, y = zip(*[(lightning.x_4258, lightning.y_4258) for lightning in self.lightnings])
        return statistics.fmean(x), statistics.fmean(y)

    @property
    def location_25831(self) -> Tuple[float, float]:
        x, y = zip(*[(lightning.x_25831, lightning.y_25831) for lightning in self.lightnings])
        return statistics.fmean(x), statistics.fmean(y)


    def compute_location(self):
        x, y = zip(*[(lightning.x_4258, lightning.y_4258) for lightning in self.lightnings])
        self.x_4258 = statistics.fmean(x)
        self.y_4258 = statistics.fmean(y)
        transformer_25831 = Transformer.from_crs("EPSG:4258", "EPSG:25831", always_xy=True)
        transformer_4326 = Transformer.from_crs("EPSG:4258", "EPSG:4326", always_xy=True)
        self.x_25831, self.y_25831 = transformer_25831.transform(self.x_4258, self.y_4258)
        self.x_4326, self.y_4326 = transformer_4326.transform(self.x_4258, self.y_4258)

    def compute_travelled_distance_cardinal_direction(self):
        count = len(self.lightnings)
        if count == 1:
            self.thunderstorm_travelled_distance = 0
            self.thunderstorm_cardinal_direction = 0
            return
        ten_percent = math.ceil(count * 0.1)
        first_ten_percent_lightnings = self.lightnings[:ten_percent]
        last_ten_percent_lightnings = self.lightnings[-ten_percent:]
        x, y = zip(*[(lightning.x_25831, lightning.y_25831) for lightning in first_ten_percent_lightnings])
        first_x = statistics.fmean(x)
        first_y = statistics.fmean(y)
        x, y = zip(*[(lightning.x_25831, lightning.y_25831) for lightning in last_ten_percent_lightnings])
        last_x = statistics.fmean(x)
        last_y = statistics.fmean(y)
        dx = last_x - first_x
        dy = last_y - first_y
        #distance
        self.thunderstorm_travelled_distance = math.sqrt(dx ** 2 + dy ** 2)
        # bearing (0° = north, 90° = east)
        self.thunderstorm_cardinal_direction = (math.degrees(math.atan2(dx, dy)) + 360) % 360

    def compute_speed(self):
        min_date = self.lightnings[0].lightning_utc_date_time
        max_date = self.lightnings[-1].lightning_utc_date_time
        seconds = (max_date - min_date).total_seconds()
        if seconds <= 0:
            self.thunderstorm_speed = 0
        else:
            self.thunderstorm_speed = self.thunderstorm_travelled_distance / (max_date - min_date).total_seconds()

    def compute_convex_hull(self):
        convex_hull = shapely.convex_hull(MultiPoint([(l.x_4258, l.y_4258) for l in self.lightnings]))
        if isinstance(convex_hull, shapely.geometry.Polygon):
            self._convex_hull_4258 = "SRID=4258;" + shapely.to_wkt(convex_hull)
            transformer_25831 = Transformer.from_crs("EPSG:4258", "EPSG:25831", always_xy=True)
            transformer_4326 = Transformer.from_crs("EPSG:4258", "EPSG:4326", always_xy=True)
            self._convex_hull_25831 = "SRID=25831;" + shapely.to_wkt(shapely.transform(convex_hull, transformer_25831.transform, interleaved=False))
            self._convex_hull_4326 = "SRID=4326;" + shapely.to_wkt(shapely.transform(convex_hull, transformer_4326.transform, interleaved=False))
        else:
            self._convex_hull_4258 = None
            self._convex_hull_4326 = None
            self._convex_hull_25831 = None

    def on_lightnings_change(self):
        # self.lightnings.sort(key=lambda lightning: lightning.date_time)
        self.compute_location()
        self.compute_lightnings_per_minute()
        self.compute_travelled_distance_cardinal_direction()
        self.compute_speed()
        self.compute_convex_hull()
        self.thunderstorm_utc_date_time_start = self.lightnings[0].lightning_utc_date_time
        self.thunderstorm_utc_date_time_end = self.lightnings[-1].lightning_utc_date_time
        self.thunderstorm_number_of_lightnings = len(self.lightnings)




