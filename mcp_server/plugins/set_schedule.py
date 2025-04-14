# from datetime import datetime
#
# from loguru import logger
#
# from event_log import elogger, EventLogModel
# from models import TaskModel
# from redis_mq import RedisSqlite
#
#
# async def set_schedule(trigger_time: str, tasks: str):
#     logger.info(f"Setting schedule, trigger time: {trigger_time}, tasks: {tasks}")
#     try:
#         datetime.strptime(trigger_time, "%Y%m%d%H%M")
#         redis = RedisSqlite("./data/scheduler.db")
#         await redis.connect()
#         await redis.rpush(
#             trigger_time,
#             TaskModel(user_id=input_.user_id, tasks=tasks, origin=input_.msg, channel="t").__str__(),
#         )
#         elogger.log(EventLogModel(
#             user_id=input_.user_id,
#             type="func",
#             level=EventLogModel.LEVEL.INFO,
#             message=f"Set schedule, trigger time: {trigger_time}, tasks: {tasks}"
#         ))
#     except Exception as e:
#         logger.error(f'error: {e}')
#         elogger.log(EventLogModel(
#             user_id=input_.user_id,
#             type="func",
#             level=EventLogModel.LEVEL.ERROR,
#             message=f"error: {e} | Set schedule, trigger time: {trigger_time}, tasks: {tasks}"
#         ))
#         return f'error: {e}'
#     return "Schedule set successfully"
#
#
# schedule_tools = {
#     "type": "function",
#     "function": {
#         "name": "set_schedule",
#         "description": "Set scheduled tasks, which can be scheduled reminders or scheduled execution of operations. Please do not set reminders within 5 minutes",
#         "parameters": {
#             "type": "object",
#             "properties": {
#                 "trigger_time": {
#                     "type": "string",
#                     "description": "The time to trigger the schedule, in the format of 'YYYYMMDDHHMM'，If the user does not specify a specific time, it defaults to 8am in the morning",
#                 },
#                 "tasks": {
#                     "type": "string",
#                     "description": "You need to write down what you need to do in the memo, and the auxiliary will remind you at the designated time",
#                 },
#             },
#             "required": ["trigger_time", "tasks"],
#         },
#     }
# }
