#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import pytz

from sqlalchemy import DateTime
from sqlalchemy import func
from sqlalchemy.orm import declarative_mixin
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


@declarative_mixin
class TimeStampMixIn(object):
    """
    Mixin for adding a timestamp column to SQLAlchemy models.

    This mixin provides a `ts` field that stores the record's timestamp
    with timezone support. The default value is set to the current time
    in the database server using ``func.now()``.

    Attributes
    ----------
    ts : sqlalchemy.orm.Mapped[datetime.datetime]
        Timestamp of the record with timezone information. Defaults to the
        current server time and cannot be null.
    """
    ts: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __iter__(self):
        """
        Iterate over the mixin's timestamp attribute.

        Yields
        ------
        tuple of (str, str or None)
            The string ``'ts'`` and its corresponding timestamp value
            formatted as an ISO 8601 string in UTC, or ``None`` if
            the timestamp is not set.
        """
        yield 'ts', self.ts.astimezone(pytz.UTC).strftime('%Y-%m-%dT%H:%M:%S%z') if self.ts is not None else None

