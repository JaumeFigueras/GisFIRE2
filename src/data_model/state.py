#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import Integer
from sqlalchemy import DateTime

from src.data_model import Base
from src.data_model.mixins.time_stamp import TimeStampMixIn

from typing import Optional
from typing import Tuple
from typing import Iterator
from typing import Any
from typing import Unpack
from typing import TypedDict
from typing import NotRequired

class StateParams(TypedDict):
    """Typed dictionary specifying the parameters required to initialize a State.

    Attributes
    ----------
    state_valid_from_utc_date_time : datetime.datetime
        UTC timestamp indicating when the state becomes valid.
    state_valid_until_utc_date_time : datetime.datetime, optional
        UTC timestamp indicating when the state is no longer valid. If not
        provided, the state is considered open-ended.
    """
    state_valid_from_utc_date_time: datetime.datetime
    state_valid_until_utc_date_time: NotRequired[datetime.datetime]

class State(Base, TimeStampMixIn):
    """Abstract SQLAlchemy model for representing the temporal validity of a state.

    This class is designed as an abstract base to be inherited by other
    SQLAlchemy models that require state tracking with start and end validity
    timestamps.

    Attributes
    ----------
    state_id : int
        Primary key of the state record.
    state_valid_from_utc_date_time : datetime.datetime
        UTC datetime indicating when the state became valid.
    state_valid_until_utc_date_time : datetime.datetime or None
        UTC datetime indicating when the state is no longer valid.
        If ``None``, the state is still valid.
    """
    # SQLAlchemy columns
    __abstract__ = True  # SQLAlchemy directive for abstract data_model
    state_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    state_valid_from_utc_date_time: Mapped[datetime.datetime] = mapped_column('state_valid_from_utc_date_time', DateTime(timezone=True), nullable=False)
    state_valid_until_utc_date_time: Mapped[Optional[datetime.datetime]] = mapped_column('state_valid_until_utc_date_time', DateTime(timezone=True), nullable=True)

    def __init__(self, **kwargs: Unpack[StateParams]) -> None:
        """Initialize a new State instance.

        Parameters
        ----------
        **kwargs : Unpack[StateParams]
            Keyword arguments corresponding to `StateParams` keys, used
            to populate the instance attributes.
        """
        super().__init__()
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def __iter__(self) -> Iterator[Tuple[str, Any]]:
        """Iterate over the state attributes as key-value pairs.

        Yields
        ------
        tuple of (str, Any)
            Pairs representing the attribute name and its formatted value.
            Datetimes are formatted as ISO 8601 strings with microseconds and
            UTC offset. If `state_valid_to_utc_date_time` is ``None``, it yields
            ``None`` instead of a string.
        """
        yield 'state_id', self.state_id
        yield 'state_valid_from_utc_date_time', self.state_valid_from_utc_date_time.strftime("%Y-%m-%dT%H:%M:%S.%f%z")
        yield 'state_valid_until_utc_date_time', self.state_valid_until_utc_date_time.strftime("%Y-%m-%dT%H:%M:%S.%f%z") if self.state_valid_until_utc_date_time is not None else None

