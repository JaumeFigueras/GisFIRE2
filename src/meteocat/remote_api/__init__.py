#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import requests

from requests.exceptions import RequestException
from requests.exceptions import HTTPError

from typing import Optional
from typing import Dict
from logging import Logger

TIMEOUT_DEFAULT = 5
RETRIES_DEFAULT = 3
BACKOFF_FACTOR_DEFAULT = 1.5  # exponential backoff factor

def get_from_api(api_url: str,
                 params: Optional[Dict] = None,
                 headers: Optional[Dict] = None,
                 timeout: int = TIMEOUT_DEFAULT,
                 retries: int = RETRIES_DEFAULT,
                 backoff_factor: float = BACKOFF_FACTOR_DEFAULT,
                 log: Optional[Logger] = None) -> requests.Response:
    """
    Perform a GET request to the specified API URL with retry and timeout logic.

    This function attempts to fetch data from the given API URL using HTTP GET.
    It supports automatic retries on communication errors or HTTP exceptions,
    with exponential backoff delays between retries to avoid rapid repeated requests.

    Parameters
    ----------
    api_url : str
        The full URL of the API endpoint to request.
    params : dict, optional
        Dictionary of URL parameters to append to the request, by default None.
    headers : dict, optional
        Dictionary of headers to append to the request, by default None.
    timeout : int, optional
        Timeout in seconds for the HTTP request, by default 5 seconds.
    retries : int, optional
        Number of times to retry the request in case of failure, by default 3.
    backoff_factor : float, optional
        Factor for exponential backoff delay between retries, by default 1.5.
    log : logging.Logger or None, optional
        Optional logger instance to log retry warnings, by default None.
    Returns
    -------
    requests.Response
        The successful HTTP response object returned by the API.

    Raises
    ------
    requests.exceptions.RequestException
        If all retry attempts fail, raises the last encountered exception.

    """
    attempt = 0
    last_exception = None

    while attempt < retries:
        try:
            response = requests.get(api_url, timeout=timeout, params=params)
            return response
        except (RequestException, HTTPError) as e:
            if log is not None:
                log.warning(f"API Request failed to fetch data from {api_url}: {e}")
            last_exception = e
            attempt += 1
            if attempt == retries:
                if log is not None:
                    log.error(f"API Request failed to fetch data from {api_url} after {retries} attempts: {e}")
                break
            # Exponential backoff before retrying
            backoff_time = backoff_factor ** attempt
            time.sleep(backoff_time)

    # If we reach here, all attempts failed
    raise last_exception
