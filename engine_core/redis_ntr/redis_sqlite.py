import aiosqlite

from .redis_abs import RedisABC


class RedisSqlite(RedisABC):
    def __init__(
            self,
            db_path: str,
            db=0,
            password=None,
    ):
        super().__init__(db_path=db_path, db=db, password=password)

    async def connect(self):
        async with aiosqlite.connect(self.db_path) as db:
            # 创建键值表
            await db.execute('''CREATE TABLE IF NOT EXISTS kv (
                            key TEXT PRIMARY KEY, value TEXT
                        )''')
            # 创建列表表
            await db.execute('''CREATE TABLE IF NOT EXISTS list (
                            key TEXT, value TEXT, position INTEGER,
                            PRIMARY KEY (key, position)
                        )''')
            await db.commit()

    async def set(self, key: str, value: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('INSERT OR REPLACE INTO kv (key, value) VALUES (?, ?)', (key, value))
            await db.commit()

    async def get(self, key: str) -> str | None:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(f'SELECT value FROM kv WHERE key = ?', (key,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    return row[0]
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

    async def delete(self, name: str):
        await self.delete(name)

    async def exists(self, key):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute('SELECT 1 FROM kv WHERE key = ?', (key,)) as cursor:
                row = await cursor.fetchone()
                return row is not None
