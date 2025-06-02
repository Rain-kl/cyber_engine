# websocket/commands.py
import json

from fastapi import WebSocket
from loguru import logger

from engine_core.agent.FcAgent.mcp_tool_call import MCPToolCall
from engine_core.hmdb import connect_hmdb
from engine_core.hmq import connect_hmq
from engine_core.task_db import task_center
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
        mcp_tool_call = MCPToolCall()
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
                tool_result = await mcp_tool_call.execute_tool_call(tool_name, tool_args)
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
    finally:
        await manager.send_private_stream(chunk_wrapper.finish_chunk(), websocket)


@command("/help")
async def help_command(chat_completion_request: ChatCompletionRequest, websocket: WebSocket, chunk_wrapper):
    """显示帮助信息"""
    try:
        commands_list = ", ".join(commands.keys())
        for i in f"可用命令: {commands_list}":
            await manager.send_private_stream(chunk_wrapper.content_chunk_wrapper(i), websocket)
    except Exception as e:
        logger.error(f"显示帮助信息时出现错误: {e}")
        for i in f"error: {e}":
            await manager.send_private_stream(chunk_wrapper.content_chunk_wrapper(i), websocket)
    finally:
        await manager.send_private_stream(chunk_wrapper.finish_chunk(), websocket)


@command("/clear")
async def clear_chat_history(chat_completion_request: ChatCompletionRequest, websocket: WebSocket, chunk_wrapper):
    """清空聊天记录"""
    try:
        user_id = chat_completion_request.extra_headers.authorization
        # 清空HMQ中的消息
        hmq = connect_hmq(user_id)
        await hmq.delete(user_id)

        # 清空HMDB中的历史消息（仅当前用户）
        hmdb = connect_hmdb(user_id)
        await hmdb.connect()
        await hmdb.delete_messages(user_id=user_id)

        for i in f"聊天记录已清空":
            await manager.send_private_stream(chunk_wrapper.content_chunk_wrapper(i), websocket)
    except Exception as e:
        logger.error(f"清空聊天记录时出现错误: {e}")
        for i in f"error: {e}":
            await manager.send_private_stream(chunk_wrapper.content_chunk_wrapper(i), websocket)
    finally:
        await manager.send_private_stream(chunk_wrapper.finish_chunk(), websocket)


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
    finally:
        await manager.send_private_stream(chunk_wrapper.finish_chunk(), websocket)


@command("/get-all-history")
async def get_all_history(chat_completion_request: ChatCompletionRequest, websocket: WebSocket, chunk_wrapper):
    """获取包括存档在内的所有聊天记录"""
    try:
        # 从HMQ获取当前对话
        hmq = connect_hmq(chat_completion_request.extra_headers.authorization)
        current_history = await hmq.get(chat_completion_request.extra_headers.authorization)

        # 从HMDB获取存档历史记录（仅当前用户）
        user_archived_history = await hmq.get_history_from_db(limit=100)

        # 发送当前对话记录
        for i in f"当前对话: {current_history}":
            await manager.send_private_stream(chunk_wrapper.content_chunk_wrapper(i), websocket)

        # 发送当前用户的存档历史记录
        await manager.send_private_stream(chunk_wrapper.content_chunk_wrapper("\n\n当前用户存档记录:\n"), websocket)
        for i, message in enumerate(user_archived_history):
            msg = f"{i + 1}. [{message['timestamp']}] {message['role']}: {message['content']}\n"
            await manager.send_private_stream(chunk_wrapper.content_chunk_wrapper(msg), websocket)

    except Exception as e:
        logger.error(f"获取所有聊天记录时出现错误: {e}")
        for i in f"error: {e}":
            await manager.send_private_stream(chunk_wrapper.content_chunk_wrapper(i), websocket)
    finally:
        await manager.send_private_stream(chunk_wrapper.finish_chunk(), websocket)


@command("/get-all-users-history")
async def get_all_users_history(chat_completion_request: ChatCompletionRequest, websocket: WebSocket, chunk_wrapper):
    """获取所有用户的聊天记录"""
    try:
        # 从HMDB获取所有用户的存档历史记录
        hmq = connect_hmq(chat_completion_request.extra_headers.authorization)
        all_users_history = await hmq.get_all_users_history(limit=100)

        # 发送所有用户的历史记录
        await manager.send_private_stream(chunk_wrapper.content_chunk_wrapper("所有用户的历史记录:\n"), websocket)
        for i, message in enumerate(all_users_history):
            msg = f"{i + 1}. 用户: {message['user_id']} - [{message['timestamp']}] {message['role']}: {message['content']}\n"
            await manager.send_private_stream(chunk_wrapper.content_chunk_wrapper(msg), websocket)

    except Exception as e:
        logger.error(f"获取所有用户聊天记录时出现错误: {e}")
        for i in f"error: {e}":
            await manager.send_private_stream(chunk_wrapper.content_chunk_wrapper(i), websocket)
    finally:
        await manager.send_private_stream(chunk_wrapper.finish_chunk(), websocket)


@command("/get-tools")
async def get_all_tools(chat_completion_request: ChatCompletionRequest, websocket: WebSocket, chunk_wrapper):
    """列出可用工具"""
    try:
        mcp_tool_call = MCPToolCall()
        # 列出可用工具
        available_tools = await mcp_tool_call.get_tools()
        for i in f"可用工具: {available_tools}":
            await manager.send_private_stream(chunk_wrapper.content_chunk_wrapper(i), websocket)
    except Exception as e:
        logger.error(f"列出可用工具时出现错误: {e}")
        for i in f"error: {e}":
            await manager.send_private_stream(chunk_wrapper.content_chunk_wrapper(i), websocket)
    finally:
        await manager.send_private_stream(chunk_wrapper.finish_chunk(), websocket)
