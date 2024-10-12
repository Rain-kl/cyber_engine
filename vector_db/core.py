import os

import lancedb
from lancedb.embeddings import OpenAIEmbeddings, SentenceTransformerEmbeddings
from lancedb.pydantic import LanceModel, Vector
from lancedb.table import Table

from config import config

if config.embedding_method == 'openai':
    os.environ["OPENAI_API_KEY"] = config.llm_api_key
    os.environ["OPENAI_BASE_URL"] = config.llm_base_url
    client = OpenAIEmbeddings()
    model = client.create(
        name=config.embedding_model,
    )
elif config.embedding_method == 'sentence_transformers':
    client = SentenceTransformerEmbeddings()
    model = client.create(name=config.embedding_model, device="cpu")


class Words(LanceModel):
    text: str = model.SourceField()
    vector: Vector(model.ndims()) = model.VectorField()


class EmbeddingVectorDB:
    def __init__(self, _table=None):
        # noinspection PyTypeChecker
        self.table: Table = _table

        pass

    def create(self, db_path: str, table_name: str):
        db = lancedb.connect(db_path)

        # noinspection PyTypeChecker
        self.table = db.create_table(table_name, schema=Words, exist_ok=True)
        return self

    def add(self, text: str):
        self.table.add(
            [{"text": text}, ]
        )
        pass

    def search(self, query):
        actual = self.table.search(query).limit(1).to_pandas()
        print(actual)

