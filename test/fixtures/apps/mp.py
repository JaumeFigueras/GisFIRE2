#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fixtures for multiprocessing-based tests.

This module defines pytest fixtures that provide shared
multiprocessing resources to test functions.
"""

import pytest
import multiprocessing as mp
import logging

@pytest.fixture(scope='function')
def mp_data(logger: logging.Logger):
    """
    Provide shared multiprocessing resources for tests.

    This fixture sets up a multiprocessing manager with:
    - A lock for process synchronization.
    - A managed list for storing results across processes.
    - A managed list holding the current process ID (initialized to 0).
    - A test logger.

    After the test completes, the multiprocessing manager
    is properly shut down.

    Parameters
    ----------
    logger : logging.Logger
        Fixture providing a logger instance for use during tests.

    Yields
    ------
    dict
        A dictionary containing:

        - **lock** (`multiprocessing.synchronize.Lock`) :
          A multiprocessing lock for synchronization.
        - **shared_result_list** (`multiprocessing.managers.ListProxy`) :
          Shared list to collect results across processes.
        - **process_id** (`multiprocessing.managers.ListProxy`) :
          Shared list containing a single integer process ID.
        - **logger** (`logging.Logger`) :
          Logger instance for test logging.
    """
    mg = mp.Manager()
    lock = mg.Lock()
    shared_result_list = mg.list()
    process_id = mg.list()
    process_id.append(0)

    yield {
        'lock': lock,
        'shared_result_list': shared_result_list,
        'process_id': process_id,
        'logger': logger,
    }

    mg.shutdown()