# Copyright (c) 2025 Kk
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

from mcp.server.fastmcp import FastMCP
import os
from dotenv import load_dotenv

load_dotenv()

prom_url = os.getenv("PROM_URL", "http://192.168.1.5:9090")


def register_devops_tools(mcp: FastMCP):
    """注册工具到 MCP 实例"""

    @mcp.tool(description="hello a user by name")
    async def hello(name: str) -> str:
        """Greet a user by name."""
        return f"Hello, {name}!"

    @mcp.tool(description="print url")
    async def prom_debug() -> str:
        """Debug Prometheus URL"""
        return prom_url
