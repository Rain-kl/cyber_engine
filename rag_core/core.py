import os
from typing import List

import lancedb
from lancedb.embeddings import OpenAIEmbeddings, SentenceTransformerEmbeddings
from lancedb.pydantic import LanceModel, Vector
from lancedb.table import Table

from config import config
from rag_core.model import SearchResponseModel

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
    def __init__(self):
        # noinspection PyTypeChecker
        self.table: Table = None

    def create(self, db_path: str, table_name: str):
        db = lancedb.connect(db_path)

        # noinspection PyTypeChecker
        self.table = db.create_table(table_name, schema=Words, exist_ok=True)
        return self

    def add(self, text: str):
        self.table.add([{"text": text}, ])

    def search(self, query: str, limit_msg=10) -> List[SearchResponseModel]:
        actual = self.table.search(query).limit(limit_msg).to_df()
        return [SearchResponseModel(
            text=row['text'],
            distance=str(row.get('_distance', 0))  # 使用 get 方法提供默认值0
        ) for index, row in actual.iterrows()]
