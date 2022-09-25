from typing import Set

import elasticapm
import aioredis

URI = 'redis://redis.redis.svc'
PORT = 6379
BLACKLIST_KEY = 'blacklist'
WHITELIST_KEY = 'whitelist'


class RedisCache:
    @elasticapm.capture_span()
    def __init__(self, db_id):
        self._r = aioredis.from_url(URI,  db=db_id)

    async def set_urls_for_key(self, key: str, urls: Set[str]):
        await self._r.sadd(key, *list(urls))
        print("Keys saved for key " + key)

    @elasticapm.capture_span()
    async def is_blacklisted(self, url: str):
        res = await self._r.sismember(BLACKLIST_KEY, url)
        return res

    @elasticapm.capture_span()
    async def is_custom_blacklisted(self, customer_id: str, url: str):
        res = await self._r.sismember(customer_id + '-' + BLACKLIST_KEY, url)
        return res

    @elasticapm.capture_span()
    async def is_whitelisted(self, customer_id: str, domain: str):
        res = await self._r.sismember(customer_id + '-' + WHITELIST_KEY, domain)
        return res
