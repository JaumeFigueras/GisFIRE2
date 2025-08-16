Data Model
==========

.. contents::
   :local:
   :depth: 1

Overview
--------

The GisFIRE project needs a way to describe the different entities that are needed to describe the lightnings,
metheorological data or thunerstorms and store them in a database. This is the data model.

The project defines a data model based on the general characteristics of the different entities and the specifities
of the different data providers, so the Object Oriented paradigm is used in the data model.

What is a Data Model?
---------------------

A data model describes:

- The entities in the system (for example: ``Lightning``, ``Weather Station``, ``Thunderstorm``)
- The relationships between these entities
- The properties and data types of each entity
- Any constraints or business rules

In this project, the data model is implemented in code using an ORM
(Object-Relational Mapping) library: `SQLAlchemy <https://www.sqlalchemy.org>`_.

Data Model
----------

Metaclass
^^^^^^^^^

The GisFIRE metaclass ia a special class that creates the necessary properties getters and setters in the classes
depending on the included mixins and the functionality assigned to them.

For example if a ``Location`` mixin is included, the mixin creates the attributes and the metaclass creates the
class properties and spatial conversion functions to convert a EPSG:4326 to a EPSG:25846

MixIns
^^^^^^

The Mixins provide generic functionality to all the classes that need them. The Mixins provide reusability in
the code.

- **Location**:
  Adds iteration over geospatial coordinates (X, Y) for one or more EPSG codes defined in
  the class-level ``__location__`` attribute. Useful for models that store positions in
  multiple coordinate systems.

- **Date/Time**:
  Manages date/time fields with timezone awareness. Supports object comparison based on
  date/time and timezone, and provides iteration with proper formatting of offsets.

- **Timestamp**:
  Automatically adds a ``ts`` field storing the record creation timestamp in UTC.
  Includes iteration support to output the timestamp in ISO 8601 format.

General Data Model
^^^^^^^^^^^^^^^^^^

The generic data model contain the following elements:

- **Data Provider**:
- **Wildfire Ignition**:
- **Lightning**:
- **Thunderstorm**:
- **Weather Station**:
- **Weather Station Status**:
- **Variable**:
- **Measure**:

Bombers de la Generalitat de Catalunya Data Model
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- **Wildfire Ignition**:

Servei Meteorològic de Catalunya
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- **Lightning**:
- **Thunderstorm**:
- **Weather Station**:
- **Weather Station Status**:
- **Variable**:
- **Measure**:

Data Model Pages
----------------

General Data Model Pages
^^^^^^^^^^^^^^^^^^^^^^^^

.. toctree::
   :maxdepth: 1

   src/data_model/metaclass
   src/data_model/mixins
   src/data_model/base
   src/data_model/data_provider
   src/data_model/lightning

Bombers de la Generalitat de Catalunya Data Model Pages
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. toctree::
   :maxdepth: 1

Servei Meteorològic de Catalunya
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. toctree::
   :maxdepth: 1
