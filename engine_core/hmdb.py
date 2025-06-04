import sqlite3
import json
import aiosqlite
from datetime import datetime


class HMDB:
    """历史消息数据库，用于存储超出最大对话轮的消息"""

    def __init__(self, user_id):
        self.db_path = "./data/hmdb.db"
        self.user_id = user_id
        self.is_connected = False

    async def connect(self):
        """连接到数据库并创建必要的表"""
        if not self.is_connected:
            # 使用同步方式创建表结构
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                )"""
                )
                conn.commit()
            self.is_connected = True
        return self

    async def add_message(self, role, content):
        """添加消息到历史数据库

        Args:
            role: 消息的角色（user或assistant）
            content: 消息内容
        """
        current_time = datetime.now().isoformat()
        # 将role和content合并为JSON格式
        message_content = json.dumps(
            {"role": role, "content": content}, ensure_ascii=False
        )

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO messages (user_id, content, timestamp) VALUES (?, ?, ?)",
                (self.user_id, message_content, current_time),
            )
            await db.commit()

    async def get_messages(self, limit=None, offset=0):
        """获取历史消息，检索全部用户ID的消息并按时间排序

        Args:
            limit: 限制返回的消息数量，None表示不限制
            offset: 起始位置的偏移量

        Returns:
            包含消息的列表，每条消息为dict格式
        """
        async with aiosqlite.connect(self.db_path) as db:
            if limit is not None:
                query = """
                    SELECT user_id, content, timestamp 
                    FROM messages 
                    ORDER BY timestamp DESC
                    LIMIT ? OFFSET ?
                """
                async with db.execute(query, (limit, offset)) as cursor:
                    rows = await cursor.fetchall()
            else:
                query = """
                    SELECT user_id, content, timestamp 
                    FROM messages 
                    ORDER BY timestamp DESC
                    OFFSET ?
                """
                async with db.execute(query, (offset,)) as cursor:
                    rows = await cursor.fetchall()

            messages = []
            for row in rows:
                user_id = row[0]
                # 解析JSON格式的content
                content_obj = json.loads(row[1])
                message = {
                    "user_id": user_id,
                    "role": content_obj["role"],
                    "content": content_obj["content"],
                    "timestamp": row[2],
                }
                messages.append(message)
            return messages

    async def get_messages_by_user(self, user_id=None, limit=None, offset=0):
        """获取特定用户的历史消息

        Args:
            user_id: 用户ID，默认为当前用户
            limit: 限制返回的消息数量，None表示不限制
            offset: 起始位置的偏移量

        Returns:
            包含消息的列表，每条消息为dict格式
        """
        user_id = user_id or self.user_id

        async with aiosqlite.connect(self.db_path) as db:
            if limit is not None:
                query = """
                    SELECT content, timestamp 
                    FROM messages 
                    WHERE user_id = ?
                    ORDER BY timestamp 
                    LIMIT ? OFFSET ?
                """
                async with db.execute(query, (user_id, limit, offset)) as cursor:
                    rows = await cursor.fetchall()
            else:
                query = """
                    SELECT content, timestamp 
                    FROM messages 
                    WHERE user_id = ?
                    ORDER BY timestamp
                    OFFSET ?
                """
                async with db.execute(query, (user_id, offset)) as cursor:
                    rows = await cursor.fetchall()

            messages = []
            for row in rows:
                # 解析JSON格式的content
                content_obj = json.loads(row[0])
                message = {
                    "user_id": user_id,
                    "role": content_obj["role"],
                    "content": content_obj["content"],
                    "timestamp": row[1],
                }
                messages.append(message)
            return messages

    async def get_message_count(self, user_id=None):
        """获取用户历史消息的总数

        Args:
            user_id: 用户ID，默认为当前用户，None表示所有用户
        """
        async with aiosqlite.connect(self.db_path) as db:
            if user_id:
                query = "SELECT COUNT(*) FROM messages WHERE user_id = ?"
                async with db.execute(query, (user_id,)) as cursor:
                    row = await cursor.fetchone()
            else:
                query = "SELECT COUNT(*) FROM messages"
                async with db.execute(query) as cursor:
                    row = await cursor.fetchone()
            return row[0] if row else 0

    async def delete_messages(self, user_id=None, before_date=None):
        """删除消息

        Args:
            user_id: 用户ID，默认为当前用户，None表示所有用户
            before_date: 删除此日期之前的所有消息，None表示删除所有消息
        """
        async with aiosqlite.connect(self.db_path) as db:
            if user_id and before_date:
                query = "DELETE FROM messages WHERE user_id = ? AND timestamp < ?"
                await db.execute(query, (user_id, before_date.isoformat()))
            elif user_id:
                query = "DELETE FROM messages WHERE user_id = ?"
                await db.execute(query, (user_id,))
            elif before_date:
                query = "DELETE FROM messages WHERE timestamp < ?"
                await db.execute(query, (before_date.isoformat(),))
            else:
                # 删除所有消息
                query = "DELETE FROM messages"
                await db.execute(query)
            await db.commit()


def connect_hmdb(user_id) -> HMDB:
    """创建并连接到HMDB实例"""
    return HMDB(user_id)
