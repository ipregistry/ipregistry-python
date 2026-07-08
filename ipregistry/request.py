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
import importlib
import json
import sys
import time
import urllib.parse
from abc import ABC, abstractmethod

from typing import Union

import requests

from .model import (ApiError, ApiResponse, ApiResponseCredits, ApiResponseThrottling, AutonomousSystem,
                    ClientError, IpInfo, IpregistryLookupError, RequesterAutonomousSystem,
                    RequesterIpInfo, RequesterUserAgent, UserAgent)


def _build_headers(config):
    """Build the HTTP headers shared by all Ipregistry API requests."""
    custom_user_agent = getattr(config, 'user_agent', None)
    if custom_user_agent:
        user_agent = custom_user_agent
    else:
        python_version = sys.version.split()[0]
        lib_version = importlib.metadata.version('ipregistry')
        user_agent = (
            "Ipregistry/" +
            lib_version +
            " (Library; Python/" +
            python_version +
            "; +https://github.com/ipregistry/ipregistry-python)"
        )

    return {
        "authorization": "ApiKey " + config.api_key,
        "content-type": "application/json",
        "user-agent": user_agent
    }


def _raise_api_error(response):
    """Raise an ApiError built from an error response, or a ClientError when
    the response is missing or its body is not a recognizable error payload."""
    if response is None:
        raise ClientError("HTTP Error occurred, but no response was received.")

    try:
        json_response = response.json()
        code = json_response['code']
        message = json_response['message']
        resolution = json_response.get('resolution')
    except (ValueError, KeyError, TypeError):
        raise ClientError(
            "HTTP error {} with unexpected response body.".format(response.status_code)
        )

    raise ApiError(code, message, resolution)


def _is_retryable_status(config, status_code):
    if status_code == 429:
        return config.retry_on_too_many_requests
    return status_code >= 500 and config.retry_on_server_error


def _backoff_interval(config, attempt):
    return config.retry_interval * (2 ** min(attempt - 1, 30))


def _retry_delay(config, response, attempt):
    if response.status_code == 429:
        retry_after = response.headers.get('retry-after')
        if retry_after is not None:
            try:
                seconds = int(retry_after)
                if seconds >= 0:
                    return seconds
            except ValueError:
                pass
    return _backoff_interval(config, attempt)


class IpregistryRequestHandler(ABC):
    def __init__(self, config):
        self._config = config

    def close(self):
        pass

    @abstractmethod
    def batch_lookup_asns(self, ips, options):
        pass

    @abstractmethod
    def batch_lookup_ips(self, ips, options):
        pass

    @abstractmethod
    def batch_parse_user_agents(self, user_agents, options):
        pass

    @abstractmethod
    def lookup_asn(self, asn, options):
        pass

    @abstractmethod
    def lookup_ip(self, ip, options):
        pass

    @abstractmethod
    def origin_lookup_ip(self, options):
        pass

    @abstractmethod
    def origin_parse_user_agent(self, options):
        pass

    def _build_base_url(self, resource, options):
        result = self._config.base_url + "/" + resource

        i = 0
        for key, value in options.items():
            if isinstance(value, bool):
                value = 'true' if value is True else 'false'
            result += ("?" if i == 0 else "&") + key + "=" + urllib.parse.quote(str(value))
            i += 1

        return result


class DefaultRequestHandler(IpregistryRequestHandler):
    def __init__(self, config, session=None):
        super().__init__(config)
        self._owns_session = session is None
        self._session = requests.Session() if session is None else session

    def close(self):
        if self._owns_session:
            self._session.close()

    def batch_lookup_asns(self, asns, options):
        response = self._request_with_retry(
            'POST',
            self._build_base_url('', options),
            data=json.dumps(["AS" + str(asn) for asn in asns])
        )
        try:
            results = response.json().get('results', [])
            parsed_results = [
                IpregistryLookupError(data) if 'code' in data else AutonomousSystem(**data)
                for data in results
            ]
            return self.build_api_response(response, parsed_results)
        except Exception as e:
            raise ClientError(e)

    def batch_lookup_ips(self, ips, options):
        response = self._request_with_retry(
            'POST',
            self._build_base_url('', options),
            data=json.dumps(ips)
        )
        try:
            results = response.json().get('results', [])
            parsed_results = [
                IpregistryLookupError(data) if 'code' in data else IpInfo(**data)
                for data in results
            ]
            return self.build_api_response(response, parsed_results)
        except Exception as e:
            raise ClientError(e)

    def batch_parse_user_agents(self, user_agents, options):
        response = self._request_with_retry(
            'POST',
            self._build_base_url('user_agent', options),
            data=json.dumps(user_agents)
        )
        try:
            results = response.json().get('results', [])
            parsed_results = [
                IpregistryLookupError(data) if 'code' in data else UserAgent(**data)
                for data in results
            ]
            return self.build_api_response(response, parsed_results)
        except Exception as e:
            raise ClientError(e)

    def lookup_asn(self, asn, options):
        response = self._request_with_retry('GET', self._build_base_url(asn, options))
        try:
            json_response = response.json()
            return self.build_api_response(
                response,
                RequesterAutonomousSystem(**json_response) if asn == 'AS'
                else AutonomousSystem(**json_response)
            )
        except Exception as e:
            raise ClientError(e)

    def lookup_ip(self, ip, options):
        response = self._request_with_retry('GET', self._build_base_url(ip, options))
        try:
            json_response = response.json()
            return self.build_api_response(
                response,
                RequesterIpInfo(**json_response) if ip == ''
                else IpInfo(**json_response)
            )
        except Exception as e:
            raise ClientError(e)

    def origin_lookup_ip(self, options):
        return self.lookup_ip('', options)

    def origin_parse_user_agent(self, options):
        response = self._request_with_retry('GET', self._build_base_url('user_agent', options))
        try:
            json_response = response.json()
            return self.build_api_response(
                response,
                RequesterUserAgent(**json_response)
            )
        except Exception as e:
            raise ClientError(e)

    def _request_with_retry(self, method, url, data=None):
        """Perform an HTTP request, retrying transient network errors and,
        depending on the configuration, 5xx and 429 responses with exponential
        backoff (honoring the Retry-After header for 429 responses)."""
        max_attempts = max(1, self._config.retry_max_attempts)
        attempt = 0

        while True:
            attempt += 1
            try:
                response = self._session.request(
                    method,
                    url,
                    data=data,
                    headers=self.__headers(),
                    timeout=self._config.timeout
                )
            except requests.RequestException as e:
                if attempt < max_attempts:
                    time.sleep(self.__backoff_interval(attempt))
                    continue
                raise ClientError(e)

            if response.status_code >= 400:
                if attempt < max_attempts and self.__is_retryable_status(response.status_code):
                    time.sleep(self.__retry_delay(response, attempt))
                    continue
                self.__create_api_error(response)

            return response

    def __is_retryable_status(self, status_code):
        return _is_retryable_status(self._config, status_code)

    def __retry_delay(self, response, attempt):
        return _retry_delay(self._config, response, attempt)

    def __backoff_interval(self, attempt):
        return _backoff_interval(self._config, attempt)

    @staticmethod
    def build_api_response(response, data):
        throttling_limit = DefaultRequestHandler.__convert_to_int(response.headers.get('x-rate-limit-limit'))
        throttling_remaining = DefaultRequestHandler.__convert_to_int(response.headers.get('x-rate-limit-remaining'))
        throttling_reset = DefaultRequestHandler.__convert_to_int(response.headers.get('x-rate-limit-reset'))

        ipregistry_credits_consumed = DefaultRequestHandler.__convert_to_int(
            response.headers.get('ipregistry-credits-consumed'))
        ipregistry_credits_remaining = DefaultRequestHandler.__convert_to_int(
            response.headers.get('ipregistry-credits-remaining'))

        return ApiResponse(
            ApiResponseCredits(
                ipregistry_credits_consumed,
                ipregistry_credits_remaining,
            ),
            data,
            ApiResponseThrottling(
                throttling_limit,
                throttling_remaining,
                throttling_reset
            )
        )

    @staticmethod
    def __convert_to_int(value: str) -> Union[int, None]:
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def __create_api_error(response):
        _raise_api_error(response)

    def __headers(self):
        return _build_headers(self._config)
