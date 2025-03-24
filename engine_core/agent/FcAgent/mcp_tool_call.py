import json

from loguru import logger

from config import config
from engine_core.utils import get_openai_client
from mcp_sdk import MCPClient


async def mcp_generate_tool_call(user_messages: list[dict[str, str]]):
    async with MCPClient(
            {
                "basic_tools": {
                    # make sure you start your weather server on port 8000
                    "url": "http://localhost:3001/sse",
                    "transport": "sse",
                }
            }
    ) as mcp_client:
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
            tools=mcp_client.get_openai_format_tools(),
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
