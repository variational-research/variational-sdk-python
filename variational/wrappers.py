import requests

from dataclasses import dataclass
from typing import Generic, List, TypeVar, Optional, Dict, Mapping

T = TypeVar("T")

RATE_LIMIT_RESET_MS_HEADER = "x-request-received-ms"


@dataclass
class ResponseMetadata:
    # timestamp in seconds when API server received the request
    request_received_at: float


@dataclass
class ApiError(Exception):
    status_code: int
    api_code: int
    message: str


@dataclass
class ApiSingle(Generic[T]):
    result: T
    meta: ResponseMetadata

    @staticmethod
    def from_response(response: requests.Response):
        return ApiSingle(
            result=response.json()['result'],
            meta=ResponseMetadata(
                _get_request_received_timestamp(response.headers)),
        )


@dataclass
class ApiList(Generic[T]):
    result: List[T]
    meta: ResponseMetadata

    @staticmethod
    def from_response(response: requests.Response):
        return ApiList(
            result=response.json()['result'],
            meta=ResponseMetadata(
                _get_request_received_timestamp(response.headers)),
        )


@dataclass
class Pagination:
    next_page: Optional[Dict]


@dataclass
class ApiPage(Generic[T]):
    result: List[T]
    pagination: Pagination
    meta: ResponseMetadata

    @staticmethod
    def from_response(response: requests.Response):
        data = response.json()
        return ApiPage(
            result=data['result'],
            pagination=Pagination(next_page=data['pagination']['next_page']),
            meta=ResponseMetadata(
                _get_request_received_timestamp(response.headers)),
        )


def _get_request_received_timestamp(headers: Mapping) -> Optional[float]:
    for k, v in headers.items():
        if k.lower() == RATE_LIMIT_RESET_MS_HEADER:
            return int(v) / 1000
    raise ValueError(
        f"response didn't contain {RATE_LIMIT_RESET_MS_HEADER} header")
