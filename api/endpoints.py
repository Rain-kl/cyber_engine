# api/endpoints.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import List, Optional

router = APIRouter()


class InputModel(BaseModel):
    username: str  # 用户名
    msg: str  # 消息内容


class ResponseModel(BaseModel):
    msg: str  # 消息内容


# 定义API端点


@router.post("/unknown", response_model=ResponseModel)
async def unknown(input_model: InputModel):
    return None
