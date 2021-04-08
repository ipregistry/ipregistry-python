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

from ipregistry.cache import InMemoryCache, NoCache

class TestIpregistryCache(unittest.TestCase):
    def test_defaultcache_get(self):
        """
        Test that get returns cache value
        """
        cache = InMemoryCache()
        self.assertEqual(None, cache.get("a"))
        cache.put("a", 1)
        self.assertEqual(1, cache.get("a"))

    def test_defaultcache_put_override(self):
        """
        Test that put override previous value
        """
        cache = InMemoryCache()
        cache.put("a", 1)
        cache.put("a", 2)
        self.assertEqual(2, cache.get("a"))

    def test_defaultcache_invalidate(self):
        """
        Test that invalidate remove correct entries
        """
        cache = InMemoryCache()
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)
        cache.invalidate("b")
        self.assertEqual(1, cache.get("a"))
        self.assertEqual(None, cache.get("b"))
        self.assertEqual(3, cache.get("c"))

    def test_defaultcache_invalidateAll(self):
        """
        Test that invalidateAll remove all entries
        """
        cache = InMemoryCache()
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)
        cache.invalidateAll()
        self.assertEqual(None, cache.get("a"))
        self.assertEqual(None, cache.get("b"))
        self.assertEqual(None, cache.get("c"))

    def test_nocache_get(self):
        """
        Test that get always returns None with NoCache implementation
        """
        cache = NoCache()
        self.assertEqual(None, cache.get("a"))
        cache.put("a", 1)
        self.assertEqual(None, cache.get("a"))

if __name__ == '__main__':
    unittest.main()
