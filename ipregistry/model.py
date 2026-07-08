"""
    Copyright 2019 Ipregistry (https://ipregistry.co).

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

       https://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""

from enum import Enum

from .json import *
from typing import Generic, TypeVar, Optional, Dict, Any

T = TypeVar('T')


class ErrorCode(str, Enum):
    BAD_REQUEST = 'BAD_REQUEST'
    DISABLED_API_KEY = 'DISABLED_API_KEY'
    FORBIDDEN_IP = 'FORBIDDEN_IP'
    FORBIDDEN_IP_ORIGIN = 'FORBIDDEN_IP_ORIGIN'
    FORBIDDEN_ORIGIN = 'FORBIDDEN_ORIGIN'
    INSUFFICIENT_CREDITS = 'INSUFFICIENT_CREDITS'
    INTERNAL = 'INTERNAL'
    INVALID_API_KEY = 'INVALID_API_KEY'
    INVALID_ASN = 'INVALID_ASN'
    INVALID_FILTER_SYNTAX = 'INVALID_FILTER_SYNTAX'
    INVALID_IP_ADDRESS = 'INVALID_IP_ADDRESS'
    MISSING_API_KEY = 'MISSING_API_KEY'
    RESERVED_ASN = 'RESERVED_ASN'
    RESERVED_IP_ADDRESS = 'RESERVED_IP_ADDRESS'
    TOO_MANY_ASNS = 'TOO_MANY_ASNS'
    TOO_MANY_IPS = 'TOO_MANY_IPS'
    TOO_MANY_REQUESTS = 'TOO_MANY_REQUESTS'
    TOO_MANY_USER_AGENTS = 'TOO_MANY_USER_AGENTS'
    UNKNOWN_ASN = 'UNKNOWN_ASN'

    @classmethod
    def from_code(cls, code):
        """Return the typed error code matching the given raw code, or None if unrecognized."""
        try:
            return cls(code)
        except ValueError:
            return None


class ApiResponseCredits:
    def __init__(self, consumed: Optional[int] = 0, remaining: Optional[int] = None):
        self.consumed = consumed
        self.remaining = remaining

    def __str__(self):
        fields = ', '.join(f"{key}={value}" for key, value in self.__dict__.items())
        return f"{self.__class__.__name__}({fields})"


class ApiResponseThrottling:
    def __init__(self, limit: int = None, remaining: int = None, reset: int = None):
        self.limit = limit
        self.remaining = remaining
        self.reset = reset

    def __str__(self):
        fields = ', '.join(f"{key}={value}" for key, value in self.__dict__.items())
        return f"{self.__class__.__name__}({fields})"


class ApiResponse(Generic[T]):
    def __init__(self, credits: ApiResponseCredits, data: T, throttling: Optional[ApiResponseThrottling] = None):
        self.credits = credits
        self.data = data
        self.throttling = throttling

    def __str__(self):
        fields = ', '.join(f"{key}={value}" for key, value in self.__dict__.items())
        return f"{self.__class__.__name__}({fields})"


class IpregistryError(Exception):
    pass


class ApiError(IpregistryError):
    def __init__(self, code: str, message: str, resolution: str):
        super().__init__(message)
        self.code = code
        self.error_code = ErrorCode.from_code(code)
        self.message = message
        self.resolution = resolution


class ClientError(IpregistryError):
   pass


class LookupError(ApiError):
    def __init__(self, json: Dict[str, Any]):
        super().__init__(
            code=json.get('code'),
            message=json.get('message'),
            resolution=json.get('resolution')
        )
