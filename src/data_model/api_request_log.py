#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.ext.mutable import MutableDict

from src.data_model import Base
from src.data_model import HashableMutableDict
from src.data_model import HashableHSTORE
from src.data_model.mixins.time_stamp import TimeStampMixIn
from src.data_model.data_provider import DataProvider

from typing import Optional
from typing import Union
from typing import TypedDict
from typing_extensions import NotRequired
from typing_extensions import Unpack

class APIRequestLogParams(TypedDict):
    api_request_endpoint: str
    api_request_params: NotRequired[MutableDict[str, str]]
    api_request_http_status: int
    api_request_error_message: NotRequired[str]
    data_provider: Union[DataProvider, str]


class APIRequestLog(Base, TimeStampMixIn):
    """
    Database model to log API requests to Meteo.cat (or other external APIs).

    Each row uniquely identifies an API request attempt based on:
    - `endpoint` (string identifying the API resource)
    - `params` (HSTORE of query parameters)

    The uniqueness constraint ensures idempotency: the same request won't be
    logged multiple times, but instead updated on retry.
    """

    __tablename__ = "api_request_log"

    api_request_id: Mapped[int] = mapped_column('api_request_id', Integer, primary_key=True, autoincrement=True)
    api_request_endpoint: Mapped[str] = mapped_column('api_request_endpoint', String, nullable=False)
    api_request_params: Mapped[Optional[MutableDict]] = mapped_column('api_request_params', HashableMutableDict.as_mutable(HashableHSTORE), nullable=True)
    api_request_http_status: Mapped[int] = mapped_column('api_request_http_status', Integer, nullable=False)
    api_request_error_message: Mapped[Optional[str]] = mapped_column('api_request_error_message', String, nullable=True)
    # SQLAlchemy relations
    data_provider_name: Mapped[str] = mapped_column('data_provider_name', ForeignKey('data_provider.data_provider_name'), nullable=False)
    data_provider: Mapped["DataProvider"] = relationship(back_populates="requests")

    def __init__(self, **kwargs: Unpack[APIRequestLogParams]) -> None:
        super().__init__()
        for key, value in kwargs.items():
            if hasattr(self, key):
                if key == "data_provider" and isinstance(value, str):
                    self.data_provider_name = value
                else:
                    setattr(self, key, value)