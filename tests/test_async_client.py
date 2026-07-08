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
import unittest

try:
    import httpx
except ImportError:
    httpx = None

from ipregistry import AsyncIpregistryClient
from ipregistry.async_client import AsyncDefaultRequestHandler
from ipregistry.cache import InMemoryCache
from ipregistry.core import IpregistryConfig
from ipregistry.model import ApiError, ClientError


def build_client(responder, **kwargs):
    """Build an async client backed by a mock transport."""
    client_kwargs = {k: kwargs.pop(k) for k in ('cache', 'max_batch_size', 'batch_concurrency') if k in kwargs}
    kwargs.setdefault('retry_interval', 0)
    transport = httpx.MockTransport(responder)
    http_client = httpx.AsyncClient(transport=transport)
    config = IpregistryConfig("tryout", **kwargs)
    return AsyncIpregistryClient(config, client=http_client, **client_kwargs)


@unittest.skipIf(httpx is None, "httpx is not installed")
class TestAsyncIpregistryClient(unittest.IsolatedAsyncioTestCase):
    async def test_lookup_ip(self):
        """
        Test that a single async IP lookup returns parsed data
        """
        def responder(request):
            return httpx.Response(200, json={'ip': '8.8.8.8', 'type': 'IPv4'})

        async with build_client(responder) as client:
            response = await client.lookup_ip('8.8.8.8')
            self.assertEqual('8.8.8.8', response.data.ip)
            self.assertEqual('IPv4', response.data.type)

    async def test_lookup_ip_api_error(self):
        """
        Test that an API error response raises an ApiError
        """
        def responder(request):
            return httpx.Response(400, json={
                'code': 'INVALID_IP_ADDRESS', 'message': 'Invalid IP.', 'resolution': 'Fix it.'})

        async with build_client(responder) as client:
            with self.assertRaises(ApiError) as context:
                await client.lookup_ip('invalid')
            self.assertEqual('INVALID_IP_ADDRESS', context.exception.code)

    async def test_lookup_ip_non_string_input(self):
        """
        Test that a non-string input raises a ValueError
        """
        def responder(request):
            return httpx.Response(200, json={})

        async with build_client(responder) as client:
            with self.assertRaises(ValueError):
                await client.lookup_ip(1234)

    async def test_retry_on_server_error_then_success(self):
        """
        Test that a 5xx response is retried asynchronously
        """
        calls = []

        def responder(request):
            calls.append(request)
            if len(calls) == 1:
                return httpx.Response(500, json={
                    'code': 'INTERNAL', 'message': 'Oops.', 'resolution': 'Retry.'})
            return httpx.Response(200, json={'ip': '8.8.8.8'})

        async with build_client(responder) as client:
            response = await client.lookup_ip('8.8.8.8')
            self.assertEqual('8.8.8.8', response.data.ip)
            self.assertEqual(2, len(calls))

    async def test_transport_error_exhausted_raises_client_error(self):
        """
        Test that persistent transport errors surface as ClientError
        """
        def responder(request):
            raise httpx.ConnectError("connection refused")

        async with build_client(responder, retry_max_attempts=2) as client:
            with self.assertRaises(ClientError):
                await client.lookup_ip('8.8.8.8')

    async def test_lookup_ip_cached(self):
        """
        Test that async single IP lookups are served from the cache
        """
        calls = []

        def responder(request):
            calls.append(request)
            return httpx.Response(200, json={'ip': '8.8.8.8'})

        async with build_client(responder, cache=InMemoryCache()) as client:
            await client.lookup_ip('8.8.8.8')
            await client.lookup_ip('8.8.8.8')
            self.assertEqual(1, len(calls))

    async def test_origin_lookup_ip_bypasses_cache(self):
        """
        Test that async origin lookups are never cached
        """
        calls = []

        def responder(request):
            calls.append(request)
            return httpx.Response(200, json={'ip': '4.4.4.4', 'user_agent': {'name': 'curl'}})

        async with build_client(responder, cache=InMemoryCache()) as client:
            await client.origin_lookup_ip()
            await client.origin_lookup_ip()
            self.assertEqual(2, len(calls))

    async def test_batch_lookup_auto_split(self):
        """
        Test that async batches above max_batch_size are chunked
        and reassembled in input order
        """
        calls = []

        def responder(request):
            ips = json.loads(request.content)
            calls.append(ips)
            return httpx.Response(200, json={'results': [{'ip': ip} for ip in ips]})

        async with build_client(responder, max_batch_size=2, batch_concurrency=2) as client:
            ips = ['1.1.1.{}'.format(i) for i in range(5)]
            response = await client.batch_lookup_ips(ips)
            self.assertEqual(3, len(calls))
            self.assertEqual(ips, [info.ip for info in response.data])

    async def test_batch_lookup_mixed_results(self):
        """
        Test that per-entry errors surface as LookupError instances
        """
        def responder(request):
            return httpx.Response(200, json={'results': [
                {'ip': '1.1.1.1'},
                {'code': 'INVALID_IP_ADDRESS', 'message': 'Invalid IP.', 'resolution': 'Fix it.'},
            ]})

        async with build_client(responder) as client:
            response = await client.batch_lookup_ips(['1.1.1.1', 'invalid'])
            self.assertEqual('1.1.1.1', response.data[0].ip)
            self.assertEqual('INVALID_IP_ADDRESS', response.data[1].code)

    async def test_missing_httpx_raises_helpful_error(self):
        """
        Test that constructing the handler without httpx raises a helpful error
        """
        import ipregistry.async_client as async_client_module
        original = async_client_module.httpx
        async_client_module.httpx = None
        try:
            with self.assertRaises(ImportError) as context:
                AsyncDefaultRequestHandler(IpregistryConfig("tryout"))
            self.assertIn('ipregistry[async]', str(context.exception))
        finally:
            async_client_module.httpx = original


if __name__ == '__main__':
    unittest.main()
