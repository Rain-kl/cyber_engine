import sqlite3
from pydantic import BaseModel
from typing import Literal


class EventLogModel(BaseModel):
    """
    事件日志模型, 用于记录用户的操作日志
    """

    user_id: int
    type: Literal["msg", "func"]
    level: int
    message: str

    class LEVEL:
        INFO = 0
        WARNING = 1
        ERROR = 2


class EventLog:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def init(self):
        try:
            with sqlite3.connect(self.db_path) as db:
                # 创建键值表
                db.execute(
                    """CREATE TABLE IF NOT EXISTS event (
                                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                                user_id INT,
                                type TEXT,
                                level INT,
                                message TEXT,
                                time TEXT
                            )"""
                )
                db.commit()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")

    def log(self, model: EventLogModel):
        self.init()
        user_id = model.user_id
        type_ = model.type
        level = model.level
        message = model.message

        try:
            with sqlite3.connect(self.db_path) as db:
                db.execute(
                    'INSERT INTO event (user_id, type, level, message, time) VALUES (?, ?, ?, ?, datetime("now"))',
                    (user_id, type_, level, message),
                )
                db.commit()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")


elogger = EventLog(db_path="./data/event_log.db")
