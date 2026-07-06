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

from ipregistry.core import IpregistryConfig
from ipregistry.model import ApiError, ClientError
from ipregistry.request import DefaultRequestHandler


def build_response(status_code, content):
    response = requests.Response()
    response.status_code = status_code
    response._content = content
    return response


class TestIpregistryRequestHandler(unittest.TestCase):
    def test_create_api_error_json_response(self):
        """
        Test that a JSON error response raises an ApiError with its fields
        """
        response = build_response(400, b'{"code": "INVALID_IP_ADDRESS", "message": "Invalid IP.", "resolution": "Fix it."}')
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

    def test_create_api_error_no_response(self):
        """
        Test that a missing response raises a ClientError
        """
        with self.assertRaises(ClientError):
            DefaultRequestHandler._DefaultRequestHandler__create_api_error(None)


if __name__ == '__main__':
    unittest.main()
