# Copyright (c) 2025 Kk
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT


import json
import httpx
from datetime import datetime, timedelta, timezone
from mcp.types import TextContent
from typing import List
from config import PROM_URL
from fastmcp import FastMCP

mcp = FastMCP(name="DevOps-MCP")

@mcp.tool(description="List all available Prometheus metric names")
async def list_metrics() -> List[TextContent]:
    """Fetch metric names from Prometheus /api/v1/label/__name__/values endpoint"""
    url = f"{PROM_URL}/api/v1/label/__name__/values"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return [TextContent(type="text", text=resp.text)]


@mcp.tool(
    description="Async query of prometheus metrics for last 5 minutes with custom metric"
)
async def get_prometheus_metrics_async_custom(metric: str) -> List[TextContent]:
    """
    Query specified prometheus metric for last 5 minutes and return raw data
    Args:
        metric: The prometheus metric name to query
    Returns:
        List of TextContent objects containing the query results
    """
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(minutes=5)

    url = f"{PROM_URL}/api/v1/query_range"
    params = {
        "query": metric,
        "start": start_time.timestamp(),
        "end": end_time.timestamp(),
        "step": "15s",
    }

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()

            if data.get("status") == "success":
                return [
                    TextContent(type="text", text=json.dumps(data["data"], indent=2))
                ]
            else:
                return [
                    TextContent(
                        type="text",
                        text=f"Prometheus Error: {data.get('error', 'Unknown error')}",
                    )
                ]

        except httpx.HTTPStatusError as e:
            return [TextContent(type="text", text=f"HTTP Error: {str(e)}")]
        except httpx.RequestError as e:
            return [TextContent(type="text", text=f"Request Error: {str(e)}")]
        except Exception as e:
            return [TextContent(type="text", text=f"Unexpected Error: {str(e)}")]
