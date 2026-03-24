import logging
import json
from typing import Any
from redis import Redis, RedisError
from app.config import Settings
from urllib.parse import urlparse


logger = logging.getLogger(__name__)
settings = Settings()

class CacheService:
    def __init__(self):
        self.client = Redis.from_url(
            settings.redis_url,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
        )
        self.default_ttl = 300 

    def get(self, key: str)-> Any | None:
        try:
            value = self.client.get(key)
            if value is None:
                return None
            return json.loads(value)
        except RedisError as e:
            logger.warning(f"[Cache] GET failed for key '{key}': {e}")
            return None
        
    def set(self, key: str, value: Any, ttl: int | None = None) -> bool:
        """
        Store a value in cache with an optional TTL (seconds).
        Falls back to default_ttl if not specified.
        Returns True on success, False on failure.
        """
        try:
            serialised = json.dumps(value, default=str)
            self.client.setex(
                name=key,
                time=ttl or self.default_ttl,
                value=serialised,
            )
            return True
        except RedisError as e:
            logger.warning(f"[Cache] SET failed for key '{key}': {e}")
            return False
        
    def delete(self, key: str) -> bool:
        """Delete a single key. Returns True if deleted, False if not found."""
        try:
            result = self.client.delete(key)
            return result > 0
        except RedisError as e:
            logger.warning(f"[Cache] DELETE failed for key '{key}': {e}")
            return False
 
    def exists(self, key: str) -> bool:
        """Check if a key exists in cache."""
        try:
            return self.client.exists(key) > 0
        except RedisError:
            return False
 
    def ttl(self, key: str) -> int:
        """Return remaining TTL in seconds. -1 = no expiry, -2 = not found."""
        try:
            return self.client.ttl(key)
        except RedisError:
            return -2
        
    # ------------------------------------------------------------------
    # BULK OPERATIONS
    # ------------------------------------------------------------------
 
    def invalidate_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching a pattern (e.g. "user:*").
        Returns the number of keys deleted.
 
        ⚠️  Uses SCAN not KEYS — safe for production/large datasets.
        """
        try:
            deleted = 0
            cursor = 0
            while True:
                cursor, keys = self.client.scan(cursor=cursor, match=pattern, count=100)
                if keys:
                    deleted += self.client.delete(*keys)
                if cursor == 0:
                    break
            logger.info(f"[Cache] Invalidated {deleted} keys matching '{pattern}'")
            return deleted
        except RedisError as e:
            logger.warning(f"[Cache] INVALIDATE failed for pattern '{pattern}': {e}")
            return 0
 
    def flush_all(self) -> bool:
        """Clear the entire cache DB. Use with caution."""
        try:
            self.client.flushdb()
            return True
        except RedisError as e:
            logger.warning(f"[Cache] FLUSH failed: {e}")
            return False
