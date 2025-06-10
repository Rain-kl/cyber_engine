import mcp.types

from config import config
from sdk.mcp_sdk import MCPClient
from sdk.mcp_sdk.client import SSEConnection


class MCPToolCall:
    def __init__(self):
        self.connections = {
            "basic_tools": SSEConnection(
                transport=config.mcp_basic_tools_transport,
                url=config.mcp_basic_tools_url,
            )
        }

    async def execute(
        self, tool_name: str, tool_args: dict
    ) -> mcp.types.CallToolResult:
        async with MCPClient(self.connections) as mcp_client:
            return await mcp_client.execute_tool(tool_name, tool_args)

    async def get_tools(self):
        async with MCPClient(self.connections) as mcp_client:
            return mcp_client.get_tools()

    async def get_openai_format_tools(self):
        async with MCPClient(self.connections) as mcp_client:
            return mcp_client.get_openai_format_tools()
