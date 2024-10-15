# api/api_mnemonic.py
import asyncio

from fastapi import APIRouter
from loguru import logger

from .core import EmbeddingVectorDB
from .model import APIBaseResponseModel, APISearchResponseModel

mn_vdb = EmbeddingVectorDB()
router = APIRouter()


@router.post("/add", response_model=APIBaseResponseModel)
async def mn_add(memory: str, user_id: int):
    def run():
        mn_vdb.create('./data/mnVdb', f"user_{user_id}")
        mn_vdb.add(memory)
        logger.debug(f"Added memory: {memory}")

    await asyncio.to_thread(run)
    return APIBaseResponseModel(status=200, message="Success")


@router.post("/search", response_model=APISearchResponseModel)
async def mn_search(query: str, user_id: int):
    def run():
        mn_vdb.create('./data/mnVdb', f"user_{user_id}")
        return mn_vdb.search(query)

    logger.debug(f"Search query: {query}")
    result = await asyncio.to_thread(run)
    return APISearchResponseModel(
        status=200,
        message="Success",
        data=result
    )
