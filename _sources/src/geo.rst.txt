Geo Module
==========

The ``geo`` module contains the functionality to manage geo data and concersion in the data model Metaclass

- ``geometry_generator.py``: When the individual geometry attributes are ser it generates the WKT string of the
  attributes
- ``location_converter.py``: Converts using ``proj4`` to different geometries
- **Data Model**: Provides different classes to access to PostGIS database geometries

Geo Module Pages
----------------

.. toctree::
   :maxdepth: 1

   geo/geometry_generator
   geo/location_converter

