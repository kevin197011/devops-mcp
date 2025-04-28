# Copyright (c) 2025 Kk
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

from mcp.server.fastmcp import FastMCP
from tools.demo import register_devops_tools
from tools.prometheus import register_prometheus_tools

mcp = FastMCP(name="DevOps-MCP", host="0.0.0.0", port=8000)
register_devops_tools(mcp)
register_prometheus_tools(mcp)

if __name__ == "__main__":
    try:
        mcp.run(transport="sse")
    except Exception as e:
        print(f"Error starting MCP: {e}")
