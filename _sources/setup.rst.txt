Setup
=====

.. contents::
   :local:
   :depth: 1

Overview
--------

The **GisFIRE2** project integrates several tools and components that must be configured before use.
This setup guide provides an overview of each requirement and links to detailed instructions.

Requirements
------------

1. **Python Virtual Environment**
   GisFIRE2 provides plugins for QGIS, so a dedicated Python virtual environment is required to ensure
   compatibility with QGIS imports. *(Currently, QGIS LTS version 3 with Qt5 is used.)*
   See :doc:`setup/python_virtual_environment` for setup steps.

2. **PostgreSQL Database**
   An independent PostgreSQL cluster is recommended for improved isolation and stability.
   See :doc:`setup/postgresql_database` for setup steps.

3. **Sphinx Documentation System**
   Sphinx is required to build the project documentation.
   See :doc:`setup/sphinx_documentation` for setup steps.

4. **Deploying Sphinx Documentation to GitHub**
   Enables automated generation and publishing of the documentation to GitHub Pages.
   See :doc:`setup/deploy_sphinx_to_github` for setup steps.

Setup Pages
-----------

.. toctree::
   :maxdepth: 1

   setup/python_virtual_environment
   setup/postgresql_database
   setup/sphinx_documentation
   setup/deploy_sphinx_to_github
