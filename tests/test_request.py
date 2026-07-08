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

import unittest

import requests
import requests_mock

from ipregistry.core import IpregistryConfig
from ipregistry.model import ApiError, ClientError
from ipregistry.request import DefaultRequestHandler


def build_response(status_code, content):
    response = requests.Response()
    response.status_code = status_code
    response._content = content
    return response


def build_mocked_handler(**config_kwargs):
    """Build a request handler whose session is backed by a mock adapter."""
    config_kwargs.setdefault('retry_interval', 0)
    adapter = requests_mock.Adapter()
    session = requests.Session()
    session.mount('https://', adapter)
    handler = DefaultRequestHandler(IpregistryConfig("tryout", **config_kwargs), session=session)
    return handler, adapter


class TestIpregistryRequestHandler(unittest.TestCase):
    def test_build_base_url_option_value_types(self):
        """
        Test that URL building handles boolean and non-string option values
        """
        handler = DefaultRequestHandler(IpregistryConfig("tryout"))
        url = handler._build_base_url('8.8.8.8', {'hostname': True, 'fields': 'location', 'n': 5})
        self.assertEqual('https://api.ipregistry.co/8.8.8.8?hostname=true&fields=location&n=5', url)

    def test_create_api_error_json_response(self):
        """
        Test that a JSON error response raises an ApiError with its fields
        """
        response = build_response(
            400, b'{"code": "INVALID_IP_ADDRESS", "message": "Invalid IP.", "resolution": "Fix it."}')
        with self.assertRaises(ApiError) as context:
            DefaultRequestHandler._DefaultRequestHandler__create_api_error(response)
        self.assertEqual('INVALID_IP_ADDRESS', context.exception.code)
        self.assertEqual('Invalid IP.', context.exception.message)

    def test_create_api_error_non_json_response(self):
        """
        Test that a non-JSON error response, e.g. an HTML page returned
        by a gateway, raises a ClientError instead of a JSONDecodeError
        """
        response = build_response(502, b'<html>Bad Gateway</html>')
        with self.assertRaises(ClientError) as context:
            DefaultRequestHandler._DefaultRequestHandler__create_api_error(response)
        self.assertIn('502', str(context.exception))

    def test_default_user_agent_header(self):
        """
        Test that the default User-Agent header identifies the library
        """
        handler, adapter = build_mocked_handler()
        adapter.register_uri('GET', 'https://api.ipregistry.co/8.8.8.8', json={'ip': '8.8.8.8'})
        handler.lookup_ip('8.8.8.8', {})
        self.assertTrue(adapter.last_request.headers['user-agent'].startswith('Ipregistry/'))

    def test_custom_user_agent_header(self):
        """
        Test that a configured User-Agent value overrides the default header
        """
        handler, adapter = build_mocked_handler(user_agent='MyApp/1.0')
        adapter.register_uri('GET', 'https://api.ipregistry.co/8.8.8.8', json={'ip': '8.8.8.8'})
        handler.lookup_ip('8.8.8.8', {})
        self.assertEqual('MyApp/1.0', adapter.last_request.headers['user-agent'])

    def test_owned_session_lifecycle(self):
        """
        Test that the handler creates its own pooled session and closes it
        """
        handler = DefaultRequestHandler(IpregistryConfig("tryout"))
        self.assertIsInstance(handler._session, requests.Session)
        self.assertTrue(handler._owns_session)
        handler.close()

    def test_custom_session_not_owned(self):
        """
        Test that a caller-provided session is used and not closed by the handler
        """
        session = requests.Session()
        try:
            handler = DefaultRequestHandler(IpregistryConfig("tryout"), session=session)
            self.assertIs(session, handler._session)
            self.assertFalse(handler._owns_session)
            handler.close()
            self.assertTrue(len(session.adapters) > 0)
        finally:
            session.close()

    def test_retry_on_server_error_then_success(self):
        """
        Test that a 5xx response is retried and the retried request succeeds
        """
        handler, adapter = build_mocked_handler()
        adapter.register_uri('GET', 'https://api.ipregistry.co/8.8.8.8', [
            {'status_code': 500, 'json': {'code': 'INTERNAL', 'message': 'Oops.', 'resolution': 'Retry.'}},
            {'status_code': 200, 'json': {'ip': '8.8.8.8'}},
        ])
        response = handler.lookup_ip('8.8.8.8', {})
        self.assertEqual('8.8.8.8', response.data.ip)
        self.assertEqual(2, adapter.call_count)

    def test_no_retry_when_server_error_retry_disabled(self):
        """
        Test that 5xx responses are not retried when retry_on_server_error is False
        """
        handler, adapter = build_mocked_handler(retry_on_server_error=False)
        adapter.register_uri('GET', 'https://api.ipregistry.co/8.8.8.8',
                             status_code=500,
                             json={'code': 'INTERNAL', 'message': 'Oops.', 'resolution': 'Retry.'})
        with self.assertRaises(ApiError):
            handler.lookup_ip('8.8.8.8', {})
        self.assertEqual(1, adapter.call_count)

    def test_retry_attempts_exhausted(self):
        """
        Test that retrying stops after retry_max_attempts attempts
        """
        handler, adapter = build_mocked_handler(retry_max_attempts=2)
        adapter.register_uri('GET', 'https://api.ipregistry.co/8.8.8.8',
                             status_code=503,
                             json={'code': 'INTERNAL', 'message': 'Oops.', 'resolution': 'Retry.'})
        with self.assertRaises(ApiError):
            handler.lookup_ip('8.8.8.8', {})
        self.assertEqual(2, adapter.call_count)

    def test_too_many_requests_not_retried_by_default(self):
        """
        Test that a 429 response is not retried unless opted in
        """
        handler, adapter = build_mocked_handler()
        adapter.register_uri('GET', 'https://api.ipregistry.co/8.8.8.8',
                             status_code=429,
                             json={'code': 'TOO_MANY_REQUESTS', 'message': 'Slow down.', 'resolution': 'Wait.'})
        with self.assertRaises(ApiError) as context:
            handler.lookup_ip('8.8.8.8', {})
        self.assertEqual('TOO_MANY_REQUESTS', context.exception.code)
        self.assertEqual(1, adapter.call_count)

    def test_too_many_requests_retried_honoring_retry_after(self):
        """
        Test that a 429 response is retried when opted in, honoring Retry-After
        """
        handler, adapter = build_mocked_handler(retry_on_too_many_requests=True)
        adapter.register_uri('GET', 'https://api.ipregistry.co/8.8.8.8', [
            {'status_code': 429, 'headers': {'Retry-After': '0'},
             'json': {'code': 'TOO_MANY_REQUESTS', 'message': 'Slow down.', 'resolution': 'Wait.'}},
            {'status_code': 200, 'json': {'ip': '8.8.8.8'}},
        ])
        response = handler.lookup_ip('8.8.8.8', {})
        self.assertEqual('8.8.8.8', response.data.ip)
        self.assertEqual(2, adapter.call_count)

    def test_transport_error_retried(self):
        """
        Test that transient network errors are retried
        """
        handler, adapter = build_mocked_handler()
        adapter.register_uri('GET', 'https://api.ipregistry.co/8.8.8.8', [
            {'exc': requests.exceptions.ConnectTimeout},
            {'status_code': 200, 'json': {'ip': '8.8.8.8'}},
        ])
        response = handler.lookup_ip('8.8.8.8', {})
        self.assertEqual('8.8.8.8', response.data.ip)

    def test_transport_error_exhausted_raises_client_error(self):
        """
        Test that a persistent network error surfaces as a ClientError
        """
        handler, adapter = build_mocked_handler(retry_max_attempts=2)
        adapter.register_uri('GET', 'https://api.ipregistry.co/8.8.8.8',
                             exc=requests.exceptions.ConnectionError)
        with self.assertRaises(ClientError):
            handler.lookup_ip('8.8.8.8', {})
        self.assertEqual(2, adapter.call_count)

    def test_origin_lookup_ip_not_double_retried(self):
        """
        Test that origin_lookup_ip does not retry on top of lookup_ip retries
        """
        handler, adapter = build_mocked_handler(retry_max_attempts=2)
        adapter.register_uri('GET', 'https://api.ipregistry.co/',
                             status_code=500,
                             json={'code': 'INTERNAL', 'message': 'Oops.', 'resolution': 'Retry.'})
        with self.assertRaises(ApiError):
            handler.origin_lookup_ip({})
        self.assertEqual(2, adapter.call_count)

    def test_create_api_error_no_response(self):
        """
        Test that a missing response raises a ClientError
        """
        with self.assertRaises(ClientError):
            DefaultRequestHandler._DefaultRequestHandler__create_api_error(None)


if __name__ == '__main__':
    unittest.main()
