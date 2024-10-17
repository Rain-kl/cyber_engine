import sqlite3

from redis_mq.redis_abs import RedisABC


class RedisSqliteSync(RedisABC):
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

    def close(self):
        pass  # Placeholder, as we're using context management for connections

    def length(self, key: str = None) -> int:
        with sqlite3.connect(self.db_path) as db:
            cursor = db.cursor()
            if key:
                cursor.execute('SELECT value FROM kv WHERE key = ?', (key,))
                result = cursor.fetchone()
                if result:
                    return len(result[0])
                else:
                    cursor.execute('SELECT COUNT(*) FROM list WHERE key = ?', (key,))
                    result = cursor.fetchone()
                    return result[0] if result else 0
            else:
                cursor.execute('SELECT COUNT(*) FROM kv')
                result = cursor.fetchone()
                return result[0]

    def set(self, key: str, value: str):
        with sqlite3.connect(self.db_path) as db:
            db.execute('INSERT OR REPLACE INTO kv (key, value) VALUES (?, ?)', (key, value))
            db.commit()

    def get(self, key: str):
        with sqlite3.connect(self.db_path) as db:
            cursor = db.execute('SELECT value FROM kv WHERE key = ?', (key,))
            row = cursor.fetchone()
            if row:
                if len(row) == 1:
                    return row[0]
                else:
                    return list(row)
            return None

    def lpush(self, key, value):
        with sqlite3.connect(self.db_path) as db:
            cursor = db.execute('SELECT MIN(position) FROM list WHERE key = ?', (key,))
            row = cursor.fetchone()
            position = row[0] - 1 if row[0] is not None else 0
            db.execute('INSERT INTO list (key, value, position) VALUES (?, ?, ?)', (key, value, position))
            db.commit()

    def rpush(self, key, value):
        with sqlite3.connect(self.db_path) as db:
            cursor = db.execute('SELECT MAX(position) FROM list WHERE key = ?', (key,))
            row = cursor.fetchone()
            position = row[0] + 1 if row[0] is not None else 0
            db.execute('INSERT INTO list (key, value, position) VALUES (?, ?, ?)', (key, value, position))
            db.commit()

    def get_list(self, key) -> list:
        with sqlite3.connect(self.db_path) as db:
            cursor = db.execute('SELECT value FROM list WHERE key = ?', (key,))
            rows = cursor.fetchall()
            return [i[0] for i in rows]

    def rpop(self, key):
        with sqlite3.connect(self.db_path) as db:
            cursor = db.execute('SELECT value, MAX(position) FROM list WHERE key = ?', (key,))
            row = cursor.fetchone()
            if row and row[0] is not None:
                value = row[0]
                db.execute('DELETE FROM list WHERE key = ? AND position = ?', (key, row[1]))
                db.commit()
                return value
            return None

    def lpop(self, key):
        with sqlite3.connect(self.db_path) as db:
            cursor = db.execute('SELECT value, MIN(position) FROM list WHERE key = ?', (key,))
            row = cursor.fetchone()
            if row and row[0] is not None:
                value = row[0]
                db.execute('DELETE FROM list WHERE key = ? AND position = ?', (key, row[1]))
                db.commit()
                return value
            return None

    def delete(self, key: str):
        with sqlite3.connect(self.db_path) as db:
            db.execute('DELETE FROM kv WHERE key = ?', (key,))
            db.commit()

    def empty(self, key: str):
        with sqlite3.connect(self.db_path) as db:
            db.execute('DELETE FROM list WHERE key = ?', (key,))
            db.commit()

    def exists(self, key):
        with sqlite3.connect(self.db_path) as db:
            cursor = db.execute('SELECT 1 FROM kv WHERE key = ?', (key,))
            row = cursor.fetchone()
            return row is not None
