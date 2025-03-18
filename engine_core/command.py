# websocket/commands.py
import asyncio
import inspect
import json

from fastapi import WebSocket
from loguru import logger

from engine_core.hmq import connect_hmq
from engine_core.task_db import task_center
from engine_core.plugins import load_plugin
from models import ChatCompletionRequest
from websocket import manager

# 命令注册表
commands = {}


def command(path):
    """
    命令注册装饰器
    :param path: 命令路径，如 "/approve"
    """

    def decorator(func):
        commands[path] = func
        return func

    return decorator


@command("/approve")
async def approve(chat_completion_request: ChatCompletionRequest, websocket: WebSocket, chunk_wrapper):
    """批准用户最新任务"""
    try:
        try:
            task = task_center.get_task(chat_completion_request.extra_headers.authorization)
        except Exception as e:
            logger.error(f"获取任务时出现错误: {e}")
            for i in f"error: {e}":
                await manager.send_private_stream(chunk_wrapper.content_chunk_wrapper(i), websocket)
            return
        tool_chain = json.loads(task.data)
        for tool_call in tool_chain:
            tool_name = tool_call["tool_name"]
            tool_args = tool_call["tool_args"]

            logger.debug(f"tool_name - {tool_name}")
            logger.debug(f"tool_args - {tool_args}")
            try:
                tool = load_plugin(tool_name)
                if inspect.iscoroutinefunction(tool):  # 判断是否是异步函数
                    tool_result = await asyncio.create_task(tool(**tool_args))
                else:
                    tool_result = tool(**tool_args)

                if tool_result:
                    content = f"已执行函数{tool_name}, 参数: {tool_args}, 结果: {tool_result}"
                else:
                    content = f"函数{tool_name}没有返回结果"
                logger.debug(f"tool_result: {tool_result}")
            except Exception as err:
                logger.error(f"执行函数{tool_name}运行时错误，错误捕获：{err}")
                content = f"执行函数{tool_name}运行时错误，错误捕获：{err}"

            # response = task.model_dump() if task else {"error": "没有找到可批准的任务或任务已过期"}
            # for i in f"{response}":
            #     await manager.send_private_stream(chunk_wrapper.content_chunk_wrapper(i), websocket)
            # await manager.send_private_stream(chunk_wrapper.content_chunk_wrapper("\n\n"), websocket)
            for i in f"{content}":
                await manager.send_private_stream(chunk_wrapper.content_chunk_wrapper(i), websocket)

            task_center.approve_task(chat_completion_request.extra_headers.authorization)
    except Exception as err:
        logger.error(f"出现未知错误: {err}")
        for i in f"error: {err}":
            await manager.send_private_stream(chunk_wrapper.content_chunk_wrapper(i), websocket)


@command("/help")
async def help_command(chat_completion_request: ChatCompletionRequest, websocket: WebSocket, chunk_wrapper):
    """显示帮助信息"""
    commands_list = ", ".join(commands.keys())
    for i in f"可用命令: {commands_list}":
        await manager.send_private_stream(chunk_wrapper.content_chunk_wrapper(i), websocket)


@command("/clear")
async def clear_chat_history(chat_completion_request: ChatCompletionRequest, websocket: WebSocket, chunk_wrapper):
    """清空聊天记录"""
    try:
        hmq = connect_hmq(chat_completion_request.extra_headers.authorization)
        await hmq.delete(chat_completion_request.extra_headers.authorization)
        for i in f"聊天记录已清空":
            await manager.send_private_stream(chunk_wrapper.content_chunk_wrapper(i), websocket)
    except Exception as e:
        logger.error(f"清空聊天记录时出现错误: {e}")
        for i in f"error: {e}":
            await manager.send_private_stream(chunk_wrapper.content_chunk_wrapper(i), websocket)


@command("/get-history")
async def get_history(chat_completion_request: ChatCompletionRequest, websocket: WebSocket, chunk_wrapper):
    """获取聊天记录"""
    try:
        hmq = connect_hmq(chat_completion_request.extra_headers.authorization)
        history = await hmq.get(chat_completion_request.extra_headers.authorization)
        for i in f"聊天记录: {history}":
            await manager.send_private_stream(chunk_wrapper.content_chunk_wrapper(i), websocket)
    except Exception as e:
        logger.error(f"获取聊天记录时出现错误: {e}")
        for i in f"error: {e}":
            await manager.send_private_stream(chunk_wrapper.content_chunk_wrapper(i), websocket)
