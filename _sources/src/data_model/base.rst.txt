Base
====

Overview
--------

Custom SQLAlchemy types and base class for models.

This module defines a custom SQLAlchemy declarative base with a metaclass
and utilities for working with PostgreSQL HSTORE fields in a hashable
and mutable way.

Base
^^^^

.. autodata:: src.data_model.Base
   :annotation:

Classes
-------

HashableMutableDict
^^^^^^^^^^^^^^^^^^^

.. autoclass:: src.data_model.HashableMutableDict
   :members:
   :undoc-members:
   :show-inheritance:

HashableHSTORE
^^^^^^^^^^^^^^

.. autoclass:: src.data_model.HashableHSTORE
   :members:
   :undoc-members:
   :show-inheritance:
   :exclude-members: impl, cache_ok