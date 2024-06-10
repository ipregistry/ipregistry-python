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
from .model import LookupError
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

    def lookup(self, ip_or_list='', **options):
        if ip_or_list == '':
            return self._origin_lookup(options)
        elif isinstance(ip_or_list, list):
            return self._batch_lookup(ip_or_list, options)
        elif isinstance(ip_or_list, str):
            return self._single_lookup(ip_or_list, options)
        else:
            raise ValueError("Invalid parameter type")

    def _batch_lookup(self, ips, options):
        sparse_cache = [None] * len(ips)
        cache_misses = []

        for i in range(0, len(ips)):
            ip = ips[i]
            cache_key = self._build_cache_key(ip, options)
            cache_value = self._cache.get(cache_key)
            if cache_value is None:
                cache_misses.append(ip)
            else:
                sparse_cache[i] = cache_value

        result = [None] * len(ips)
        fresh_ip_info = self._requestHandler.batch_lookup(cache_misses, options)
        j = 0
        k = 0

        for cachedIpInfo in sparse_cache:
            if cachedIpInfo is None:
                if not isinstance(fresh_ip_info[k], LookupError):
                    self._cache.put(self._build_cache_key(ips[j], options), fresh_ip_info[k])
                result[j] = fresh_ip_info[k]
                k += 1
            else:
                result[j] = cachedIpInfo
            j += 1

        return result

    def _origin_lookup(self, options):
        return self._single_lookup('', options)

    def _single_lookup(self, ip, options):
        cache_key = self._build_cache_key(ip, options)
        cache_value = self._cache.get(cache_key)

        if cache_value is None:
            cache_value = self._requestHandler.single_lookup(ip, options)
            self._cache.put(cache_key, cache_value)

        return cache_value

    def _build_cache_key(self, ip, options):
        result = ip

        for key, value in options.items():
            if isinstance(value, bool):
                value = 'true' if value is True else 'false'
            result += ';' + key + '=' + value

        return result

    def _is_api_error(self, data):
        return 'code' in data


class IpregistryConfig:
    def __init__(self, key, base_url="https://api.ipregistry.co", timeout=15):
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
