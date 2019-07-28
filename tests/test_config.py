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
        requestHandler = DefaultRequestHandler(IpregistryConfig("tryout"))
        print(requestHandler._config)
        self.assertEqual("tryout", requestHandler._config.apiKey)
        self.assertEqual("https://api.ipregistry.co", requestHandler._config.apiUrl)
        self.assertEqual(3, requestHandler._config.timeout)

    def test_config_optional_parameters(self):
        """
        Test that config takes into account optional parameters
        """
        requestHandler = DefaultRequestHandler(IpregistryConfig("MY_API_KEY", "https://custom.acme.com", 10))
        print(requestHandler._config)
        self.assertEqual("MY_API_KEY", requestHandler._config.apiKey)
        self.assertEqual("https://custom.acme.com", requestHandler._config.apiUrl)
        self.assertEqual(10, requestHandler._config.timeout)

if __name__ == '__main__':
    unittest.main()
