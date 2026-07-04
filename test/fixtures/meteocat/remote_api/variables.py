#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
import os
import json

from pathlib import Path

@pytest.fixture(scope='function')
def mesurades() -> str:
    """
    Reads the JSON file of measured variables from the meteocat API and returns it as string.

    https://api.meteo.cat/xema/v1/variables/mesurades/metadades
    """
    current_dir: Path = Path(__file__).parent
    json_file: str = os.path.join(str(current_dir), os.path.join("json", "mesurades.json"))
    with open(json_file, 'r') as file:
        data = file.read()
        return data

@pytest.fixture(scope='function')
def auxiliars() -> str:
    """
    Reads the JSON file of measured variables from the meteocat API and returns it as string.

    https://api.meteo.cat/xema/v1/variables/auxiliars/metadades
    """
    current_dir: Path = Path(__file__).parent
    json_file: str = os.path.join(str(current_dir), os.path.join("json", "auxiliars.json"))
    with open(json_file, 'r') as file:
        data = file.read()
        return data


@pytest.fixture(scope='function')
def multivariable() -> str:
    """
    Reads the JSON file of measured variables from the meteocat API and returns it as string.

    https://api.meteo.cat/xema/v1/variables/auxiliars/metadades
    """
    current_dir: Path = Path(__file__).parent
    json_file: str = os.path.join(str(current_dir), os.path.join("json", "multivariable.json"))
    with open(json_file, 'r') as file:
        data = file.read()
        return data
