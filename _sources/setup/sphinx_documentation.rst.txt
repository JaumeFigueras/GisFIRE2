Setting up the Sphinx Documentation Environment
===============================================

Sphinx is a powerful documentation generation system widely used in Python projects.
It can produce HTML, PDF, ePub, and other formats from reStructuredText (``.rst``) source files.

This guide explains how to set up and build Sphinx documentation for your project.

Prerequisites
-------------

- **Python** (version 3.7 or higher recommended)
- **pip** (Python package manager)

Install Sphinx
--------------

First, install Sphinx in your Python environment (or the requirements file):

.. code-block:: bash

    pip3 install sphinx

Install any additional themes, for example:

.. code-block:: bash

    pip install sphinx-rtd-theme

Create the Sphinx Documentation Skeleton
-----------------------------------------

From your project’s root directory, run:

.. code-block:: bash

    sphinx-quickstart doc

This command will:

- Create a ``doc/`` directory with the basic configuration
- Generate ``conf.py`` for Sphinx settings
- Create the initial ``index.rst`` file

When prompted, you can accept defaults or customize settings (project name, author, version, etc.). It is
**recommended** to use different folders for sources and build files

Building the HTML Documentation
--------------------------------

After editing your documentation sources (in ``doc/source/``), you can build the HTML output:

.. code-block:: bash

    sphinx-build -M html doc/source/ doc/build/

The generated HTML files will be available in:

``doc/build/html/index.html``

You can open this file in your web browser to view the documentation.

Updating Documentation
----------------------

1. Add or modify ``.rst`` files in ``doc/source/``.
2. Update the ``index.rst`` table of contents if needed.
3. Re-run the ``sphinx-build`` command to rebuild the documentation.

References
----------

- `Sphinx Documentation <https://www.sphinx-doc.org/>`_
- `reStructuredText Primer <https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html>`_
