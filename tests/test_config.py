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

from ipregistry.core import IpregistryConfig
from ipregistry.request import DefaultRequestHandler


class TestIpregistryConfig(unittest.TestCase):
    def test_default_config(self):
        """
        Test that default config use right parameters
        """
        request_handler = DefaultRequestHandler(IpregistryConfig("tryout"))
        print(request_handler._config)
        self.assertEqual("tryout", request_handler._config.api_key)
        self.assertEqual("https://api.ipregistry.co", request_handler._config.base_url)
        self.assertEqual(5, request_handler._config.timeout)

    def test_config_optional_parameters(self):
        """
        Test that config takes into account optional parameters
        """
        request_handler = DefaultRequestHandler(IpregistryConfig("MY_API_KEY", "https://custom.acme.com", 10))
        print(request_handler._config)
        self.assertEqual("MY_API_KEY", request_handler._config.api_key)
        self.assertEqual("https://custom.acme.com", request_handler._config.base_url)
        self.assertEqual(10, request_handler._config.timeout)


if __name__ == '__main__':
    unittest.main()
