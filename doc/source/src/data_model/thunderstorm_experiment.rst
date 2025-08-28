Thunderstorm Experiment
=======================

This module defines the SQLAlchemy ORM model for a thunderstorm experiment.
in GisFire a thunderstorm experiment is the algorithm and parametrs used to determine
the `Lightning` set that belong to a `Thunderstorm`.

Classes
-------

ThunderstormExperiment
^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: src.data_model.thunderstorm_experiment.ThunderstormExperiment
   :members: __init__
   :undoc-members:
   :show-inheritance:
   :exclude-members: algorithm, parameters

ThunderstormExperimentParams
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: src.data_model.thunderstorm_experiment.ThunderstormExperimentParams
   :members:
   :undoc-members:
   :show-inheritance:
   :exclude-members: algorithm, parameters

ThunderstormExperimentAlgorithm
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: src.data_model.thunderstorm_experiment.ThunderstormExperimentAlgorithm
   :members:
   :undoc-members:
   :show-inheritance:
   :exclude-members: TIME, DISTANCE, TIME_DISTANCE, DBSCAN_TIME, DBSCAN_TIME_DISTANCE
