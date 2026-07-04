Data Provider
=============

This module defines the SQLAlchemy ORM model for a data provider in the
GisFIRE system. A data provider represents an entity that supplies
geospatial or lightning data to the platform. It includes metadata such
as name, description, and an optional URL, as well as relationships to
other models like `Lightning`.

Notes
-----
The module uses `__future__.annotations` to allow type annotations
referring to the enclosing class (PEP 563).

Classes
-------

DataProvider
^^^^^^^^^^^^

.. autoclass:: src.data_model.data_provider.DataProvider
   :members: __init__
   :undoc-members:
   :show-inheritance:
   :exclude-members: __tablename__, name, description, url

DataProviderParams
^^^^^^^^^^^^^^^^^^

.. autoclass:: src.data_model.data_provider.DataProviderParams
   :members:
   :undoc-members:
   :show-inheritance:
   :exclude-members: name, description, url