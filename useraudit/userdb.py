from sqlalchemy import create_engine, Column, Integer, String, Sequence, Text
from sqlalchemy.orm import sessionmaker, declarative_base, Query

try:
    from .ext import __SqliteORM
except ImportError:
    from ext import __SqliteORM

# 创建基类
Base = declarative_base()


# 定义一个User类映射到数据库中的一个表
class User(Base):
    """
    用户表, 用于存储用户ID和标签
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    portrait = Column(String(500))

    def __repr__(self):
        return f"<User(id='{self.id}', portrait='{self.portrait}')>"


class BindID(Base):
    __tablename__ = "bind_id"

    bindID = Column(Integer, primary_key=True)
    id = Column(Integer)
    platform = Column(String(50))

    def __repr__(self):
        return f"<BindID(bindID='{self.bindID}', id='{self.id}', platform='{self.platform}')>"


class UserDB(__SqliteORM):
    def __init__(self, db_path="./data/user.db"):
        super().__init__(db_path)
        self._create_table(Base)


if __name__ == "__main__":
    db = UserDB("./test.db")
    # a = db.query(User).filter(User.id == 1).first()
    # print(a)
