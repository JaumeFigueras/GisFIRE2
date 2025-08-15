Mixins
======

This section documents the reusable SQLAlchemy mixins available in the project.
These mixins add specific behaviors or attributes to models, such as timestamping,
date/time handling, and location coordinate management.

.. note::
   These mixins use the SQLAlchemy ``@declarative_mixin`` decorator, meaning they
   are intended to be inherited by declarative ORM classes.

DateTimeMixIn
-------------

The :class:`DateTimeMixIn` mixin provides an iterable interface for accessing date/time
attributes with timezone awareness, and supports equality comparison between objects.

**Features:**

- Handles date/time attributes defined in the class-level ``__date__`` list.
- Preserves timezone offsets when iterating over attributes.
- Compares objects based on both timestamp and timezone.

.. autoclass:: src.data_model.mixins.date_time.DateTimeMixIn
   :members: __eq__, __iter__
   :undoc-members:
   :show-inheritance:

LocationMixIn
-------------

The :class:`LocationMixIn` mixin provides an iterable interface for accessing location
coordinates in various EPSG spatial reference systems.

**Features:**

- Uses the ``__location__`` class attribute to determine available coordinate sets.
- Iterates through X and Y coordinates for each EPSG code.

.. autoclass:: src.data_model.mixins.location.LocationMixIn
   :members: __iter__
   :undoc-members:
   :show-inheritance:

TimeStampMixIn
--------------

The :class:`TimeStampMixIn` mixin adds a ``ts`` timestamp column to models,
automatically populated with the current server time.

**Features:**

- Stores the timestamp with timezone support.
- Iterates to produce an ISO 8601 UTC string representation of the timestamp.

.. autoclass:: src.data_model.mixins.time_stamp.TimeStampMixIn
   :members: __iter__
   :undoc-members:
   :show-inheritance:
   :exclude-members: ts
