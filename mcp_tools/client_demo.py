import asyncio
import json
from contextlib import AsyncExitStack
from typing import Optional

from mcp import ClientSession
from mcp.client.sse import sse_client
from openai import AsyncOpenAI


class MCPClient:
    def __init__(self):
        # 初始化会话和客户端对象
        self.session: Optional[ClientSession] = None  # 会话对象
        self.exit_stack = AsyncExitStack()  # 退出堆栈
        self.openai = AsyncOpenAI(
            base_url="https://us.ifopen.ai/v1",
            api_key="sk-M2PdpI7oW8FAw9OZ8fttrSXLkHmrXNYpHgKbS6AYy7lswmjn",
        )
        self.model = "gpt-4o"

    async def get_response(self, messages: list, tools: list):
        try:
            response = await self.openai.chat.completions.create(
                model=self.model,
                max_tokens=1000,
                messages=messages,
                tools=tools,
            )
            return response
        except Exception as e:
            print(f"获取响应时出错: {e}")
            # 返回一个合适的错误对象，而不是协程
            return None  # 或者创建一个模拟响应对象

    async def get_tools(self):
        # 列出可用工具
        response = await self.session.list_tools()
        available_tools = [{
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,  # 工具描述
                "parameters": tool.inputSchema  # 工具输入模式
            }
        } for tool in response.tools]

        return available_tools

    async def connect_to_sse_server(self, server_url: str):
        """Connect to an MCP server running with SSE transport"""
        # Store the context managers so they stay alive
        self._streams_context = sse_client(url=server_url)
        streams = await self._streams_context.__aenter__()

        self._session_context = ClientSession(*streams)
        self.session: ClientSession = await self._session_context.__aenter__()

        # Initialize
        await self.session.initialize()

        # List available tools to verify connection
        print("Initialized SSE client...")
        print("Listing tools...")
        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])

    async def process_query(self, query: str) -> str:
        """使用 OpenAI 和可用工具处理查询"""

        # 创建消息列表
        messages = [
            {
                "role": "user",
                "content": query
            }
        ]

        # 列出可用工具
        available_tools = await self.get_tools()
        # 处理消息
        response = await self.get_response(messages, available_tools)

        # 处理LLM响应和工具调用
        tool_results = []
        final_text = []
        for choice in response.choices:
            message = choice.message
            is_function_call = message.tool_calls
            # if is_function_call:
            #    print("准备调用工具",is_function_call)
            # 如果不调用工具，则添加到 final_text 中
            if not is_function_call:
                final_text.append(message.content)
            # 如果是工具调用，则获取工具名称和输入
            else:
                # 解包tool_calls
                tool_name = message.tool_calls[0].function.name
                tool_args = json.loads(message.tool_calls[0].function.arguments)
                print(f"准备调用工具: {tool_name}")
                print(f"参数: {json.dumps(tool_args, ensure_ascii=False, indent=2)}")
                # 执行工具调用，获取结果
                result = await self.session.call_tool(tool_name, tool_args)
                tool_results.append({"call": tool_name, "result": result})
                final_text.append(f"[Calling tool {tool_name} with args {tool_args}]")

                # 继续与工具结果进行对话
                if message.content and hasattr(message.content, 'text'):
                    messages.append({
                        "role": "assistant",
                        "content": message.content
                    })
                # 将工具调用结果添加到消息
                messages.append({
                    "role": "user",
                    "content": result.content
                })
                # 获取下一个LLM响应
                response = await self.get_response(messages, available_tools)
                # 将结果添加到 final_text
                final_text.append(response.choices[0].message.content)

        return "\\n".join(final_text)

    async def chat_loop(self):
        """运行交互式聊天循环（没有记忆）"""
        print("\\nMCP Client 启动!")
        print("输入您的查询或 'quit' 退出.")

        while True:

            query = input("\\nQuery: ").strip()

            if query.lower() == 'quit':
                break

            response = await self.process_query(query)
            print("\\n" + response)


    async def cleanup(self):
        """清理资源"""
        await self.exit_stack.aclose()


async def main():

    client = MCPClient()
    try:
        await client.connect_to_sse_server(server_url="http://localhost:3001/sse")
        await client.chat_loop()
    finally:
        await client.cleanup()


if __name__ == "__main__":
    import sys

    asyncio.run(main())
