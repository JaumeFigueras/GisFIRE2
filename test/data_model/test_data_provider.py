#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for the ``DataProvider`` class.

These tests validate the initialization behavior of the
:class:`~src.data_model.data_provider.DataProvider` class.

Tested scenarios
----------------
- Initialization with all parameters provided.
- Initialization with only required parameters.
- Initialization with unexpected extra fields.
- Initialization with no parameters.
- Equality with data providers
- Inequality with data providers with different types

The tests ensure that attributes are correctly set, optional fields
default to ``None``, and unexpected arguments are ignored.
"""

from src.data_model.data_provider import DataProvider


def test_data_provider_init_00():
    """
    Test initialization with all parameters.

    This test ensures that when `DataProvider` is initialized with
    `name`, `description`, and `url`, all attributes are correctly set.

    Expected behavior
    -----------------
    - `name` is stored as given.
    - `description` is stored as given.
    - `url` is stored as given.
    """
    dp = DataProvider(
        name="data provider name",
        description="data provider description",
        url="https://www.test.cat",
    )
    assert dp.name == "data provider name"
    assert dp.description == "data provider description"
    assert dp.url == "https://www.test.cat"


def test_data_provider_init_01():
    """
    Test initialization with only required parameters.

    This test ensures that when `DataProvider` is initialized without
    the optional `url`, it defaults to ``None``.

    Expected behavior
    -----------------
    - `name` is stored as given.
    - `description` is stored as given.
    - `url` is ``None``.
    """
    dp = DataProvider(
        name="data provider name",
        description="data provider description",
    )
    assert dp.name == "data provider name"
    assert dp.description == "data provider description"
    assert dp.url is None


def test_data_provider_init_02():
    """
    Test initialization with an unexpected extra field.

    This test ensures that if an unexpected keyword argument is passed,
    it is ignored and does not become an attribute of the instance.

    Expected behavior
    -----------------
    - `name` is stored as given.
    - `description` is stored as given.
    - Extra fields are ignored.
    """
    dp = DataProvider(
        name="data provider name",
        description="data provider description",
        estra_field="extra", # type: ignore
    )
    assert dp.name == "data provider name"
    assert dp.description == "data provider description"
    assert not hasattr(dp, "extra_field")


def test_data_provider_init_03():
    """
    Test initialization with no parameters.

    This test ensures that when `DataProvider` is initialized without
    arguments, all attributes default to ``None``.

    Expected behavior
    -----------------
    - `name` is ``None``.
    - `description` is ``None``.
    - `url` is ``None``.
    """
    dp = DataProvider() # type: ignore
    assert getattr(dp, "name", None) is None
    assert getattr(dp, "description", None) is None
    assert getattr(dp, "url", None) is None

def test_data_provider_eq_00():
    """
    Test equality with same name.

    This test ensures that two `DataProvider` instances with the same
    `name` are considered equal, even if other attributes differ.

    Expected behavior
    -----------------
    - Equality is determined solely by the `name` attribute.
    - Instances with the same `name` are equal regardless of
      `description` or `url`.
    """
    dp1 = DataProvider(name="provider", description="desc1", url="https://a.com")
    dp2 = DataProvider(name="provider", description="desc2", url="https://b.com")

    assert dp1 == dp2


def test_data_provider_eq_01():
    """
    Test inequality with different names.

    This test ensures that two `DataProvider` instances with different
    `name` values are not considered equal, even if their other
    attributes match.

    Expected behavior
    -----------------
    - Instances with different `name` values are not equal.
    - `description` and `url` do not affect equality.
    """
    dp1 = DataProvider(name="provider1", description="desc", url="https://a.com")
    dp2 = DataProvider(name="provider2", description="desc", url="https://a.com")
    dp3 = DataProvider(name="provider1", description="desc", url="https://a.com")

    assert dp1 != dp2
    assert dp1 == dp3


def test_data_provider_eq_02():
    """
    Test comparison with non-`DataProvider`.

    This test ensures that comparing a `DataProvider` instance against
    an object of a different type always returns ``False``.

    Expected behavior
    -----------------
    - `DataProvider` compared with a string, integer, or ``None`` is
      not equal.
    - No exceptions are raised during comparison.
    """
    dp = DataProvider(name="provider", description="desc", url="https://a.com")

    assert dp != "provider"
    assert dp != 123
    assert dp is not None
