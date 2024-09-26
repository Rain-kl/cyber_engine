import asyncio

from engine_core.redis_ntr.redis_sqlite import RedisSqlite

async def mqt():
    redis=RedisSqlite('./data/mq.db')
    await redis.connect()
    await redis.set("a","bhs")
    rsp=await redis.get("a")
    print(rsp)
    await redis.rpush('q','a')
    await redis.rpush('q','b')
    rsp=await redis.rpop('q')
    print(rsp)
    rsp=await redis.rpop('q')
    print(rsp)

if __name__ == '__main__':
    asyncio.run(mqt())