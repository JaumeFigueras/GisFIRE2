GisFIRE2 documentation
======================

This repository contains all the code developed for my PhD research on lightning-caused wildfires in Catalonia — from
data preparation to predictive modelling and operational logistics.

It includes:

- **Data processing** pipelines for integrating wildfire perimeters, lightning strike datasets, meteorological observations, and geographic information.
- **Algorithms** for linking lightning events to wildfire ignitions using spatial–temporal analysis and validation methods.
- **Machine learning** models for:
    - Predicting which lightning strikes are likely to cause an ignition (pre-ignition classification).
    - Thusnderstorm characterization
- **Techniques for imbalanced datasets**, including re-sampling, cost-sensitive learning, and rare-event evaluation metrics.
- **Optimization algorithms** for aerial firefighting: minimal-disc coverage of lightning events, route planning, and resource allocation.

The project also uses `QGIS <https://www.qgis.org>`_, so different **plugins** have also been developed.

The aim is to bridge environmental data science with operational wildfire management, enabling better risk prediction
and efficient firefighting deployment.

The documents ar organized as follow:

- **GisFIRE Setup**:
- **GisFIRE Data Model**:
- **GisFIRE Project Modules**:
    - **Geo**:
- **GisFIRE API**:
- **Applications**:
- **QGIS Plugins**:

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   setup
   data_model
   modules

