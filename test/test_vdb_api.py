import time

import pytest

from engine_core.vdb_api import Mnemonic


class TestVDB:
    """测试RedisSqlite类的异步方法"""

    @pytest.mark.asyncio
    async def add(self):
        start = time.time()
        mn = Mnemonic()
        await mn.add("hello", user_id=10001)
        print(f"Time taken: {time.time() - start}")
