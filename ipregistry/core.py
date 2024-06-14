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
from .cache import IpregistryCache, NoCache
from .json import AutonomousSystem, IpInfo
from .model import LookupError, ApiResponse, ApiResponseCredits, ApiResponseThrottling
from .request import DefaultRequestHandler, IpregistryRequestHandler


class IpregistryClient:
    def __init__(self, key_or_config, **kwargs):
        self._config = key_or_config if isinstance(key_or_config, IpregistryConfig) else IpregistryConfig(key_or_config)
        self._cache = kwargs["cache"] if "cache" in kwargs else NoCache()
        self._requestHandler = kwargs["requestHandler"] if "requestHandler" in kwargs else DefaultRequestHandler(self._config)

        if not isinstance(self._cache, IpregistryCache):
            raise ValueError("Given cache instance is not of type IpregistryCache")
        if not isinstance(self._requestHandler, IpregistryRequestHandler):
            raise ValueError("Given request handler instance is not of type IpregistryRequestHandler")

    def batch_lookup_asns(self, ips, **options):
        return self.batch_request(ips, self._requestHandler.batch_lookup_asns, **options)

    def batch_lookup_ips(self, ips, **options):
        return self.batch_request(ips, self._requestHandler.batch_lookup_ips, **options)

    def batch_parse_user_agents(self, user_agents, **options):
        return self.batch_request(user_agents, self._requestHandler.batch_parse_user_agents, **options)

    def batch_request(self, items, request_handler_func, **options):
        sparse_cache = [None] * len(items)
        cache_misses = []

        for i in range(len(items)):
            item = items[i]
            cache_key = self.__build_cache_key(item, options)
            cache_value = self._cache.get(cache_key)
            if cache_value is None:
                cache_misses.append(item)
            else:
                sparse_cache[i] = cache_value

        result = [None] * len(items)
        if len(cache_misses) > 0:
            response = request_handler_func(cache_misses, options)
        else:
            response = ApiResponse(
                ApiResponseCredits(),
                [],
                ApiResponseThrottling()
            )

        fresh_item_info = response.data
        j = 0
        k = 0

        for cached_item_info in sparse_cache:
            if cached_item_info is None:
                if not isinstance(fresh_item_info[k], LookupError):
                    self._cache.put(self.__build_cache_key(items[j], options), fresh_item_info[k])
                result[j] = fresh_item_info[k]
                k += 1
            else:
                result[j] = cached_item_info
            j += 1

        response.data = result

        return response

    def lookup_asn(self, asn, **options):
        return self.__lookup_asn(asn, options)

    def lookup_ip(self, ip, **options):
        if isinstance(ip, str):
            return self.__lookup_ip(ip, options)
        else:
            raise ValueError("Invalid value for 'ip' parameter: " + ip)

    def origin_lookup_asn(self, **options):
        return self.__lookup_asn('AS', options)

    def origin_lookup_ip(self, **options):
        return self.__lookup_ip('', options)

    def origin_parse_user_agent(self, **options):
        return self._requestHandler.origin_parse_user_agent(options)

    def __lookup_asn(self, asn, options):
        return self.__lookup(
            'AS' + str(asn) if IpregistryClient.__is_number(asn) else 'AS',
            options, self._requestHandler.lookup_asn,
            AutonomousSystem)

    def __lookup_ip(self, ip, options):
        return self.__lookup(ip, options, self._requestHandler.lookup_ip, IpInfo)

    def __lookup(self, key, options, lookup_func, response_type):
        cache_key = self.__build_cache_key(key, options)
        cache_value = self._cache.get(cache_key)

        if cache_value is None:
            response = lookup_func(key, options)
            if isinstance(response.data, response_type):
                self._cache.put(cache_key, response.data)
            return response

        return ApiResponse(
            ApiResponseCredits(),
            cache_value,
            ApiResponseThrottling()
        )

    def parse_user_agent(self, user_agent, **options):
        response = self.batch_parse_user_agents([user_agent], **options)
        response.data = response.data[0]
        return response

    @staticmethod
    def __build_cache_key(key, options):
        result = key

        for key, value in options.items():
            if isinstance(value, bool):
                value = 'true' if value is True else 'false'
            result += ';' + key + '=' + value

        return result

    @staticmethod
    def __is_api_error(data):
        return 'code' in data

    @staticmethod
    def __is_number(value):
        try:
            # Try converting the value to a float
            float(value)
            return True
        except ValueError:
            return False


class IpregistryConfig:
    def __init__(self, key, base_url="https://api.ipregistry.co", timeout=5):
        """
        Initialize the IpregistryConfig instance.

        Parameters:
        key (str): The API key for accessing the Ipregistry service.
        base_url (str): The base URL for the Ipregistry API. Defaults to "https://api.ipregistry.co".
                        There also exists a European Union (EU) base URL "https://eu.api.ipregistry.co"
                        that can be used to ensure requests are handled by nodes hosted in the EU only.
        timeout (int): The timeout duration (in seconds) for API requests. Defaults to 15 seconds.
        """
        self.api_key = key
        self.base_url = base_url
        self.timeout = timeout

    def __str__(self):
        """
        Return a string representation of the IpregistryConfig instance.

        Returns:
        str: A string containing the API key, base URL, and timeout value.
        """
        return "api_key={}, base_url={}, timeout={}".format(self.api_key, self.base_url, self.timeout)
