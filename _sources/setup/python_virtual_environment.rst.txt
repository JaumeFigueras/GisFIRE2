Python Virtual Environment
==========================

GisFIRE2 provides plugins for QGIS, so a dedicated Python virtual environment is required to ensure compatibility with QGIS imports.
On Linux, this can be done by creating a temporary virtual environment to install the necessary tools, and then using the QGIS virtual environment creation utility.

Steps
-----

1. **Create a temporary virtual environment**

    This environment will be used only to install the QGIS virtual environment creation tool.

    .. code-block:: bash

      python3 -m venv tmp_venv

2. **Activate the temporary virtual environment**

    .. code-block:: bash

      source tmp_venv/bin/activate

3. **Install the QGIS virtual environment creation tool**

    .. code-block:: bash

      pip3 install qgis-venv-creator

4. **Generate the QGIS-compatible virtual environment**

    Change to your GisFIRE2 project directory, then run:

    .. code-block:: bash

      create-qgis-venv --venv-name .venv

5. **Clean up and configure your IDE**

    Once the process is complete:

    - You may delete the temporary virtual environment (`tmp_venv`).
    - Configure your preferred IDE to use the new `.venv` interpreter.

     For **PyCharm**, go to:

     `File → Settings → Python → Interpreter` and select the `.venv` path.

6. **Install regular dependencies**

    When all is setup the dependencies can be installed with:

    .. code-block:: bash

      pip3 install -r requirements.txt

References
----------

- `Creating a Python Virtual Environment for PyQGIS Development with VS Code on Windows <https://blog.geotribu.net/2024/11/25/creating-a-python-virtual-environment-for-pyqgis-development-with-vs-code-on-windows/>`_
- `qgis-venv-creator GitHub Repository <https://github.com/GispoCoding/qgis-venv-creator>`_
