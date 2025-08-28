#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# General imports
import datetime
import statistics
import pytz

from sqlalchemy import Integer
from sqlalchemy import Float
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from geoalchemy2 import shape
from geoalchemy2 import Geometry
from geoalchemy2.elements import WKBElement

# Local project imports
from src.data_model import Base
from src.data_model.mixins.location import LocationMixIn
from src.data_model.mixins.time_stamp import TimeStampMixIn
from src.data_model.lightning import Lightning
from src.data_model.thunderstorm_experiment import ThunderstormExperiment

# Typing hints imports
from sqlalchemy.orm import Mapped
from typing import List
from typing import Optional
from typing import Union
from typing import Tuple
from typing import TypedDict
from typing import Unpack
from typing import NotRequired
from shapely.geometry import Point
from shapely.geometry import Polygon


class ThunderstormLightningAssociation(Base):
    """
    Association table linking thunderstorms and lightning events.

    This class models the many-to-many relationship between thunderstorms and
    lightning strikes. Each record represents a single association between a
    thunderstorm and a lightning event, allowing for detailed tracking and analysis
    of how lightning activity corresponds to storm occurrences.

    Attributes
    ----------
    thunderstorm_id : int
        Foreign key referencing the associated thunderstorm.
    lightning_id : int
        Foreign key referencing the associated lightning event.
    lightning : :class:`~src.data_model.lightning.Lightning`
        The lightning event linked to the thunderstorm.
    thunderstorm : :class:`~src.data_model.thunderstorm.Thunderstorm`
        The thunderstorm linked to the lightning event.

    Notes
    -----
    This table uses a composite primary key (`thunderstorm_id`, `lightning_id`)
    to uniquely identify each association. It enables efficient querying of
    lightning events per thunderstorm and vice versa.

    See Also
    --------
    :class:`~src.data_model.thunderstorm.Thunderstorm`
        Model representing individual thunderstorm records.
    :class:`~src.data_model.lightning.Lightning`
        Model representing individual lightning strike records.
    """
    __tablename__ = "thunderstorm_lightning_association"
    thunderstorm_id: Mapped[int] = mapped_column(ForeignKey("thunderstorm.thunderstorm_id"), primary_key=True)
    lightning_id: Mapped[int] = mapped_column(ForeignKey("lightning.lightning_id"), primary_key=True)
    lightning: Mapped["Lightning"] = relationship(back_populates="thunderstorm_associations", viewonly=True)  # type: ignore
    thunderstorm: Mapped["Thunderstorm"] = relationship(back_populates="lightning_associations", viewonly=True)

class ThunderstormParams(TypedDict):
    """
    Typed dictionary for initializing a :class:`Thunderstorm`.

    This dictionary defines the expected keyword arguments that can be
    passed into the `Thunderstorm` constructor.

    Attributes
    ----------
    x_4326 : float, optional
        Longitude coordinate of the storm location in EPSG:4326.
    y_4326 : float, optional
        Latitude coordinate of the storm location in EPSG:4326.
    date_time_start : datetime.datetime
        Start time of the thunderstorm event.
    date_time_end : datetime.datetime
        End time of the thunderstorm event.
    lightnings_per_minute : float, optional
        Frequency of lightning strikes per minute during the storm.
    travelled_distance : float, optional
        Distance traveled by the storm in meters.
    cardinal_direction : float, optional
        Direction of storm movement in degrees.
    speed : float, optional
        Speed of storm movement in m/s.
    thunderstorm_experiment : ThunderstormExperiment or int
        Identifier of the associated thunderstorm experiment.
    """
    x_4326: NotRequired[float]
    y_4326: NotRequired[float]
    thunderstorm_utc_date_time_start: NotRequired[datetime.datetime]
    thunderstorm_utc_date_time_end: NotRequired[datetime.datetime]
    thunderstorm_lightnings_per_minute: NotRequired[float]
    thunderstorm_travelled_distance: NotRequired[float]
    thunderstorm_cardinal_direction: NotRequired[float]
    thunderstorm_speed: NotRequired[float]
    thunderstorm_number_of_lightnings: NotRequired[int]
    thunderstorm_experiment: Union[ThunderstormExperiment, int]


class Thunderstorm(Base, LocationMixIn, TimeStampMixIn):
    """
    Represents a thunderstorm event with spatial, temporal, and physical characteristics.

    This class models a thunderstorm as a spatiotemporal phenomenon, capturing its
    location, duration, movement, and intensity. It integrates geographic metadata
    through `LocationMixIn`, temporal metadata via `DateTimeMixIn`, and timestamping
    through `TimeStampMixIn`. The class also supports relationships to lightning events
    and experimental contexts.

    Attributes
    ----------
    thunderstorm_id : int
        Unique identifier for the thunderstorm record.
    lightnings_per_minute : float
        Frequency of lightning strikes per minute during the storm.
    thunderstorm_travelled_distance : float
        Distance traveled by the storm in meters.
    thunderstorm_cardinal_direction : float
        Direction of storm movement in degrees (0 degrees is North, 90 is East, 180 is South, 270 is West).
    thunderstorm_speed : float
        Speed of storm movement in m/s.
    _convex_hull_4326 : WKBElement
        Geometry representing the convex hull of the storm in EPSG:4326.
    x_4326 : float
        Longitude coordinate of the storm location in EPSG:4326 (generated by metaclass).
    y_4326 : float
        Latitude coordinate of the storm location in EPSG:4326 (generated by metaclass).
    geometry_4326 : Union[str, Point]
        Geometry representation of the storm location in EPSG:4326 (generated by metaclass).
    date_time_start : datetime.datetime
        Start time of the thunderstorm event (generated by metaclass).
    tzinfo_date_time_start : str
        Timezone information for the start time (generated by metaclass).
    date_time_end : datetime.datetime
        End time of the thunderstorm event (generated by metaclass).
    tzinfo_date_time_end : str
        Timezone information for the end time (generated by metaclass).
    thunderstorm_experiment_id : int
        Foreign key linking to the associated thunderstorm experiment.
    thunderstorm_experiment : ThunderstormExperiment
        Relationship to the parent experiment that includes this thunderstorm.
    lightnings : List[Lightning]
        Many-to-many relationship to associated lightning events.
    lightning_associations : List[ThunderstormLightningAssociation]
        Association objects linking this thunderstorm to lightning events.
    ts : datetime.datetime
        Insertion and update time in the database (generated by metaclass).

    Notes
    -----
    - The location and date attributes are dynamically generated by metaclasses.
    - Geometry fields use GeoAlchemy2 and are stored in WKB format.
    - Relationships to lightning events support both direct and association-based access.
    """
    # Metaclass location attributes
    __location__ = [
        {'epsg': 4326, 'validation': 'geographic', 'conversion': False, 'nullable': False},
    ]
    # Type hint for generated attributes by the metaclass
    x_4326: float
    y_4326: float
    geometry_4326: Union[str, Point]
    # Class data
    __tablename__ = "thunderstorm"
    thunderstorm_id: Mapped[int] = mapped_column('thunderstorm_id', Integer, primary_key=True, autoincrement=True)
    thunderstorm_utc_date_time_start: Mapped[datetime.datetime] = mapped_column('thunderstorm_utc_date_time_start', DateTime(timezone=True), nullable=False)
    thunderstorm_utc_date_time_end: Mapped[datetime.datetime] = mapped_column('thunderstorm_utc_date_time_end', DateTime(timezone=True), nullable=False)
    thunderstorm_lightnings_per_minute: Mapped[float] = mapped_column('thunderstorm_lightnings_per_minute', Float)
    thunderstorm_travelled_distance: Mapped[float] = mapped_column('thunderstorm_travelled_distance', Float)
    thunderstorm_cardinal_direction: Mapped[float] = mapped_column('thunderstorm_cardinal_direction', Float)
    thunderstorm_speed: Mapped[float] = mapped_column('thunderstorm_speed', Float)
    thunderstorm_number_of_lightnings: Mapped[int] = mapped_column('thunderstorm_number_of_lightnings', Integer)
    _convex_hull_4326: Mapped[Optional[WKBElement]] = mapped_column('convex_hull_4326', Geometry(geometry_type='POLYGON', srid=int(4326)), nullable=True)
    # Relations
    thunderstorm_experiment_id: Mapped[int] = mapped_column('thunderstorm_experiment_id', ForeignKey('thunderstorm_experiment.thunderstorm_experiment_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    thunderstorm_experiment: Mapped["ThunderstormExperiment"] = relationship(back_populates="thunderstorms")
    # many-to-many relationship to Child, bypassing the `Association` class
    lightnings: Mapped[List["Lightning"]] = relationship(secondary="thunderstorm_lightning_association", back_populates="thunderstorms", order_by=Lightning.lightning_utc_date_time)
    # association between Parent -> Association -> Child
    lightning_associations: Mapped[List["ThunderstormLightningAssociation"]] = relationship(back_populates="thunderstorm", viewonly=True)
    # Inheritance
    type: Mapped[str]
    __mapper_args__ = {
        "polymorphic_identity": "thunderstorm",
        "polymorphic_on": "type",
    }

    def __init__(self, **kwargs: Unpack[ThunderstormParams]) -> None:
        """
        Initialize a Thunderstorm instance.

        Parameters
        ----------
        **kwargs : ThunderstormParams
            Keyword arguments matching the thunderstorm schema.

        Notes
        -----
        - Only keys matching existing attributes are set.
        - Extra/unrecognized keys are ignored.
        """
        super().__init__()
        for key, value in kwargs.items():
            if hasattr(self, key) and not Base.is_defined_in_parents(Thunderstorm, key):
                if (key == "thunderstorm_experiment") and (isinstance(value, int)):
                    self.thunderstorm_experiment_id = value
                else:
                    setattr(self, key, value)

    @property
    def convex_hull_4326(self) -> Polygon:
        """
        Converts the stored geometry to a Shapely Polygon object.

        Returns
        -------
        shapely.geometry.Polygon
            A Shapely representation of the region's geometry.
        """
        return shape.to_shape(self._convex_hull_4326)

    @property
    def location_4326(self) -> Tuple[float, float]:
        x, y = zip(*[(lightning.x_4326, lightning.y_4326) for lightning in self.lightnings])
        return statistics.fmean(x), statistics.fmean(y)

    @property
    def average_utc_date_time(self) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(
            statistics.fmean([l.lightning_utc_date_time.timestamp() for l in self.lightnings]),
            tz=pytz.UTC
        )

    def compute_location(self):
        x, y = zip(*[(lightning.x_4326, lightning.y_4326) for lightning in self.lightnings])
        self.x_4326 = statistics.fmean(x)
        self.y_4326 = statistics.fmean(y)

    def compute_lightnings_per_minute(self):
        # assuming it is an ordered list
        min_date = self.lightnings[0].lightning_utc_date_time
        max_date = self.lightnings[-1].lightning_utc_date_time
        count = len(self.lightnings)
        number_of_minutes = max(1., (max_date - min_date).total_seconds() / 60.)
        self.thunderstorm_lightnings_per_minute = count / number_of_minutes

