import json

from loguru import logger

from config import config
from engine_core.utils import get_openai_client
from sdk.mcp_sdk import MCPClient
from sdk.mcp_sdk.client import SSEConnection


class MCPToolCall:
    def __init__(self):

        self.connections = {
            "basic_tools": SSEConnection(
                transport="sse",
                url="http://localhost:3001/sse"
            )
        }

    async def generate_tool_call(self, user_messages: list[dict[str, str]]):
        async with MCPClient(
                self.connections
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

    async def execute_tool_call(self, tool_name: str, tool_args: dict):
        async with MCPClient(
                self.connections
        ) as mcp_client:
            return await mcp_client.execute_tool(tool_name, tool_args)

    async def get_tools(self):
        async with MCPClient(
                self.connections
        ) as mcp_client:
            return mcp_client.get_tools()
