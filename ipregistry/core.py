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

import json

from .cache import IpregistryCache, NoCache
from .model import LookupError
from .request import DefaultRequestHandler, IpregistryRequestHandler

class IpregistryClient:
    def __init__(self, keyOrConfig, **kwargs):
        self._config = keyOrConfig if isinstance(keyOrConfig, IpregistryConfig) else IpregistryConfig(keyOrConfig)
        self._cache = kwargs["cache"] if "cache" in kwargs else NoCache()
        self._requestHandler = kwargs["requestHandler"] if "requestHandler" in kwargs else DefaultRequestHandler(self._config)

        if not isinstance(self._cache, IpregistryCache):
            raise ValueError("Given cache instance is not of type IpregistryCache")
        if not isinstance(self._requestHandler, IpregistryRequestHandler):
            raise ValueError("Given request handler instance is not of type IpregistryRequestHandler")

    def lookup(self, ipOrList='', **options):
        if ipOrList == '':
            return self._originLookup(options)
        elif isinstance(ipOrList, list):
            return self._batchLookup(ipOrList, options)
        elif isinstance(ipOrList, str):
            return self._singleLookup(ipOrList, options)
        else:
            raise ValueError("Invalid parameter type")

    def _batchLookup(self, ips, options):
        sparseCache = [None] * len(ips)
        cacheMisses = []

        for i in range(0, len(ips)):
            ip = ips[i]
            cacheKey = self._buildCacheKey(ip, options)
            cacheValue = self._cache.get(cacheKey)
            if cacheValue is None:
                cacheMisses.append(ip)
            else:
                sparseCache[i] = cacheValue

        result = [None] * len(ips)
        freshIpInfo = self._requestHandler.batchLookup(cacheMisses, options)
        j = 0
        k = 0

        for cachedIpInfo in sparseCache:
            if cachedIpInfo is None:
                if not isinstance(freshIpInfo[k], LookupError):
                    self._cache.put(self._buildCacheKey(ips[j], options), freshIpInfo[k])
                result[j] = freshIpInfo[k]
                k += 1
            else:
                result[j] = cachedIpInfo
            j += 1

        return result

    def _originLookup(self, options):
        return self._singleLookup('', options)

    def _singleLookup(self, ip, options):
        cacheKey = self._buildCacheKey(ip, options)
        cacheValue = self._cache.get(cacheKey)

        if cacheValue is None:
            cacheValue = self._requestHandler.singleLookup(ip, options)
            self._cache.put(cacheKey, cacheValue)

        return cacheValue

    def _buildCacheKey(self, ip, options):
        result = ip

        for key, value in options.items():
            if isinstance(value, bool):
                value = 'true' if value is True else 'false'
            result += ';' + key + '=' + value

        return result

    def _isApiError(self, data):
        return 'code' in data

class IpregistryConfig:
    def __init__(self, key, apiUrl="https://api.ipregistry.co", timeout=15):
        self.apiKey = key
        self.apiUrl = apiUrl
        self.timeout = timeout

    def __str__(self):
         return "apiKey={}, apiUrl={}, timeout={}".format(self.apiKey, self.apiUrl, self.timeout)
