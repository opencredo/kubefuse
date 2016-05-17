from hamcrest import *
import unittest

from kubefuse.cache import ExpiringCache

class CacheTest(unittest.TestCase):

    def test_cache_get_set(self):
        cache = ExpiringCache(expire_in_seconds = 3600)
        cache.set("key", "value")
        assert_that(cache.get("key"), equal_to("value"))
    
    def test_cache_expired(self):
        cache = ExpiringCache(expire_in_seconds = -10) # expires straight away
        cache.set("key", "value")
        assert_that(cache.get('key'), equal_to(None))

    def test_cache_miss(self):
        cache = ExpiringCache(expire_in_seconds = 10)
        assert_that(cache.get('nonexisting'), equal_to(None))

