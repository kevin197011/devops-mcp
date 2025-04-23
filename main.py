import httpx
from fastmcp import FastMCP
from mcp.types import TextContent
from typing import List

# 实例化 MCP
mcp = FastMCP(name="DevOps-MCP")

# Prometheus 地址配置
PROM_URL = "http://localhost:9090"

# 工具 1：Hello 测试
@mcp.tool()
def greet(name: str) -> str:
    """Greet a user by name."""
    return f"Hello, {name}!"

# 工具 2：查询 Prometheus 所有 metric 名字
@mcp.tool(description="List all available Prometheus metric names")
async def list_metrics() -> List[TextContent]:
    """Fetch metric names from Prometheus /api/v1/label/__name__/values"""
    url = f"{PROM_URL}/api/v1/label/__name__/values"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return [TextContent(type="text", text=resp.text)]

# 启动 SSE 服务
if __name__ == "__main__":
    mcp.run(transport="sse", host="0.0.0.0", port=8000)
