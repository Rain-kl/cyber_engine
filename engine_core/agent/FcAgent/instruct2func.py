import asyncio
import inspect
import json
import re
from typing import Any

from loguru import logger

from config import config
from engine_core.plugins import load_plugin
from engine_core.utils import get_openai_client, parse_json_object
from .prompt import fc_agent_prompt_generator


# @get_time_async
async def instruction_to_function_mapper(
        user_messages: list[dict[str, str]], tools: list[dict], use_prompt=True
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
                *user_messages
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
        return parse_json_object(content)
    else:
        client = get_openai_client()
        response = await client.chat.completions.create(
            model=config.llm_agent_model,
            messages=[
                # {
                #     "role": "user",
                #     "content": instruction
                # },
                *user_messages
            ],
            max_tokens=200,
            temperature=0.1,
            tools=tools,
        )
        if response.choices[0].message.tool_calls:
            tools_chain = []
            for tool_call in response.choices[0].message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)

                logger.debug(f"tool_name - {tool_name}")
                logger.debug(f"tool_args - {tool_args}")

                tools_chain.append({
                    "tool_name": tool_name,
                    "tool_args": tool_args,
                })
            return tools_chain
        else:
            return response.choices[0].message.content
