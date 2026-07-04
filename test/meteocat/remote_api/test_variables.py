#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
import requests_mock

from requests.exceptions import HTTPError
from requests.exceptions import ConnectTimeout
from requests.exceptions import RequestException

from src.meteocat.remote_api.variables import URL_XEMA_VARIABLES_MESURADES
from src.meteocat.remote_api.variables import URL_XEMA_VARIABLES_AUXILIARS
from src.meteocat.remote_api.variables import URL_XEMA_VARIABLES_MULTIVARIABLE
from src.meteocat.remote_api.variables import get_variables_list
from src.exceptions.status_code_error import StatusCodeError
from src.meteocat.data_model.variable import MeteocatVariable

from typing import List

def test_get_variable_list_01() -> None:
    """
    Tests the get_exchanges_from_symbol_list method that retrieves the exchange list assuming an HTTP Error
    """
    with requests_mock.Mocker() as rm:
        for url in [URL_XEMA_VARIABLES_MESURADES, URL_XEMA_VARIABLES_AUXILIARS, URL_XEMA_VARIABLES_MULTIVARIABLE]:
            rm.get(url, exc=HTTPError)
        with pytest.raises(RequestException):
            _ = get_variables_list('1234')


def test_get_variable_list_02() -> None:
    """
    Tests the get_exchanges_from_symbol_list method that retrieves the exchange list assuming an HTTP Connection
    Timeout Error
    """
    with requests_mock.Mocker() as rm:
        for url in [URL_XEMA_VARIABLES_MESURADES, URL_XEMA_VARIABLES_AUXILIARS, URL_XEMA_VARIABLES_MULTIVARIABLE]:
            rm.get(url, exc=ConnectTimeout)
        with pytest.raises(RequestException):
            _ = get_variables_list('1234')


def test_get_variable_list_03() -> None:
    """
    Tests the get_exchanges_from_symbol_list method that retrieves the exchange list
    """
    with requests_mock.Mocker() as rm:
        for url in [URL_XEMA_VARIABLES_MESURADES, URL_XEMA_VARIABLES_AUXILIARS, URL_XEMA_VARIABLES_MULTIVARIABLE]:
            rm.get(url, text='', status_code=404)
        with pytest.raises(StatusCodeError):
            _ = get_variables_list('1234')


def test_get_variable_list_04(mesurades: str, auxiliars: str, multivariable: str) -> None:
    """
    Tests the get_exchanges_from_symbol_list method that retrieves the exchange list assuming an HTTP Connection
    Timeout Error
    """
    with requests_mock.Mocker() as rm:
        for url, response in [(URL_XEMA_VARIABLES_MESURADES, mesurades),
                              (URL_XEMA_VARIABLES_AUXILIARS, auxiliars),
                              (URL_XEMA_VARIABLES_MULTIVARIABLE, multivariable)]:
            rm.get(url, text=response, status_code=200)
        elements: List[MeteocatVariable] = get_variables_list('1234')
        assert len(elements) == 90
        for element in elements:
            assert isinstance(element, MeteocatVariable)
