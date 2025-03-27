from contextlib import AsyncExitStack
from types import TracebackType
from typing import Any, Literal, TypedDict, cast

from httpx_sse import SSEError
from mcp import ClientSession, StdioServerParameters
from mcp.client.sse import sse_client
from mcp.client.stdio import stdio_client
from mcp.types import Tool

DEFAULT_HTTP_TIMEOUT = 10
DEFAULT_ENCODING = "utf-8"
DEFAULT_SSE_READ_TIMEOUT = 5
DEFAULT_ENCODING_ERROR_HANDLER = "strict"


async def load_mcp_tools(session: ClientSession) -> list[Tool]:
    """Load all available MCP tools and convert them to LangChain tools."""
    # 列出可用工具
    response = await session.list_tools()
    return response.tools


class StdioConnection(TypedDict):
    transport: Literal["stdio"]

    command: str
    """The executable to run to start the server."""

    args: list[str]
    """Command line arguments to pass to the executable."""

    env: dict[str, str] | None
    """The environment to use when spawning the process."""

    encoding: str
    """The text encoding used when sending/receiving messages to the server."""

    encoding_error_handler: Literal["strict", "ignore", "replace"]
    """
    The text encoding error handler.

    See https://docs.python.org/3/library/codecs.html#codec-base-classes for
    explanations of possible values
    """


class SSEConnection(TypedDict):
    transport: Literal["sse"]

    url: str
    """The URL of the SSE endpoint to connect to."""

    headers: dict[str, Any] | None = None
    """HTTP headers to send to the SSE endpoint"""

    timeout: float
    """HTTP timeout"""

    sse_read_timeout: float
    """SSE read timeout"""


class MCPClient:
    """Client for connecting to multiple MCP servers and loading LangChain-compatible tools from them."""

    def __init__(self, connections: dict[str, StdioConnection | SSEConnection] = None) -> None:
        """Initialize a MultiServerMCPClient with MCP servers connections.

        Args:
            connections: A dictionary mapping server names to connection configurations.
                Each configuration can be either a StdioConnection or SSEConnection.
                If None, no initial connections are established.

        Example:

            ```python
            async with MultiServerMCPClient(
                {
                    "math": {
                        "command": "python",
                        # Make sure to update to the full absolute path to your math_server.py file
                        "args": ["/path/to/math_server.py"],
                        "transport": "stdio",
                    },
                    "weather": {
                        # make sure you start your weather server on port 8000
                        "url": "http://localhost:8000/sse",
                        "transport": "sse",
                    }
                }
            ) as client:
                all_tools = client.get_tools()
                ...
            ```
        """
        self.connections = connections
        self.exit_stack = AsyncExitStack()
        self.sessions: dict[str, ClientSession] = {}
        self.server_name_to_tools: dict[str, list[Tool]] = {}

    async def _initialize_session_and_load_tools(
            self, server_name: str, session: ClientSession
    ) -> None:
        """Initialize a session and load tools from it.

        Args:
            server_name: Name to identify this server connection
            session: The ClientSession to initialize
        """
        # Initialize the session
        await session.initialize()
        self.sessions[server_name] = session

        # Load tools from this server
        server_tools = await load_mcp_tools(session)
        self.server_name_to_tools[server_name] = server_tools

    async def connect_to_server(
            self,
            server_name: str,
            *,
            transport: Literal["stdio", "sse"] = "stdio",
            **kwargs,
    ) -> None:
        """Connect to an MCP server using either stdio or SSE.

        This is a generic method that calls either connect_to_server_via_stdio or connect_to_server_via_sse
        based on the provided transport parameter.

        Args:
            server_name: Name to identify this server connection
            transport: Type of transport to use ("stdio" or "sse"), defaults to "stdio"
            **kwargs: Additional arguments to pass to the specific connection method

        Raises:
            ValueError: If transport is not recognized
            ValueError: If required parameters for the specified transport are missing
        """
        if transport == "sse":
            if "url" not in kwargs:
                raise ValueError("'url' parameter is required for SSE connection")
            await self.connect_to_server_via_sse(
                server_name,
                url=kwargs["url"],
                headers=kwargs.get("headers"),
                timeout=kwargs.get("timeout", DEFAULT_HTTP_TIMEOUT),
                sse_read_timeout=kwargs.get("sse_read_timeout", DEFAULT_SSE_READ_TIMEOUT),
            )
        elif transport == "stdio":
            if "command" not in kwargs:
                raise ValueError("'command' parameter is required for stdio connection")
            if "args" not in kwargs:
                raise ValueError("'args' parameter is required for stdio connection")
            await self.connect_to_server_via_stdio(
                server_name,
                command=kwargs["command"],
                args=kwargs["args"],
                env=kwargs.get("env"),
                encoding=kwargs.get("encoding", DEFAULT_ENCODING)
            )
        else:
            raise ValueError(f"Unsupported transport: {transport}. Must be 'stdio' or 'sse'")

    async def connect_to_server_via_stdio(
            self,
            server_name: str,
            *,
            command: str,
            args: list[str],
            env: dict[str, str] | None = None,
            encoding: str = DEFAULT_ENCODING,
            encoding_error_handler: Literal[
                "strict", "ignore", "replace"
            ] = DEFAULT_ENCODING_ERROR_HANDLER,
    ) -> None:
        """Connect to a specific MCP server using stdio

        Args:
            server_name: Name to identify this server connection
            command: Command to execute
            args: Arguments for the command
            env: Environment variables for the command
            encoding: Character encoding
            encoding_error_handler: How to handle encoding errors
        """
        server_params = StdioServerParameters(
            command=command,
            args=args,
            env=env,
            encoding=encoding,
            encoding_error_handler=encoding_error_handler,
        )

        # Create and store the connection
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        read, write = stdio_transport
        session = cast(
            ClientSession,
            await self.exit_stack.enter_async_context(ClientSession(read, write)),
        )

        await self._initialize_session_and_load_tools(server_name, session)

    async def connect_to_server_via_sse(
            self,
            server_name: str,
            *,
            url: str,
            headers: dict[str, Any] | None = None,
            timeout: float = DEFAULT_HTTP_TIMEOUT,
            sse_read_timeout: float = DEFAULT_SSE_READ_TIMEOUT,
    ) -> None:
        """Connect to a specific MCP server using SSE

        Args:
            server_name: Name to identify this server connection
            url: URL of the SSE server
            headers: HTTP headers to send to the SSE endpoint
            timeout: HTTP timeout
            sse_read_timeout: SSE read timeout
        """
        # Create and store the connection
        try:
            sse_transport = await self.exit_stack.enter_async_context(
                sse_client(url, headers, timeout, sse_read_timeout)
            )
            read, write = sse_transport
            session = cast(
                ClientSession,
                await self.exit_stack.enter_async_context(ClientSession(read, write)),
            )

            await self._initialize_session_and_load_tools(server_name, session)
        except Exception as e:
            raise SSEError(f"Failed to connect to SSE server at {url}") from e

    def get_tools(self) -> list[dict]:
        """Get a list of all tools from all connected servers."""
        all_tools: list[Tool] = []
        for server_tools in self.server_name_to_tools.values():
            all_tools.extend(server_tools)
        return all_tools

    def get_openai_format_tools(self):
        all_tools: list[Tool] = []
        for server_tools in self.server_name_to_tools.values():
            all_tools.extend(server_tools)
        return [{
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.inputSchema
            }
        } for tool in all_tools]

    def execute_tool(self, tool_name: str, tool_args: dict[str, Any]):
        # Find the tool
        for server_name, server_tools in self.server_name_to_tools.items():
            for tool in server_tools:
                if tool.name == tool_name:
                    # Execute the tool
                    return self.sessions[server_name].call_tool(tool_name, tool_args)
        raise ValueError(f"Tool '{tool_name}' not found")

    async def __aenter__(self) -> "MCPClient":
        try:
            connections = self.connections or {}
            for server_name, connection in connections.items():
                connection_dict = connection.copy()
                transport = connection_dict.pop("transport")
                if transport == "stdio":
                    await self.connect_to_server_via_stdio(server_name, **connection_dict)
                elif transport == "sse":
                    await self.connect_to_server_via_sse(server_name, **connection_dict)
                else:
                    raise ValueError(
                        f"Unsupported transport: {transport}. Must be 'stdio' or 'sse'"
                    )
            return self
        except Exception:
            await self.exit_stack.aclose()
            raise

    async def __aexit__(
            self,
            exc_type: type[BaseException] | None,
            exc_val: BaseException | None,
            exc_tb: TracebackType | None,
    ) -> None:
        await self.exit_stack.aclose()
