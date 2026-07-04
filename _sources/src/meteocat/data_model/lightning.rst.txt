MeteocatLightning
=================

SQLAlchemy ORM model for Lightning events.

This module defines the `MeteocatLightning` class representing lightning occurrences
recorded the Meteo.cat data providers. It inherits from `Lightning` and adds the properties of
a lightning that are recorded by Meteo.Cat.

Classes
-------

MeteocatLightning
^^^^^^^^^^^^^^^^^

.. autoclass:: src.meteocat.data_model.lightning.MeteocatLightning
   :members: __init__, __iter__, object_hook_gisfire_api
   :undoc-members:
   :show-inheritance:
   :exclude-members: meteocat_id, peak_current, multiplicity, chi_squared, ellipse_major_axis, ellipse_minor_axis,
                     ellipse_angle, number_of_sensors, hit_ground, municipality_code, x_4258, y_4258

MeteocatLightningParams
^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: src.meteocat.data_model.lightning.MeteocatLightningParams
   :members:
   :undoc-members:
   :show-inheritance:
   :exclude-members: meteocat_id, peak_current, multiplicity, chi_squared, ellipse_major_axis, ellipse_minor_axis,
                     ellipse_angle, number_of_sensors, hit_ground, municipality_code, x_4258, y_4258, x_25831, y_25831,
                     geometry_4258, geometry_25831
