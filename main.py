import json
import httpx
import requests
from fastmcp import FastMCP
from mcp.types import TextContent
from typing import List
from datetime import datetime, timedelta
from datetime import timezone
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

# @mcp.tool(description="Query raw prometheus metrics data for last 5 minutes")
# async def get_prometheus_metrics(metric: str = "up") -> List[TextContent]:
#     """
#     Query specified prometheus metric for last 5 minutes and return raw data
#     without analysis

#     Args:
#         metric: The prometheus metric name to query (default: 'up')
#     """
#     # 计算时间范围（最近5分钟）
#     end_time = datetime.now(timezone.utc)
#     start_time = end_time - timedelta(minutes=5)
#     # 使用 range_query 直接获取5分钟数据
#     query = f'{metric}[5m]'  # 使用传入的metric参数构建查询
#     # 构建API请求URL
#     url = f"{PROM_URL}/api/v1/query_range"
#     params = {
#         "query": metric,  # 不附加 [5m]，直接在 range 中指定时间范围
#         "start": start_time.timestamp(),
#         "end": end_time.timestamp(),
#         "step": "15s"  # 步长（根据数据精度调整）
#     }
#     async with httpx.AsyncClient() as client:
#         try:
#             resp = await client.get(url, params=params)
#             resp.raise_for_status()
#             data = resp.json()
#             if data["status"] == "success":
#                 # 返回原始JSON数据
#                 print([TextContent(
#                     type="text",
#                     text=json.dumps(data["data"], indent=2)
#                 )])
#                 return [TextContent(
#                     type="text",
#                     text=json.dumps(data["data"], indent=2)
#                 )]
#             else:
#                 return [TextContent(
#                     type="text",
#                     text=f"Error from Prometheus: {data.get('error', 'Unknown error')}"
#                 )]
#         except httpx.HTTPStatusError as e:
#             return [TextContent(type="text", text=f"HTTP error: {str(e)}")]
#         except Exception as e:
#             return [TextContent(type="text", text=f"Error: {str(e)}")]


# 工具 3：同步版 Prometheus 指标查询（使用requests）
@mcp.tool(description="Sync query of prometheus metrics for last 5 minutes")
def get_prometheus_metrics_sync(metric: str = "prometheus_http_requests_total") -> List[TextContent]:
    """
    Query specified prometheus metric for last 5 minutes and return raw data

    Args:
        metric: The prometheus metric name (default: 'prometheus_http_requests_total')
    """
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(minutes=5)

    url = f"{PROM_URL}/api/v1/query_range"
    params = {
        "query": metric,
        "start": start_time.timestamp(),
        "end": end_time.timestamp(),
        "step": "15s"
    }

    try:
        resp = requests.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()

        if data.get("status") == "success":
            return [TextContent(
                type="text",
                text=json.dumps(data["data"], indent=2)
            )]
        else:
            return [TextContent(
                type="text",
                text=f"Prometheus Error: {data.get('error', 'Unknown error')}"
            )]

    except requests.exceptions.HTTPError as e:
        return [TextContent(type="text", text=f"HTTP Error: {str(e)}")]
    except requests.exceptions.RequestException as e:
        return [TextContent(type="text", text=f"Request Error: {str(e)}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Unexpected Error: {str(e)}")]

# 启动 SSE 服务
if __name__ == "__main__":
    mcp.run(transport="sse", host="0.0.0.0", port=8000)
