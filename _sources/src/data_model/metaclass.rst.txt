ModelMeta Metaclass
===================

The ``ModelMeta`` metaclass extends SQLAlchemy's ``DeclarativeMeta`` to
dynamically generate:

- **Location properties**: ``x_*``, ``y_*``, and ``geometry_*`` columns,
  including coordinate validation, geometry generation, and optional
  coordinate conversion.
- **DateTime properties**: Attributes with timezone enforcement and
  automatic timezone column storage.
- **Default properties**: Simple getters and setters for auxiliary fields.

Overview
--------

``ModelMeta`` is used as the metaclass for ORM models that require
automatic generation of location and/or datetime fields based on
configuration dictionaries defined in the model's class body.

The main goals of this metaclass are:

1. Avoid repetitive boilerplate for defining coordinate and datetime fields.
2. Automatically link coordinates with geometry generation.
3. Enforce geographic validation (longitude/latitude ranges) when required.
4. Handle timezone-aware datetime values safely.

How It Works
------------

When a class is created with ``ModelMeta`` as its metaclass:

1. **Location properties** are generated if the special ``__location__``
   attribute exists in the class dictionary.

    Each location configuration is a dictionary with:

    - ``epsg``: EPSG code for the coordinate system (e.g., ``4326``).
    - ``validation``: ``"geographic"`` for lat/lon validation, or ``False``.
    - ``conversion``: Optional list of coordinate system conversion mappings.

    Example:

    .. code-block:: python

        __location__ = [
        {'epsg': 4258, 'validation': 'geographic', 'conversion': [
            {'src': 4258, 'dst': 4326},
            {'src': 4258, 'dst': 25831}
        ]},
        {'epsg': 25831, 'validation': False, 'conversion': False}
        ]

    This example will create two locations for the two ``epsg``, one is geographic and uses validation and when
    setted converts to the two ``dst`` attributes with its ``epsg``

2. **Datetime properties** are generated if the special ``__date__``
   attribute exists in the class dictionary.

   Each datetime configuration is a dictionary with:

   - ``name``: Name of the datetime attribute.
   - ``nullable``: Boolean indicating whether the field can be ``NULL``.

   Example:

   .. code-block:: python

      __date__ = [
          {"name": "created_at", "nullable": False}
      ]

3. Geometry columns are automatically linked to coordinate columns and
   generated using the ``GeometryGenerator`` helper.
4. Optional coordinate conversions are performed using the
   ``LocationConverter`` helper.

Property Factories
------------------

The metaclass defines several internal "factory" functions to produce
properties:

- ``property_factory_xy``:
  Creates ``x_*`` and ``y_*`` coordinate properties with optional validation
  and automatic geometry/conversion triggers.

- ``property_factory_geometry``:
  Creates read-only ``geometry_*`` properties that return either a WKT string
  or a Shapely ``Point`` object.

- ``property_factory_datetime``:
  Creates datetime properties with timezone enforcement and storage of
  timezone information in a separate column.

- ``property_factory_default``:
  Creates simple getter/setter properties for auxiliary fields.

Example Usage
-------------

.. code-block:: python

   from sqlalchemy.orm import declarative_base
   from src.models.modelmeta import ModelMeta

   Base = declarative_base(metaclass=ModelMeta)

   class Sensor(Base):
       __tablename__ = "sensors"

       __location__ = [
           {
               "epsg": 4326,
               "validation": "geographic",
               "conversion": [
                   {"src": 4326, "dst": 3857}
               ]
           }
       ]

       __date__ = [
           {"name": "installed_at", "nullable": False}
       ]

       # Additional columns and methods here

In this example:

- The metaclass automatically adds:
  - ``x_4326`` and ``y_4326`` properties with longitude/latitude validation.
  - ``geometry_4326`` property linked to the coordinates.
  - ``installed_at`` datetime property with timezone enforcement.
- Geometry is updated automatically when coordinates change.
- Conversions between coordinate systems are handled automatically.

Code
----

.. autoclass:: src.data_model.metaclass.model_metaclass.ModelMeta
   :members:
   :undoc-members:
   :show-inheritance:
   :private-members:
   :special-members:
