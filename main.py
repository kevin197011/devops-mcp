import json
import httpx
import requests
from fastmcp import FastMCP
from mcp.types import TextContent
from typing import List
from datetime import datetime, timedelta, timezone
import os

# Initialize MCP instance
mcp = FastMCP(name="DevOps-MCP")

# Prometheus URL configuration
PROM_URL = os.getenv("PROM_URL", "http://localhost:9090")

# Tool 1: Hello test
@mcp.tool()
def greet(name: str) -> str:
    """Greet a user by name."""
    return f"Hello, {name}!"

# Tool 2: List all available Prometheus metrics
@mcp.tool(description="List all available Prometheus metric names")
async def list_metrics() -> List[TextContent]:
    """Fetch metric names from Prometheus /api/v1/label/__name__/values endpoint"""
    url = f"{PROM_URL}/api/v1/label/__name__/values"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return [TextContent(type="text", text=resp.text)]
    except httpx.HTTPStatusError as e:
        return [TextContent(type="text", text=f"HTTP Status Error: {e.response.status_code} {e.response.text}")]
    except httpx.RequestError as e:
        return [TextContent(type="text", text=f"Request Error: {str(e)}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Unexpected Error: {str(e)}")]

# Tool 3: Synchronous Prometheus metrics query (using requests)
@mcp.tool(description="Sync query of prometheus metrics for last 5 minutes")
def get_prometheus_metrics_sync(metric: str) -> List[TextContent]:
    """
    Query specified prometheus metric for last 5 minutes and return raw data

    Args:
        metric: The prometheus metric name to query
    Returns:
        List of TextContent objects containing the query results
    """
    # Calculate time range (last 5 minutes)
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(minutes=5)

    # Build API request URL and parameters
    url = f"{PROM_URL}/api/v1/query_range"
    params = {
        "query": metric,
        "start": int(start_time.timestamp()),
        "end": int(end_time.timestamp()),
        "step": "15s"  # Step size (adjust according to data precision needs)
    }

    try:
        # Execute the request
        resp = requests.get(url, params=params, timeout=10.0)
        resp.raise_for_status()
        data = resp.json()

        # Handle response
        if data.get("status") == "success":
            return [TextContent(
                type="text",
                text=json.dumps(data["data"], indent=2)
            )]
        else:
            error_type = data.get("errorType", "Unknown errorType")
            error_message = data.get("error", "Unknown error")
            return [TextContent(
                type="text",
                text=f"Prometheus Error ({error_type}): {error_message}"
            )]

    except requests.exceptions.HTTPError as e:
        return [TextContent(type="text", text=f"HTTP Error: {str(e)}")]
    except requests.exceptions.RequestException as e:
        return [TextContent(type="text", text=f"Request Error: {str(e)}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Unexpected Error: {str(e)}")]

# Start SSE service
if __name__ == "__main__":
    try:
        mcp.run(transport="sse", host="0.0.0.0", port=8000)
    except Exception as e:
        print(f"Error starting MCP: {str(e)}")