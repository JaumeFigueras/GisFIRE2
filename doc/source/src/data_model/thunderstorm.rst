Thunderstorm
============

This module defines the SQLAlchemy ORM model for a thunderstorm.
in GisFire a thunderstorm experiment is the algorithm and parametrs used to determine
the `Lightning` set that belong to a `Thunderstorm`.

Classes
-------

Thunderstorm
^^^^^^^^^^^^

.. autoclass:: src.data_model.thunderstorm.Thunderstorm
   :members: __init__, number_of_lightnings, convex_hull_4326
   :undoc-members:
   :show-inheritance:
   :exclude-members:

ThunderstormParams
^^^^^^^^^^^^^^^^^^

.. autoclass:: src.data_model.thunderstorm.ThunderstormParams
   :members:
   :undoc-members:
   :show-inheritance:
   :exclude-members: thunderstorm_experiment_id,speed,cardinal_direction,travelled_distance,lightnings_per_minute,
                     date_time_end,date_time_start,y_4326,x_4326

ThunderstormLightningAssociation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: src.data_model.thunderstorm.ThunderstormLightningAssociation
   :members:
   :undoc-members:
   :show-inheritance:
   :exclude-members: thunderstorm,lightning,lightning_id,thunderstorm_id