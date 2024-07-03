import sys
import time
from typing import Dict, Generic, Optional, TypeVar

DEFAULT_CACHE_SIZE = 10 * 1024  # 10KB
DEFAULT_CACHE_TTL = 5  # 5 seconds

T = TypeVar("T")


class CacheProvider(Generic[T]):
    def get(self, key: str) -> Optional[T]:
        pass

    def set(self, key: str, val: T, ttl_override: Optional[int] = None) -> None:
        pass


class CachedItem(Generic[T]):
    def __init__(self, value: T, access_counter: int, size: int, expiration: float):
        self.value = value
        self.access_counter = access_counter
        self.size = size
        self.expiration = expiration


class LocalCache(CacheProvider[T]):
    def __init__(self, max_size: int, ttl: int):
        self.cache: Dict[str, CachedItem[T]] = {}
        self.max_size = max_size
        self.current_size = 0
        self.access_counter = 0
        self.ttl = ttl

    def get(self, key: str) -> Optional[T]:
        if self.max_size == 0:
            return None

        item = self.cache.get(key)
        if item is None:
            return None

        # Check if the item has expired
        if time.time() > item.expiration:
            self.current_size -= item.size
            del self.cache[key]
            return None

        # Update the access counter for LRU eviction
        self.access_counter += 1
        item.access_counter = self.access_counter
        self.cache[key] = item

        return item.value

    def set(self, key: str, val: T, ttl_override: Optional[int] = None) -> None:
        if self.max_size == 0:
            return

        ttl = self.ttl if ttl_override is None else ttl_override
        size = sys.getsizeof(val)

        # Check if the key already exists in the cache
        if key in self.cache:
            item = self.cache[key]
            self.current_size -= item.size
            self.current_size += size
            self.access_counter += 1
            self.cache[key] = CachedItem(val, self.access_counter, size, time.time() + ttl)
            return

        # Evict expired items
        for k, item in list(self.cache.items()):
            if time.time() > item.expiration:
                self.current_size -= item.size
                del self.cache[k]

        # Evict records if the cache size exceeds the max size
        while self.current_size + size > self.max_size:
            oldest_key = None
            oldest_access_counter = float("inf")

            for k, v in self.cache.items():
                if v.access_counter < oldest_access_counter:
                    oldest_key = k
                    oldest_access_counter = v.access_counter

            if oldest_key is not None:
                self.current_size -= self.cache[oldest_key].size
                del self.cache[oldest_key]
            else:
                break

        # Add the new item to the cache
        self.access_counter += 1
        self.cache[key] = CachedItem(val, self.access_counter, size, time.time() + ttl)
        self.current_size += size
