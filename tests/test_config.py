import unittest

from ipregistry import ipregistry
from ipregistry import request

class TestIpregistryConfig(unittest.TestCase):
    def test_default_config(self):
        """
        Test that default config use right parameters.
        """
        requestHandler = request.DefaultRequestHandler(ipregistry.IpregistryConfig("tryout"))
        print(requestHandler._config)
        self.assertEqual("tryout", requestHandler._config.apiKey)
        self.assertEqual("https://api.ipregistry.co", requestHandler._config.apiUrl)
        self.assertEqual(3, requestHandler._config.timeout)

    def test_config_optional_parameters(self):
        """
        Test that config takes into account optional parameters.
        """
        requestHandler = request.DefaultRequestHandler(ipregistry.IpregistryConfig("MY_API_KEY", "https://custom.acme.com", 10))
        print(requestHandler._config)
        self.assertEqual("MY_API_KEY", requestHandler._config.apiKey)
        self.assertEqual("https://custom.acme.com", requestHandler._config.apiUrl)
        self.assertEqual(10, requestHandler._config.timeout)

if __name__ == '__main__':
    unittest.main()
