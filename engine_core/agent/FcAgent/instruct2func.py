import asyncio
import inspect
import json
import re
from typing import Any, AsyncGenerator

from loguru import logger

from config import config
from engine_core.utils import get_openai_client
from .prompt import fc_agent_prompt_generator
from engine_core.plugins import load_plugin


# @get_time_async
async def instruction_to_function_mapper(
        instruction: str, tools: list[dict], use_prompt=False
) -> Any:
    """用于不支持function calling的模型，将指令映射到函数"""
    if use_prompt:
        client = get_openai_client()

        prompt = fc_agent_prompt_generator(str(tools))
        response = await client.chat.completions.create(
            model=config.llm_agent_model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                },
                {
                    "role": "user",
                    "content": instruction
                }
            ],
            max_tokens=200,
            temperature=0.1,
        )
        # print(response)
        content = response.choices[0].message.content
        assert content is not None, f"Content is None: {response}"
        if content.startswith("<think>"):
            content = ''.join(re.findall(r"</think>(.*)", content, flags=re.DOTALL)).strip()

        # content = '这里是一些说明文字，接着出现一个 JSON 数组：[{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}]，后面还有其他文字'
        content_arr = list(content)

        result = None  # 用于存储查找到的 JSON 对象
        start_index = None  # JSON 对象的起始下标
        stack = 0  # 用于括号匹配的计数变量

        for index, char in enumerate(content_arr):
            if char == "[":
                # 如果当前字符为 [，则作为 JSON 对象的开始
                start_index = index
                stack = 1  # 初始化括号计数
                # 从下一个字符开始继续查找，直到所有的 [ 都匹配到 ]
            for j in range(index + 1, len(content_arr)):
                if content_arr[j] == "[":
                    stack += 1
                elif content_arr[j] == "]":
                    stack -= 1
                # 当 stack 恰好为 0 时，说明匹配完成
                if stack == 0:
                    end_index = j  # JSON 对象的结束下标
                    json_str = "".join(content_arr[start_index:end_index + 1])
                    try:
                        result = json.loads(json_str)
                    except json.JSONDecodeError as e:
                        # print("JSON 解析错误:", e)
                        break
                # 找到后退出外层循环
                if result is not None:
                    break

        if result is not None:
            # print("解析到的 JSON 对象为:")
            return result
        else:
            return {"error": "未找到 JSON 对象"}
    else:
        client = get_openai_client()
        response = await client.chat.completions.create(
            model=config.llm_agent_model,
            messages=[
                {
                    "role": "user",
                    "content": instruction
                }
            ],
            max_tokens=200,
            temperature=0.1,
            tools=tools,
        )
        if response.choices[0].message.tool_calls:
            for tool_call in response.choices[0].message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)

                logger.debug(f"tool_name - {tool_name}")
                logger.debug(f"tool_args - {tool_args}")

                tool = load_plugin(tool_name)
                if inspect.iscoroutinefunction(tool):  # 判断是否是异步函数
                    tool_result = await asyncio.create_task(tool(**tool_args))
                else:
                    tool_result = tool(**tool_args)

                if tool_result:
                    content = f"已执行函数{tool_name}, 参数: {tool_args}, 结果: {tool_result}"
                else:
                    content = f"函数{tool_name}没有返回结果",
                logger.debug(f"tool_result: {tool_result}")
                return {
                    "tool_name": tool_name,
                    "tool_args": tool_args,
                }
        else:
            return response.choices[0].message.content
