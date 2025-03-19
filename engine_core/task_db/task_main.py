import json
import sqlite3
import time

from models import TaskModel


class TaskCenter:
    def __init__(self):
        self.db_path = './data/task_center.db'

    def init(self):
        try:
            with sqlite3.connect(self.db_path) as db:
                # 创建键值表
                db.execute('''CREATE TABLE IF NOT EXISTS tasks (
                                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                                user_id text,
                                data text,
                                status INT,
                                created TEXT
                            )''')
                db.commit()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")

    def add_task(self, model: TaskModel):
        self.init()
        user_id = model.user_id
        data = model.data
        status = 0
        created = int(time.time())

        try:
            with sqlite3.connect(self.db_path) as db:
                db.execute(
                    'INSERT INTO tasks (user_id, data, status, created) VALUES (?, ?, ?, ?)',
                    (user_id, data, status, created)
                )
                db.commit()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")

    def get_task(self, user_id: str):
        """
        获取用户最新的任务
        """
        self.init()
        current_time = int(time.time())
        expiration_time = 30 * 60  # 30分钟过期时间（秒）

        with sqlite3.connect(self.db_path) as db:
            # 查询用户最新的任务
            cursor = db.execute(
                'SELECT id, user_id, data, status, created FROM tasks WHERE user_id = ? ORDER BY created DESC LIMIT 1',
                (user_id,)
            )
            task = cursor.fetchone()

            if not task:
                raise ValueError(f"未找到用户 {user_id} 的任务")

            task_id, task_user_id, data, status, created = task
            created = int(created)

            # 返回批准的任务信息
            return TaskModel(
                user_id=task_user_id,
                data=data,
                status=status,
                created=created
            )

    def approve_task(self, user_id: str) -> TaskModel:
        """
        批准用户最新的任务
        :param user_id: 用户ID
        :return: 批准的任务信息，如果没有找到任务或任务已过期返回None
        """
        self.init()
        current_time = int(time.time())
        expiration_time = 30 * 60  # 30分钟过期时间（秒）

        with sqlite3.connect(self.db_path) as db:
            # 查询用户最新的任务
            cursor = db.execute(
                'SELECT id, user_id, data, status, created FROM tasks WHERE user_id = ? ORDER BY created DESC LIMIT 1',
                (user_id,)
            )
            task = cursor.fetchone()

            if not task:
                raise ValueError(f"未找到用户 {user_id} 的任务")

            task_id, task_user_id, data, status, created = task
            created = int(created)

            # 检查任务是否已过期
            if current_time - created > expiration_time:
                raise ValueError(f"任务已过期。任务ID: {task_id}")

            if status != 0:
                raise ValueError(f"任务已执行，无需重复批准。任务ID: {task_id}")

            # 更新任务状态为已批准(1)
            db.execute('UPDATE tasks SET status = 1 WHERE id = ?', (task_id,))
            db.commit()

            # 返回批准的任务信息
            return TaskModel(
                user_id=task_user_id,
                data=data,
                status=1,
                created=created
            )


task_center = TaskCenter()
