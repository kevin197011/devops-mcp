# Copyright (c) 2025 Kk
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

from mcp.server.fastmcp import FastMCP
import os


def devops_register_tools(mcp: FastMCP):
    """注册工具到 MCP 实例"""

    @mcp.tool(description="hello a user by name")
    async def hello(name: str) -> str:
        """Greet a user by name."""
        return f"Hello, {name}!"

    @mcp.tool(description="print url")
    async def prom_debug() -> str:
        """Debug Prometheus URL"""
        return os.getenv("PROM_URL", "http://localhost:9090")
