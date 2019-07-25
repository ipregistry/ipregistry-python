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

from . import cache
from . import model
from . import request

class IpregistryClient:
    def __init__(self, keyOrConfig, **kwargs):
        self._config = keyOrConfig if isinstance(keyOrConfig, IpregistryConfig) else IpregistryConfig(keyOrConfig)
        self._cache = kwargs["cache"] if "cache" in kwargs else cache.DefaultCache()
        self._requestHandler = kwargs["requestHandler"] if "requestHandler" in kwargs else request.DefaultRequestHandler(self._config)

        if not isinstance(self._cache, cache.IpregistryCache):
            raise ValueError("Given cache instance is not of type IpregistryCache")
        if not isinstance(self._requestHandler, request.IpregistryRequestHandler):
            raise ValueError("Given request handler instance is not of type IpregistryRequestHandler")

    def lookup(self, *args):
        length = len(args)
        if length == 0:
            return self._originLookup()
        elif length == 1:
            if isinstance(args[0], list):
                return self._batchLookup(args[0])
            elif isinstance(args[0], str):
                return self._singleLookup(args[0])
            else:
                raise ValueError('Invalid parameter type')
        else:
            raise ValueError("Invalid number of parameters")

    def _batchLookup(self, ips):
        print("Batch IP Lookup")

    def _originLookup(self):
        print("Origin IP Lookup")

    def _singleLookup(self, ip):
        # TODO: build cache key with options
        cacheKey = ip
        cacheValue = self._cache.get(cacheKey)

        if cacheValue is None:
            cacheValue = self._requestHandler.singleLookup(ip)
            self._cache.put(cacheKey, cacheValue)

        return cacheValue


class IpregistryConfig:
    def __init__(self, key, apiUrl="https://api.ipregistry.co", timeout=3):
        self.apiKey = key
        self.apiUrl = apiUrl
        self.timeout = timeout

    def __str__(self):
         return "apiKey={}, apiUrl={}, timeout={}".format(self.apiKey, self.apiUrl, self.timeout)


# client = IpregistryClient("tryout")
# try:
#     print(client.lookup("1.1.1.2").ip)
# except ApiError as e:
#     print(e.code)