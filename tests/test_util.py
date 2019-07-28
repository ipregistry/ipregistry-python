import unittest

from ipregistry.cache import DefaultCache, NoCache
from ipregistry.util import UserAgent

class TestIpregistryUserAgent(unittest.TestCase):
    def test_isbot_chrome(self):
        """
        Test that isBot is False with standard Chrome User-Agent
        """
        self.assertEqual(False, UserAgent.isBot("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"))

    def test_isbot_chrome(self):
        """
        Test that isBot is True with Googlebot UserAgent
        """
        self.assertEqual(True, UserAgent.isBot("Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"))


if __name__ == '__main__':
    unittest.main()
