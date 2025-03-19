import json

import aiosqlite
import sqlite3
from .redis_abs import RedisABC


class RedisSqlite(RedisABC):
    def __init__(
            self,
            db_path: str,
            db=0,
            password=None,
    ):
        super().__init__(db_path=db_path, db=db, password=password)

    def connect(self):
        with sqlite3.connect(self.db_path) as db:
            # 创建键值表
            db.execute('''CREATE TABLE IF NOT EXISTS kv (
                            key TEXT PRIMARY KEY, value TEXT
                        )''')
            # 创建列表表
            db.execute('''CREATE TABLE IF NOT EXISTS list (
                            key TEXT, value TEXT, position INTEGER,
                            PRIMARY KEY (key, position)
                        )''')
            db.commit()
        return self

    async def close(self):
        pass

    async def length(self, key: str = None) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            if key:
                cursor = await db.execute('SELECT value FROM kv WHERE key = ?', (key,))
                result = await cursor.fetchone()
                if result:
                    return len(result[0])
                else:
                    cursor = await db.execute('SELECT COUNT(*) FROM list WHERE key = ?', (key,))
                    result = await cursor.fetchone()

                    return result[0] if result else 0
            else:
                cursor = await db.execute('SELECT COUNT(*) FROM kv')
                result = await cursor.fetchone()
                return result

    async def set(self, key: str, value: str | list | dict):
        if isinstance(value, dict) or isinstance(value, list):
            value = json.dumps(value, ensure_ascii=False)
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('INSERT OR REPLACE INTO kv (key, value) VALUES (?, ?)', (key, value))
            await db.commit()

    async def get(self, key: str) -> str | list | None:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(f'SELECT value FROM kv WHERE key = ?', (key,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    if len(row) == 1:
                        try:
                            return json.loads(row[0])
                        except json.JSONDecodeError:
                            return row[0]
                    else:
                        try:
                            return [json.loads(i) for i in row]
                        except json.JSONDecodeError:
                            return list(row)
                return None

    async def lpush(self, key, value):
        async with aiosqlite.connect(self.db_path) as db:
            # 找到当前位置的最小值并减 1，以模拟 "左推" 操作
            async with db.execute('SELECT MIN(position) FROM list WHERE key = ?', (key,)) as cursor:
                row = await cursor.fetchone()
                position = row[0] - 1 if row[0] is not None else 0
            await db.execute('INSERT INTO list (key, value, position) VALUES (?, ?, ?)', (key, value, position))
            await db.commit()

    async def rpush(self, key, value):
        async with aiosqlite.connect(self.db_path) as db:
            # 找到当前位置的最大值并加 1，以模拟 "右推" 操作
            async with db.execute('SELECT MAX(position) FROM list WHERE key = ?', (key,)) as cursor:
                row = await cursor.fetchone()
                position = row[0] + 1 if row[0] is not None else 0
            await db.execute('INSERT INTO list (key, value, position) VALUES (?, ?, ?)', (key, value, position))
            await db.commit()

    async def get_list(self, key) -> list:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute('SELECT value FROM list WHERE key = ?', (key,)) as cursor:
                row = await cursor.fetchall()
                return [i[0] for i in row]

    async def rpop(self, key):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute('SELECT value, MAX(position) FROM list WHERE key = ?', (key,)) as cursor:
                row = await cursor.fetchone()
                if row and row[0] is not None:
                    value = row[0]
                    await db.execute('DELETE FROM list WHERE key = ? AND position = ?', (key, row[1]))
                    await db.commit()
                    return value
                return None

    async def lpop(self, key):
        async with aiosqlite.connect(self.db_path) as db:
            # 查询最小position对应的value
            async with db.execute('SELECT value, MIN(position) FROM list WHERE key = ?', (key,)) as cursor:
                row = await cursor.fetchone()
                if row and row[0] is not None:
                    value = row[0]
                    # 删除该最小position的元素
                    await db.execute('DELETE FROM list WHERE key = ? AND position = ?', (key, row[1]))
                    await db.commit()
                    return value
                return None

    async def delete(self, key: str):
        """
        删除键值对
        :param key:
        :return:
        """
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('DELETE FROM kv WHERE key = ?', (key,))
            await db.commit()

    async def empty(self, key: str):
        """
        清空列表
        :param key:
        :return:
        """
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('DELETE FROM list WHERE key = ?', (key,))
            await db.commit()

    async def exists(self, key):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute('SELECT 1 FROM kv WHERE key = ?', (key,)) as cursor:
                row = await cursor.fetchone()
                return row is not None
