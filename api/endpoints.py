# api/endpoints.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import List, Optional

from model import ResponseModel, InputModel

router = APIRouter()


# 定义API端点


@router.post("/unknown", response_model=ResponseModel)
async def unknown(input_model: InputModel):
    return None
