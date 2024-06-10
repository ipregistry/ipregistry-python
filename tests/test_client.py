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

import os
import unittest

from ipregistry.cache import InMemoryCache, NoCache
from ipregistry.core import IpregistryClient


class TestIpregistryClient(unittest.TestCase):
    def test_defaultclient_cache(self):
        """
        Test that default cache is an instance of NoCache
        """
        client = IpregistryClient("")
        self.assertEqual(True, isinstance(client._cache, NoCache))

    def test_simple_lookup(self):
        """
        Test that a simple lookup returns data
        """
        client = IpregistryClient(os.getenv('IPREGISTRY_API_KEY'))
        response = client.lookup('8.8.8.8')
        self.assertIsNotNone(response.ip)
        self.assertIsNotNone(response.company.domain)
        self.assertEqual('US', response.location.country.code)

    def test_simple_lookup_in_memory_cache(self):
        """
        Test consecutive lookup with in-memory cache
        """
        client = IpregistryClient(os.getenv('IPREGISTRY_API_KEY'), cache=InMemoryCache(maxsize=2048, ttl=600))
        response = client.lookup('8.8.8.8')
        response = client.lookup('8.8.8.8')
        self.assertIsNotNone(response.ip)
        self.assertIsNotNone(response.company.domain)


if __name__ == '__main__':
    unittest.main()
