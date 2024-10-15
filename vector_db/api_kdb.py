# api/api_kdb.py

from fastapi import APIRouter, File, UploadFile

from .core import EmbeddingVectorDB
from .model import APIBaseResponseModel, APISearchResponseModel

kb_vdb = EmbeddingVectorDB()
router = APIRouter()


@router.post("/addfile", response_model=APIBaseResponseModel)
async def kdb_add_file(file: UploadFile = File(...)):
    pass


@router.post("/search", response_model=APISearchResponseModel)
async def kdb_search(query: str, user_id: int):
    pass
