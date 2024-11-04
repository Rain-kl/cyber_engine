from sqlalchemy import create_engine, Column, Integer, String, Sequence, Text
from sqlalchemy.orm import sessionmaker, declarative_base, Query

# 创建基类
Base = declarative_base()


# 定义一个User类映射到数据库中的一个表
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    user = Column(String(50))
    msg = Column(Text)
    time = Column(String(50))

    def __repr__(self):
        return f"<User(user='{self.user}', msg='{self.msg}', time='{self.time}')>"


class __SqliteORM:
    def __init__(self, db_path="./test.db"):
        self.engine = create_engine(f'sqlite:///{db_path}')
        self.session = sessionmaker(bind=self.engine)()

    def _create_table(self, base):
        base.metadata.create_all(self.engine)

    def insert(self, base):
        self.session.add(base)
        self.session.commit()

    def query(self, base) -> Query:
        return self.session.query(base)


class HistoricalMsgDB(__SqliteORM):
    def __init__(self, db_path="./data/historical.db"):
        super().__init__(db_path)
        self._create_table(Base)


if __name__ == '__main__':
    db = HistoricalMsgDB()
    a = db.query(User).filter(User.id == 1).first()
    print(a)
