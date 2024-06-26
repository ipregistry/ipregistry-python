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

from ipregistry import ApiError, AutonomousSystem, IpInfo, LookupError, ClientError, UserAgent
from ipregistry.cache import InMemoryCache, NoCache
from ipregistry.core import IpregistryClient, IpregistryConfig


class TestIpregistryClient(unittest.TestCase):

    def test_batch_lookup_asns(self):
        """
        Test batch asns lookup with valid and invalid inputs
        """
        client = IpregistryClient(os.getenv('IPREGISTRY_API_KEY'))
        response = client.batch_lookup_asns([33, 'invalid', -1])
        print(response)
        self.assertEqual(3, len(response.data))
        self.assertEqual(True, isinstance(response.data[0], AutonomousSystem))
        self.assertEqual(True, isinstance(response.data[1], LookupError))
        self.assertEqual('INVALID_ASN', response.data[1].code)
        self.assertEqual(True, isinstance(response.data[2], LookupError))
        self.assertEqual('INVALID_ASN', response.data[2].code)

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

    def test_batch_parse_user_agents(self):
        """
        Test batch parse user agents
        """
        client = IpregistryClient(os.getenv('IPREGISTRY_API_KEY'))
        response = client.batch_parse_user_agents([
            'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36',
            'Mozilla/5.0 (Linux; Android 13; SM-S901U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36',
            'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36'
        ])

        self.assertEqual(4, len(response.data))
        self.assertEqual(5, response.credits.consumed)

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

    def test_lookup_asn(self):
        """
        Test Autonomous System data lookup by ASN
        """
        client = IpregistryClient(os.getenv('IPREGISTRY_API_KEY'))
        response = client.lookup_asn(400923)
        self.assertEqual(400923, response.data.asn)
        self.assertEqual(1, response.credits.consumed)
        self.assertIsNotNone(response.data.relationships)

    def test_lookup_ip(self):
        """
        Test that a simple IP lookup returns data
        """
        client = IpregistryClient(os.getenv('IPREGISTRY_API_KEY'))
        response = client.lookup_ip('8.8.8.8')
        self.assertIsNotNone(response.data.ip)
        self.assertIsNotNone(response.data.company.domain)
        self.assertEqual('US', response.data.location.country.code)

    def test_lookup_ip_with_eu_base_url(self):
        """
        Test a simple IP lookup with the EU base URL
        """
        client = IpregistryClient(IpregistryConfig(os.getenv('IPREGISTRY_API_KEY')).with_eu_base_url())
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

    def test_lookup_timeout(self):
        """
        Test a client error is raised upon connection timeout
        """
        client = IpregistryClient(IpregistryConfig(os.getenv('IPREGISTRY_API_KEY'), "https://api.ipregistry.co",
                                                   0.0001))
        with self.assertRaises(ClientError):
            client.lookup_ip('1.1.1.1')

    def test_origin_asn(self):
        """
        Test origin Autonomous System data lookup
        """
        client = IpregistryClient(os.getenv('IPREGISTRY_API_KEY'))
        response = client.origin_lookup_asn()
        self.assertIsNotNone(response.data.asn)
        self.assertEqual(1, response.credits.consumed)
        self.assertIsNotNone(response.data.relationships)

    def test_origin_lookup_ip(self):
        """
        Test that a simple origin IP lookup returns data
        """
        client = IpregistryClient(os.getenv('IPREGISTRY_API_KEY'))
        response = client.origin_lookup_ip()
        self.assertIsNotNone(response.data.ip)
        self.assertIsNotNone(response.data.user_agent)

    def test_origin_parse_user_agent(self):
        """
        Test origin parse user agent
        """
        client = IpregistryClient(os.getenv('IPREGISTRY_API_KEY'))
        response = client.origin_parse_user_agent()

        self.assertIsInstance(response.data, UserAgent)
        self.assertEqual(1, response.credits.consumed)

    def test_parse_user_agent(self):
        """
        Test user agent parsing
        """
        client = IpregistryClient(os.getenv('IPREGISTRY_API_KEY'))
        response = client.parse_user_agent('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36')

        self.assertIsInstance(response.data, UserAgent)
        self.assertEqual(1, response.credits.consumed)

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


if __name__ == '__main__':
    unittest.main()
