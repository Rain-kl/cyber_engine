from sqlalchemy import create_engine, Column, Integer, String, Sequence, Text
from sqlalchemy.orm import sessionmaker, declarative_base, Query


class __SqliteORM:
    def __init__(self, db_path="./test.db"):
        self.engine = create_engine(f"sqlite:///{db_path}")
        self.session = sessionmaker(bind=self.engine)()

    def _create_table(self, base):
        base.metadata.create_all(self.engine)

    def insert(self, base):
        self.session.add(base)
        self.session.commit()

    def query(self, base) -> Query:
        return self.session.query(base)
