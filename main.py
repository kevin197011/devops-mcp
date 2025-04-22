"""
MCP Website Fetcher Server - Consolidated Implementation

Combines all functionality in a single file with clearly separated components.
"""

# import anyio
import httpx
from typing import List, Union
from mcp.server.lowlevel import Server
import mcp.types as types
from mcp.server.sse import SseServerTransport
import uvicorn
from starlette.applications import Starlette
from starlette.routing import Mount, Route

# ======================
# Core Business Logic
# ======================


def create_http_client() -> httpx.AsyncClient:
    """Create configured HTTP client"""
    return httpx.AsyncClient(
        follow_redirects=True,
        headers={
            "User-Agent": "MCP Test Server (github.com/modelcontextprotocol/python-sdk)"
        },
    )


async def fetch_website_content(url: str, client: httpx.AsyncClient) -> str:
    """Pure function to fetch raw website content"""
    response = await client.get(url)
    response.raise_for_status()
    return response.text


def create_content_response(text: str) -> List[types.TextContent]:
    """Transform raw content into MCP content objects"""
    return [types.TextContent(type="text", text=text)]


# ======================
# Tool Definitions
# ======================


def make_fetch_tool_definition() -> types.Tool:
    """Create the tool metadata definition"""
    return types.Tool(
        name="fetch",
        description="Fetches a website and returns its content",
        inputSchema={
            "type": "object",
            "required": ["url"],
            "properties": {
                "url": {
                    "type": "string",
                    "description": "URL to fetch",
                }
            },
        },
    )


async def handle_fetch_tool(name: str, arguments: dict) -> List[types.TextContent]:
    """Tool handler for 'fetch' command"""
    if name != "fetch":
        raise ValueError(f"Unknown tool: {name}")
    if "url" not in arguments:
        raise ValueError("Missing required argument 'url'")

    async with create_http_client() as client:
        content = await fetch_website_content(arguments["url"], client)
        return create_content_response(content)


async def handle_list_tools() -> List[types.Tool]:
    """Returns metadata about available tools"""
    return [make_fetch_tool_definition()]


# ======================
# Server Management
# ======================


def create_mcp_server(name: str = "mcp-website-fetcher") -> Server:
    """Initialize and configure MCP server with tools"""
    server = Server(name)

    # Register tool handlers
    server.call_tool()(handle_fetch_tool)
    server.list_tools()(handle_list_tools)

    return server


async def run_server_with_streams(server: Server, input_stream, output_stream):
    """Run server with specified I/O streams"""
    await server.run(
        input_stream, output_stream, server.create_initialization_options()
    )


# ======================
# Transport Implementations
# ======================


class SSETransport:
    """Server-Sent Events transport implementation"""

    def __init__(self, port: int = 8000):
        self.port = port
        self.sse = SseServerTransport("/messages/")

    async def handle_sse(self, request):
        """SSE endpoint handler"""
        async with self.sse.connect_sse(
            request.scope, request.receive, request._send
        ) as streams:
            await run_server_with_streams(self.server, streams[0], streams[1])

    def create_starlette_app(self, server: Server):
        """Initialize Starlette application"""
        self.server = server
        return Starlette(
            debug=True,
            routes=[
                Route("/sse", self.handle_sse),
                Mount("/messages/", app=self.sse.handle_post_message),
            ],
        )

    def run(self, server: Server):
        """Run server in SSE mode"""
        app = self.create_starlette_app(server)
        uvicorn.run(app, host="0.0.0.0", port=self.port, log_level="info")


# ======================
# CLI Interface
# ======================


def main():
    """Main entry point for the MCP Website Fetcher Server"""
    server = create_mcp_server()
    SSETransport(8000).run(server)


if __name__ == "__main__":
    main()
