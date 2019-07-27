import unittest

from ipregistry.cache import DefaultCache, NoCache

class TestIpregistryCache(unittest.TestCase):
    def test_defaultcache_get(self):
        """
        Test that get returns cache value
        """
        cache = DefaultCache()
        self.assertEqual(None, cache.get("a"))
        cache.put("a", 1)
        self.assertEqual(1, cache.get("a"))

    def test_defaultcache_put_override(self):
        """
        Test that put override previous value
        """
        cache = DefaultCache()
        cache.put("a", 1)
        cache.put("a", 2)
        self.assertEqual(2, cache.get("a"))

    def test_defaultcache_invalidate(self):
        """
        Test that invalidate remove correct entries
        """
        cache = DefaultCache()
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
        cache = DefaultCache()
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
