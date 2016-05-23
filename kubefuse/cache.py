import logging
import time

class ExpiringCache(object):
    def __init__(self, expire_in_seconds):
        self._cache = {}
        self._timestamps = {}
        self.EXPIRE_IN_SECONDS = expire_in_seconds

    def set(self, key, value):
        t = time.time() + self.EXPIRE_IN_SECONDS
        self._cache[key] = value
        self._timestamps[key] = t
        logging.info("Add key '%s' to cache (expires %d)" % (key, t))

    def get(self, key):
        if key not in self._timestamps:
            return None
        now = time.time()
        expires_at = self._timestamps[key]
        if now < expires_at:
            logging.info("Retrieved '%s' from cache" % key)
            return self._cache[key]
        self.delete(key)
        return None

    def delete(self, key):
        del(self._timestamps[key])
        del(self._cache[key])
