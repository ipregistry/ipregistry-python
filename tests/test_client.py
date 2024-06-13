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

from ipregistry import ApiError, IpInfo, LookupError, ClientError
from ipregistry.cache import InMemoryCache, NoCache
from ipregistry.core import IpregistryClient, IpregistryConfig


class TestIpregistryClient(unittest.TestCase):

    def test_batch_lookup_ips(self):
        """
        Test batch ips lookup with valid and invalid inputs
        """
        client = IpregistryClient(os.getenv('IPREGISTRY_API_KEY'))
        response = client.batch_lookup_ips(['1.1.1.1', 'invalid', '8.8.8.8'])
        self.assertEqual(3, len(response.data))
        self.assertEqual(True, isinstance(response.data[0], IpInfo))
        self.assertEqual(True, isinstance(response.data[1], LookupError))
        self.assertEqual('INVALID_IP_ADDRESS', response.data[1].code)
        self.assertEqual(True, isinstance(response.data[2], IpInfo))

    def test_client_cache_default(self):
        """
        Test that default cache is an instance of NoCache
        """
        client = IpregistryClient("tryout")
        self.assertEqual(True, isinstance(client._cache, NoCache))

    def test_client_cache_inmemory_ip_lookup(self):
        """
        Test the client in memory cache
        """
        client = IpregistryClient(os.getenv('IPREGISTRY_API_KEY'), cache=InMemoryCache(maxsize=2048, ttl=600))
        lookup_ip_response = client.lookup_ip('1.1.1.3')
        lookup_ip_response2 = client.lookup_ip('1.1.1.3')

        self.assertEqual(1, lookup_ip_response.credits.consumed)
        self.assertEqual(0, lookup_ip_response2.credits.consumed)

    def test_client_cache_inmemory_batch_ips_lookup(self):
        """
        Test the client in memory cache
        """
        client = IpregistryClient(os.getenv('IPREGISTRY_API_KEY'), cache=InMemoryCache(maxsize=2048, ttl=600))
        lookup_ip_response = client.lookup_ip('1.1.1.3')
        batch_ips_response = client.batch_lookup_ips(['1.1.1.1', '1.1.1.3'])

        self.assertEqual(1, lookup_ip_response.credits.consumed)
        self.assertEqual(1, batch_ips_response.credits.consumed)

        batch_ips_response2 = client.batch_lookup_ips(['1.1.1.1', '1.1.1.3'])
        self.assertEqual(0, batch_ips_response2.credits.consumed)

    def test_lookup_ip(self):
        """
        Test that a simple lookup returns data
        """
        client = IpregistryClient(os.getenv('IPREGISTRY_API_KEY'))
        response = client.lookup_ip('8.8.8.8')
        self.assertIsNotNone(response.data.ip)
        self.assertIsNotNone(response.data.company.domain)
        self.assertEqual('US', response.data.location.country.code)

    def test_lookup_ip_invalid_input(self):
        """
        Test that an IP lookup with an invalid input fails with an ApiError
        """
        client = IpregistryClient(os.getenv('IPREGISTRY_API_KEY'))
        with self.assertRaises(ApiError) as context:
            response = client.lookup_ip('invalid')
        print("test", context.exception)
        self.assertEqual('INVALID_IP_ADDRESS', context.exception.code)

    def test_lookup_ip_cache(self):
        """
        Test consecutive lookup with in-memory cache
        """
        client = IpregistryClient(os.getenv('IPREGISTRY_API_KEY'), cache=InMemoryCache(maxsize=2048, ttl=600))
        response = client.lookup_ip('8.8.8.8')
        response = client.lookup_ip('8.8.8.8')
        self.assertIsNotNone(response.data.ip)
        self.assertIsNotNone(response.data.company.domain)

    def test_response_metadata(self):
        """
        Test metadata returned for each successful response
        """
        client = IpregistryClient(os.getenv('IPREGISTRY_API_KEY'))
        batch_ips_lookup_response = client.batch_lookup_ips(['1.1.1.1', 'invalid', '8.8.8.8'])
        lookup_ip_response = client.lookup_ip('1.1.1.2')

        self.assertEqual(3, batch_ips_lookup_response.credits.consumed)
        self.assertEqual(1, lookup_ip_response.credits.consumed)

        self.assertIsNotNone(batch_ips_lookup_response.credits.remaining)
        self.assertIsNotNone(lookup_ip_response.credits.remaining)

    def test_lookup_timeout(self):
        """
        Test a client error is raised upon connection timeout
        """
        client = IpregistryClient(IpregistryConfig(os.getenv('IPREGISTRY_API_KEY'), "https://api.ipregistry.co",
                                                   0.0001))
        with self.assertRaises(ClientError):
            client.lookup_ip('1.1.1.1')


if __name__ == '__main__':
    unittest.main()
