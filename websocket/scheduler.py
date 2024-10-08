from datetime import datetime
import asyncio

from redis_ntr import RedisSqlite
from .connection_manager import manager


async def scheduled_broadcast():
    redis = RedisSqlite("./data/scheduler.db")
    await redis.connect()
    while True:
        current_time = datetime.now()
        formatted_time = current_time.strftime('%Y%m%d%H%M')
        result = await redis.get_list(formatted_time)
        if result:
            for msg in result:
                await manager.broadcast(msg)
            await redis.delete(formatted_time)
        await asyncio.sleep(60)
