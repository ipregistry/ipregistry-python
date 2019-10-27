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

import abc, six

from cachetools import TTLCache

@six.add_metaclass(abc.ABCMeta)
class IpregistryCache:
    @abc.abstractmethod
    def get(self, key):
        pass

    @abc.abstractmethod
    def put(self, key, data):
        pass

    @abc.abstractmethod
    def invalidate(self, key):
        pass

    @abc.abstractmethod
    def invalidateAll(self):
        pass

class DefaultCache(IpregistryCache):
    def __init__(self, maxsize=2048, ttl=600):
        self._cache = TTLCache(maxsize, ttl)

    def get(self, key):
        try:
            return self._cache[key]
        except:
            return None

    def put(self, key, data):
        self._cache[key] = data

    def invalidate(self, key):
        del self._cache[key]

    def invalidateAll(self):
        for key in self._cache:
            del self._cache[key]

class NoCache(IpregistryCache):
    def __init__(self, maxsize=2048, ttl=86400):
        pass

    def get(self, key):
        return None

    def put(self, key, data):
        pass

    def invalidate(self, key):
        pass

    def invalidateAll(self):
        pass
