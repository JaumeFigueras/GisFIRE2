#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

from setuptools.package_index import URL_SCHEME

from src.meteocat.remote_api import get_from_api
from src.meteocat.data_model.variable import MeteocatVariable
from src.json_decoders.no_none_in_list import NoNoneInList
from src.exceptions.status_code_error import StatusCodeError

from typing import List

URL_XEMA_VARIABLES_MESURADES = "https://api.meteo.cat/xema/v1/variables/mesurades/metadades"
URL_XEMA_VARIABLES_AUXILIARS = "https://api.meteo.cat/xema/v1/variables/auxiliars/metadades"
URL_XEMA_VARIABLES_MULTIVARIABLE = "https://api.meteo.cat/xema/v1/variables/cmv/metadades"

def get_variables_list(api_key: str) -> List[MeteocatVariable]:
    try:
        headers = {
            'X-Api-Key': api_key,
        }
        values: List[MeteocatVariable] = list()
        for url in [URL_XEMA_VARIABLES_MESURADES, URL_XEMA_VARIABLES_AUXILIARS, URL_XEMA_VARIABLES_MULTIVARIABLE]:
            response = get_from_api(api_url=url, headers=headers)
            if response.ok:
                values += json.loads(response.text, cls=NoNoneInList, object_hook=MeteocatVariable.object_hook_variable_meteocat_api)
            else:
                raise StatusCodeError(response.status_code, response.text)
        return values
    except Exception as xcpt:
        raise xcpt
