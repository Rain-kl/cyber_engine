from .QopAgent.qop_agent import QopProcess
from .RouterAgent import RouterAgent
import time
from loguru import logger

# from llama_index.postprocessor.flag_embedding_reranker import (
#     FlagEmbeddingReranker,
# )
#
# start_time = time.time()
# reranker = FlagEmbeddingReranker(
#     top_n=3,
#     model="./data/bge-reranker-v2-m3",
#     use_fp16=False
# )
# logger.success(f"Reranker model loading complete. spend: {time.time() - start_time}")

__all__ = ["QopProcess", "RouterAgent"]
