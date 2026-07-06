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

from ipregistry.model import RequesterIpInfo


class TestIpregistryModel(unittest.TestCase):
    def test_requester_ip_info_user_agent_optional(self):
        """
        Test that RequesterIpInfo validates when the user_agent field is
        missing, e.g. when a fields filter excludes it from the response
        """
        info = RequesterIpInfo(ip='8.8.8.8')
        self.assertEqual('8.8.8.8', info.ip)
        self.assertIsNone(info.user_agent)


if __name__ == '__main__':
    unittest.main()
