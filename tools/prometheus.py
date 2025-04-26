# Copyright (c) 2025 Kk
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import os
import httpx
from datetime import datetime, timedelta, timezone
from typing import List
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

prom_url = os.getenv("PROM_URL", "http://localhost:9090")


def register_prometheus_tools(mcp: FastMCP):
    """注册 Prometheus 工具到 MCP 实例"""

    @mcp.tool(description="List all available Prometheus metric names")
    async def list_metrics() -> List[str]:
        """
        Fetch metric names from Prometheus /api/v1/label/__name__/values endpoint.
        Returns:
            A list of metric names.
        """
        url = f"{prom_url}/api/v1/label/__name__/values"
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                if data.get("status") == "success":
                    return data.get("data", [])
                else:
                    return [f"Error: {data.get('error', 'Unknown error')}"]
            except Exception as e:
                return [f"Error fetching metrics: {str(e)}"]

    @mcp.tool(description="Query Prometheus metrics for a specific time range")
    async def query_metrics(metric: str, minutes: int = 5) -> List[dict]:
        """
        Query specified Prometheus metric for the last N minutes.
        Args:
            metric: The Prometheus metric name to query.
            minutes: The time range in minutes (default is 5 minutes).
        Returns:
            A list of metric data points.
        """
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(minutes=minutes)

        url = f"{prom_url}/api/v1/query_range"
        params = {
            "query": metric,
            "start": start_time.timestamp(),
            "end": end_time.timestamp(),
            "step": "15s",
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                if data.get("status") == "success":
                    return data.get("data", {}).get("result", [])
                else:
                    return [{"error": data.get("error", "Unknown error")}]
            except Exception as e:
                return [{"error": str(e)}]
