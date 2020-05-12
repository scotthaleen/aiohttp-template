import asyncio
import logging
from logging import Logger
from typing import Any, List, Optional, TypedDict

import aioredis

from . import utils

logger: Logger = logging.getLogger(__name__)


class PriorityItem(TypedDict):
    item: str
    priority: int

Q_PREFIX = "system:app:q:"
Q_PREFIX_F = "system:app:q:{name}"

async def connect(host, port) -> aioredis.Redis:
    pool = await aioredis.create_pool((host, port), encoding="utf-8")
    return aioredis.Redis(pool)

async def get_q_size(redis: aioredis.Redis, name: str) -> int:
    """ Get Size of a Queue"""
    count = await redis.zcard(Q_PREFIX_F.format(name=name))
    return count

async def get_q_pop(redis: aioredis.Redis, name: str) -> str:
    """Get lowest priority of a sorted set"""
    result = await redis.zpopmin(Q_PREFIX_F.format(name=name), count=1, encoding="utf-8")
    return next(iter(result), None)

async def get_all_qs(redis: aioredis.Redis) -> List[dict]:
    """List all queue names"""
    qs = await redis.keys(f"{Q_PREFIX}*", encoding="utf-8")
    return {q.replace(Q_PREFIX, ""): await redis.zcard(q) for q in qs}

async def q_add(redis: aioredis.Redis, name: str, item: str, priority=10) -> None:
    """Add to a prioirty queue"""
    q = Q_PREFIX_F.format(name=name)
    await redis.zadd(q, priority, item, incr=True)
    return None

async def q_add_many(
    redis: aioredis.Redis, name: str, items: List[PriorityItem]
) -> int:
    """
    Returns count of items added
    """
    q = Q_PREFIX_F.format(name=name)
    return sum(
        await asyncio.gather(
            *[redis.zadd(q, item["priority"], item["item"]) for item in items]
        )
    )

