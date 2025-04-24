import json
import httpx
import requests
from fastmcp import FastMCP
from mcp.types import TextContent
from typing import List
from datetime import datetime, timedelta
from datetime import timezone

# Initialize MCP instance
mcp = FastMCP(name="DevOps-MCP")

# Prometheus URL configuration
PROM_URL = "http://localhost:9090"

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
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return [TextContent(type="text", text=resp.text)]

# Tool 3: Synchronous Prometheus metrics query (using requests)
@mcp.tool(description="Sync query of prometheus metrics for last 5 minutes")
def get_prometheus_metrics_sync(metric: str = "prometheus_http_requests_total") -> List[TextContent]:
    """
    Query specified prometheus metric for last 5 minutes and return raw data

    Args:
        metric: The prometheus metric name to query (default: 'prometheus_http_requests_total')
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
        "start": start_time.timestamp(),
        "end": end_time.timestamp(),
        "step": "15s"  # Step size (adjust according to data precision needs)
    }

    try:
        # Execute the request
        resp = requests.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()

        # Handle response
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

# Start SSE service
if __name__ == "__main__":
    mcp.run(transport="sse", host="0.0.0.0", port=8000)
