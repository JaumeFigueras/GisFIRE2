Testing Fixtures
================

.. contents::
   :local:
   :depth: 2

Overview
--------

In pytest, a **fixture** is a reusable piece of code that provides a fixed baseline for your tests. Fixtures are used to set up and tear down resources that tests depend on, such as databases, files, or network connections.

Fixtures help you:

- Avoid code duplication in test setup and teardown.
- Ensure tests run in a consistent and isolated environment.
- Make tests easier to maintain and more readable.
- Manage external dependencies in a controlled manner.

Why Fixtures are Necessary
--------------------------

Using fixtures is necessary because:

1. **Reusability**
   If multiple tests need the same setup (e.g., creating a temporary database or populating test data), fixtures allow you to define this setup once and reuse it across tests.

2. **Isolation**
   Fixtures can create isolated environments for each test, ensuring that tests do not interfere with one another.

3. **Automatic Cleanup**
   Fixtures can include teardown code, which automatically cleans up resources after a test finishes. This prevents side effects like leftover files or persistent database records.

4. **Modularity and Readability**
   Fixtures separate setup code from test logic, making tests easier to read and maintain.

Example
-------

Here is a simple fixture example using pytest:

.. code-block:: python

    import pytest

    @pytest.fixture
    def sample_list():
        """Provides a sample list for tests."""
        return [1, 2, 3]

    def test_sum(sample_list):
        assert sum(sample_list) == 6

Explanation:

- The ``sample_list`` fixture provides the test data.
- The test function ``test_sum`` automatically receives the fixture as an argument.
- The fixture ensures consistent test input and isolates setup from test logic.

Advanced Usage
--------------

Fixtures can also:

- Use different scopes (function, class, module, session) to control how often they are set up and torn down.
- Depend on other fixtures.
- Use factories to provide dynamic or parameterized test data.

References
----------

- `pytest Fixtures <https://docs.pytest.org/en/stable/fixture.html>`_

Pages
-----

.. toctree::
   :maxdepth: 1

   fixtures/data_model
   fixtures/meteocat
   fixtures/apps
