import json
from datetime import datetime
import asyncio
from loguru import logger

from model import TaskModel, InputModel, ResponseModel
from redis_mq import RedisSqlite
from .ws_clients import websocket_list
from .connection_manager import manager
from engine_core import ponder


async def scheduled_broadcast():
    redis = RedisSqlite("./data/scheduler.db")
    while True:
        await redis.connect()
        current_time = datetime.now()
        formatted_time = current_time.strftime('%Y%m%d%H%M')
        result = await redis.get_list(formatted_time)
        if result:
            for msg in result:
                logger.info(f"Schedule task: {msg}")
                task_model = TaskModel(**json.loads(msg))
                input_ = InputModel(
                    role="auxiliary",
                    user_id=task_model.user_id,
                    channel=task_model.channel,
                    msg=f"用户在某个时间点设置的任务: 【{task_model.origin}】，现在已经到了时间点了，请执行相关操作"
                )
                pond_msg = await ponder(input_)
                response_data = ResponseModel(
                    user_id=task_model.user_id,
                    msg=str(pond_msg)
                )
                await manager.send_private_msg(response_data, websocket_list[task_model.channel])

            await redis.empty(formatted_time)
        await asyncio.sleep(5)
