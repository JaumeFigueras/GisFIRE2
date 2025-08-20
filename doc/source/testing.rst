Testing
=======

.. contents::
   :local:
   :depth: 2

Overview
--------

Testing is a critical part of software development. It ensures that your code behaves as expected, helps catch bugs early, and improves maintainability.

**Why testing is necessary:**

- Detect regressions and bugs before they reach production.
- Provide confidence when refactoring code.
- Serve as documentation for code behavior.

**Using pytest:**

`pytest <https://docs.pytest.org/en/stable/>`_ is a powerful testing framework for Python. Some key points:

- Simple syntax for writing tests.
- Supports fixtures for reusable test setup.
- Integrates with CI/CD pipelines for automated testing.

conftest.py
-----------

The ``conftest.py`` file is a special pytest configuration file. It provides reusable fixtures and setup code for your tests.

In this project, ``conftest.py`` specifically handles a temporary PostgreSQL test database with SQLAlchemy. Here's what it does:

Temporary PostgreSQL instance
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Uses ``pytest_postgresql`` to create an ephemeral database for testing.
- Ensures tests run in isolation and do not affect production data.

Database schema initialization
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Executes a series of SQL files to create all necessary tables and relationships in the test database.

Scoped SQLAlchemy session fixture
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Provides a ``db_session`` fixture, which:

- Connects to the temporary database.
- Yields a SQLAlchemy ``scoped_session`` for tests to use.
- Cleans up by deleting all table contents at the end of each test function.


Pages
-----

.. toctree::
   :maxdepth: 1

   test/conftest
   test/fixtures
   test/database
   test/data_model
   test/apps

