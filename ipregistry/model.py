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

from .json import *
from typing import Generic, TypeVar, Optional, Dict, Any

T = TypeVar('T')


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


class RequesterIpInfo(IpInfo):
    user_agent: UserAgent


class IpregistryError(Exception):
    pass


class ApiError(IpregistryError):
    def __init__(self, code: str, message: str, resolution: str):
        self.code = code
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
