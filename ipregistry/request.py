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
import urllib.parse
from abc import ABC, abstractmethod
from typing import Union

import requests

from .model import (ApiError, ApiResponse, ApiResponseCredits, ApiResponseThrottling, AutonomousSystem,
                    ClientError, IpInfo, LookupError, RequesterAutonomousSystem, RequesterIpInfo,
                    RequesterUserAgent, UserAgent)


class IpregistryRequestHandler(ABC):
    def __init__(self, config):
        self._config = config

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
            result += ("?" if i == 0 else "&") + key + "=" + urllib.parse.quote(value)
            i += 1

        return result


class DefaultRequestHandler(IpregistryRequestHandler):
    def batch_lookup_asns(self, asns, options):
        response = None
        try:
            response = requests.post(
                self._build_base_url('', options),
                data=json.dumps(list(map(lambda asn: "AS" + str(asn), asns))),
                headers=self.__headers(),
                timeout=self._config.timeout
            )
            response.raise_for_status()
            results = response.json().get('results', [])

            parsed_results = [
                LookupError(data) if 'code' in data else AutonomousSystem(**data)
                for data in results
            ]

            return self.build_api_response(response, parsed_results)
        except requests.HTTPError:
            self.__create_api_error(response)
        except Exception as e:
            raise ClientError(e)

    def batch_lookup_ips(self, ips, options):
        response = None
        try:
            response = requests.post(
                self._build_base_url('', options),
                data=json.dumps(ips),
                headers=self.__headers(),
                timeout=self._config.timeout
            )
            response.raise_for_status()
            results = response.json().get('results', [])

            parsed_results = [
                LookupError(data) if 'code' in data else IpInfo(**data)
                for data in results
            ]

            return self.build_api_response(response, parsed_results)
        except requests.HTTPError:
            self.__create_api_error(response)
        except Exception as e:
            raise ClientError(e)

    def batch_parse_user_agents(self, user_agents, options):
        response = None
        try:
            response = requests.post(
                self._build_base_url('user_agent', options),
                data=json.dumps(user_agents),
                headers=self.__headers(),
                timeout=self._config.timeout
            )
            response.raise_for_status()
            results = response.json().get('results', [])

            parsed_results = [
                LookupError(data) if 'code' in data else UserAgent(**data)
                for data in results
            ]

            return self.build_api_response(response, parsed_results)
        except requests.HTTPError:
            self.__create_api_error(response)
        except Exception as e:
            raise ClientError(e)

    def lookup_asn(self, asn, options):
        response = None
        try:
            response = requests.get(
                self._build_base_url(asn, options),
                headers=self.__headers(),
                timeout=self._config.timeout
            )
            response.raise_for_status()
            json_response = response.json()

            return self.build_api_response(
                response,
                RequesterAutonomousSystem(**json_response) if asn == 'AS'
                else AutonomousSystem(**json_response)
            )
        except requests.HTTPError:
            self.__create_api_error(response)
        except Exception as err:
            raise ClientError(err)

    def lookup_ip(self, ip, options):
        response = None
        try:
            response = requests.get(
                self._build_base_url(ip, options),
                headers=self.__headers(),
                timeout=self._config.timeout
            )
            response.raise_for_status()
            json_response = response.json()

            return self.build_api_response(
                response,
                RequesterIpInfo(**json_response) if ip == ''
                else IpInfo(**json_response)
            )
        except requests.HTTPError:
            self.__create_api_error(response)
        except Exception as err:
            raise ClientError(err)

    def origin_lookup_ip(self, options):
        return self.lookup_ip('', options)

    def origin_parse_user_agent(self, options):
        response = None
        try:
            response = requests.get(
                self._build_base_url('user_agent', options),
                headers=self.__headers(),
                timeout=self._config.timeout
            )
            response.raise_for_status()
            json_response = response.json()

            return self.build_api_response(
                response,
                RequesterUserAgent(**json_response)
            )
        except requests.HTTPError:
            self.__create_api_error(response)
        except Exception as err:
            raise ClientError(err)

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
        if response is not None:
            json_response = response.json()
            raise ApiError(json_response['code'], json_response['message'], json_response['resolution'])
        else:
            raise ClientError("HTTP Error occurred, but no response was received.")

    def __headers(self):
        python_version = sys.version.split()[0]
        lib_version = importlib.metadata.version('ipregistry')
        return {
            "authorization": "ApiKey " + self._config.api_key,
            "content-type": "application/json",
            "user-agent":
                "Ipregistry/" +
                lib_version +
                " (Library; Python/" +
                python_version +
                "; +https://github.com/ipregistry/ipregistry-python)"
        }
