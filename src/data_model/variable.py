#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from src.data_model import Base
from src.data_model.mixins.time_stamp import TimeStampMixIn
from src.data_model.data_provider import DataProvider

from typing import Tuple
from typing import Iterator
from typing import Any
from typing import Union
from typing import TypedDict
from typing import Unpack

class VariableParams(TypedDict):
    """Typed dictionary specifying the parameters required to initialize a Variable.

    Attributes
    ----------
    variable_name : str
        Name of the variable.
    data_provider : DataProvider or str
        Either a `DataProvider` instance or the name of the data provider
        (as a string) to associate with the variable.
    """
    variable_name: str
    data_provider: Union[DataProvider, str]

class Variable(Base, TimeStampMixIn):
    """SQLAlchemy model representing a variable linked to a data provider.

    This class serves as a base entity for variables within the data model.
    It supports polymorphic inheritance and maintains a relationship to a
    data provider.

    Attributes
    ----------
    variable_id : int
        Primary key of the variable.
    variable_name : str
        Name of the variable.
    data_provider_name : str
        Foreign key reference to the name of the associated data provider.
    data_provider : DataProvider
        Relationship to the associated `DataProvider` object.
    type : str
        Column used by SQLAlchemy to manage polymorphic inheritance.
    """
    # SQLAlchemy columns
    __tablename__ = "variable"
    variable_id: Mapped[int] = mapped_column('variable_id', Integer, primary_key=True, autoincrement=True)
    variable_name: Mapped[str] = mapped_column('variable_name', String, nullable=False)
    # SQLAlchemy relations
    data_provider_name: Mapped[str] = mapped_column('data_provider_name', ForeignKey('data_provider.data_provider_name'), nullable=False)
    data_provider: Mapped["DataProvider"] = relationship(back_populates="variables")
    # SQLAlchemy Inheritance options
    type: Mapped[str]
    __mapper_args__ = {
        "polymorphic_identity": "variable",
        "polymorphic_on": "type",
    }

    def __init__(self, **kwargs: Unpack[VariableParams]) -> None:
        """Initialize a new Variable instance.

        Parameters
        ----------
        **kwargs : Unpack[VariableParams]
            Keyword arguments corresponding to `VariableParams`. Keys are
            assigned as attributes if they exist. If `data_provider` is given
            as a string, it is stored in `data_provider_name`; otherwise,
            a `DataProvider` object is assigned to the `data_provider`
            relationship.
        """
        super().__init__()
        for key, value in kwargs.items():
            if hasattr(self, key):
                if key == "data_provider" and isinstance(value, str):
                    self.data_provider_name = value
                else:
                    setattr(self, key, value)

    def __iter__(self) -> Iterator[Tuple[str, Any]]:
        """Iterate over the variable attributes as key-value pairs.

        Yields
        ------
        tuple of (str, Any)
            Pairs representing the attribute name and its value. Includes:

            - ``("variable_id", int)``
            - ``("variable_name", str)``
            - ``("data_provider_name", str)``
        """
        yield 'variable_id', self.variable_id
        yield 'variable_name', self.variable_name
        yield 'data_provider_name', self.data_provider_name
