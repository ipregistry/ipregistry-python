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

from ipregistry.util import UserAgents


class TestIpregistryUserAgent(unittest.TestCase):
    def test_isbot_chrome_false(self):
        """
        Test that isBot is False with standard Chrome User-Agent
        """
        self.assertEqual(False, UserAgents.is_bot("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ("
                                                  "KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"))

    def test_isbot_chrome_true(self):
        """
        Test that isBot is True with Googlebot UserAgent
        """
        self.assertEqual(True, UserAgents.is_bot("Mozilla/5.0 (compatible; Googlebot/2.1; "
                                                 "+http://www.google.com/bot.html)"))


if __name__ == '__main__':
    unittest.main()
