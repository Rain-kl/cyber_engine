import asyncio

from engine_core import ponder
from redis_mq import RedisSqlite


async def scheduled_broadcast():
    redis = RedisSqlite("./data/scheduler.db")
    while True:
        # TODO: 定时任务
        # await redis.connect()
        # current_time = datetime.now()
        # formatted_time = current_time.strftime('%Y%m%d%H%M')
        # result = await redis.get_list(formatted_time)
        # if result:
        #     for msg in result:
        #         logger.info(f"Schedule task: {msg}")
        #         task_model = TaskModel(**json.loads(msg))
        #         # input_ = InputModel(
        #         #     role="auxiliary",
        #         #     user_id=task_model.user_id,
        #         #     channel=task_model.channel,
        #         #     msg=f"用户在某个时间点设置的任务: 【{task_model.origin}】，现在已经到了时间点了，请执行相关操作"
        #         # )
        #         # pond_msg = await ponder(input_)
        #         # response_data = ResponseModel(
        #         #     user_id=task_model.user_id,
        #         #     msg=str(pond_msg)
        #         # )
        #         await manager.send_private_msg("Hello", websocket_list[task_model.channel])
        #
        #     await redis.empty(formatted_time)
        await asyncio.sleep(5)
