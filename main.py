import json
import httpx
from fastmcp import FastMCP
from mcp.types import TextContent
from typing import List
from datetime import datetime, timedelta

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

@mcp.tool(description="Query raw prometheus metrics data for last 5 minutes")
async def get_prometheus_metrics(metric: str = "up") -> List[TextContent]:
    """
    Query specified prometheus metric for last 5 minutes and return raw data
    without analysis

    Args:
        metric: The prometheus metric name to query (default: 'prometheus_target_sync_failed_total')
    """
    # 计算时间范围（最近5分钟）
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(minutes=5)
    # 使用 range_query 直接获取5分钟数据
    query = f'{metric}[5m]'  # 使用传入的metric参数构建查询
    # 构建API请求URL
    url = f"{PROM_URL}/api/v1/query"
    params = {
        "query": query,
        "time": end_time.timestamp()  # 查询当前时间点的5分钟数据
    }
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            if data["status"] == "success":
                # 返回原始JSON数据
                return [TextContent(
                    type="text",
                    text=json.dumps(data["data"], indent=2)
                )]
            else:
                return [TextContent(
                    type="text",
                    text=f"Error from Prometheus: {data.get('error', 'Unknown error')}"
                )]
        except httpx.HTTPStatusError as e:
            return [TextContent(type="text", text=f"HTTP error: {str(e)}")]
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]


# 启动 SSE 服务
if __name__ == "__main__":
    mcp.run(transport="sse", host="0.0.0.0", port=8000)
