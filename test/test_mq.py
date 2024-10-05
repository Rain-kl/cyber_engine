import pytest
from redis_ntr import RedisSqlite  # 假设你的代码在your_module.py中


class TestRedisSqlite:
    """测试RedisSqlite类的异步方法"""

    @pytest.mark.asyncio
    async def test_connection(self):
        """测试数据库连接"""
        # 创建 RedisSqlite 实例，并连接到测试数据库
        redis = RedisSqlite('../data/test_mq.db')
        await redis.connect()
        # 连接后应该能正常执行期望行为，例如检查默认数据库或版本信息等
        # 假设连接后可以获取一些状态信息，这是一个简单的连接性测试
        await redis.close()  # 确保测试结束后关闭连接

    @pytest.mark.asyncio
    async def test_set_and_get(self):
        """测试set和get功能"""
        redis = RedisSqlite('../data/test_mq.db')
        await redis.connect()
        await redis.set("a", "bhs")
        value = await redis.get("a")
        assert value == "bhs"
        await redis.close()

    @pytest.mark.asyncio
    async def test_append(self):
        """测试set和get功能"""
        redis = RedisSqlite('../data/test_mq.db')
        await redis.connect()
        await redis.empty("a")
        await redis.rpush("a", "bhs")
        await redis.rpush("a", "ash")
        value = await redis.get_list("a")
        assert value == ["bhs", "ash"]
        await redis.empty("a")



    @pytest.mark.asyncio
    async def test_stack_operations(self):
        """测试队列操作"""
        redis = RedisSqlite('../data/test_mq.db')
        await redis.connect()
        await redis.rpush('q', 'a')
        await redis.rpush('q', 'b')

        # 检查弹出操作
        rsp = await redis.rpop('q')
        assert rsp == 'b'

        # 检查队列长度
        length = await redis.length("q")
        assert length == 1

        # 再次弹出操作
        rsp = await redis.rpop('q')
        assert rsp == 'a'

        # 再次检查队列长度
        length = await redis.length("q")
        assert length == 0

        await redis.close()

    @pytest.mark.asyncio
    async def test_queue_operations(self):
        """测试队列操作"""
        redis = RedisSqlite('../data/test_mq.db')
        await redis.connect()
        await redis.rpush('q', 'a')
        await redis.rpush('q', 'b')

        # 检查弹出操作
        rsp = await redis.lpop('q')
        assert rsp == 'a'

        # 检查队列长度
        length = await redis.length("q")
        assert length == 1

        # 再次弹出操作
        rsp = await redis.lpop('q')
        assert rsp == 'b'

        # 再次检查队列长度
        length = await redis.length("q")
        assert length == 0

        await redis.close()
