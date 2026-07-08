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

from ipregistry.json import Connection, Currency, CurrencyFormat, IpInfo, UserAgent
from ipregistry.model import ApiError, ErrorCode, IpregistryLookupError, LookupError, RequesterIpInfo


class TestIpregistryModel(unittest.TestCase):
    def test_connection_fields_optional(self):
        """
        Test that Connection validates when fields are missing,
        e.g. when a fields filter excludes them from the response
        """
        connection = Connection()
        self.assertIsNone(connection.asn)
        self.assertIsNone(connection.domain)

        info = IpInfo(ip='8.8.8.8', connection={'asn': 15169})
        self.assertEqual(15169, info.connection.asn)

    def test_currency_format_fields_optional(self):
        """
        Test that CurrencyFormat validates when negative/positive are missing
        """
        currency_format = CurrencyFormat()
        self.assertIsNone(currency_format.negative)
        self.assertIsNone(currency_format.positive)

        currency = Currency(code='USD', format={})
        self.assertEqual('USD', currency.code)

    def test_user_agent_fields_optional(self):
        """
        Test that UserAgent validates when device, engine or os are missing
        """
        user_agent = UserAgent(name='Chrome')
        self.assertEqual('Chrome', user_agent.name)
        self.assertIsNone(user_agent.device)
        self.assertIsNone(user_agent.engine)
        self.assertIsNone(user_agent.os)

    def test_requester_ip_info_user_agent_optional(self):
        """
        Test that RequesterIpInfo validates when the user_agent field is
        missing, e.g. when a fields filter excludes it from the response
        """
        info = RequesterIpInfo(ip='8.8.8.8')
        self.assertEqual('8.8.8.8', info.ip)
        self.assertIsNone(info.user_agent)


    def test_api_error_str(self):
        """
        Test that str(ApiError) returns the error message
        """
        error = ApiError('INVALID_IP_ADDRESS', 'The IP address is invalid.', 'Check the input.')
        self.assertEqual('The IP address is invalid.', str(error))

    def test_api_error_typed_error_code(self):
        """
        Test that ApiError exposes a typed error code alongside the raw string
        """
        error = ApiError('INVALID_IP_ADDRESS', 'The IP address is invalid.', 'Check the input.')
        self.assertEqual(ErrorCode.INVALID_IP_ADDRESS, error.error_code)
        self.assertEqual('INVALID_IP_ADDRESS', error.code)

    def test_api_error_unknown_error_code(self):
        """
        Test that an unrecognized raw code yields no typed error code
        """
        error = ApiError('SOME_FUTURE_CODE', 'New error.', None)
        self.assertIsNone(error.error_code)
        self.assertEqual('SOME_FUTURE_CODE', error.code)

    def test_error_code_from_code(self):
        """
        Test raw to typed error code conversion
        """
        self.assertEqual(ErrorCode.TOO_MANY_REQUESTS, ErrorCode.from_code('TOO_MANY_REQUESTS'))
        self.assertIsNone(ErrorCode.from_code('NOT_A_CODE'))
        self.assertIsNone(ErrorCode.from_code(None))

    def test_lookup_error_str(self):
        """
        Test that str(IpregistryLookupError) returns the error message
        """
        error = IpregistryLookupError({'code': 'INVALID_ASN', 'message': 'The ASN is invalid.'})
        self.assertEqual('The ASN is invalid.', str(error))
        self.assertEqual('INVALID_ASN', error.code)

    def test_lookup_error_backward_compatible_alias(self):
        """
        Test that the legacy LookupError name remains usable as an alias
        """
        self.assertIs(LookupError, IpregistryLookupError)


if __name__ == '__main__':
    unittest.main()
