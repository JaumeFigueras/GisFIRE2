Lightning
=========

SQLAlchemy ORM model for Lightning events.

This module defines the `Lightning` class representing lightning occurrences
recorded by various data providers. It uses several mixins to provide common
functionality such as timestamps, geospatial location, and datetime handling.

Classes
-------

Lightning
^^^^^^^^^

.. autoclass:: src.data_model.lightning.Lightning
   :members: __init__, __iter__
   :undoc-members:
   :show-inheritance:
   :exclude-members: __tablename__, x_4326, y_4326, date_time, data_provider, type

DataProviderParams
^^^^^^^^^^^^^^^^^^

.. autoclass:: src.data_model.lightning.LightningParams
   :members:
   :undoc-members:
   :show-inheritance:
   :exclude-members: x_4326, y_4326, date_time, data_provider
