# Copyright (c) 2025 Kk
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import requests
from datetime import datetime, timedelta, timezone
from typing import List
import json

class TextContent:
    def __init__(self, type: str, text: str):
        self.type = type
        self.text = text

def get_prometheus_metrics_sync(metric: str = "prometheus_http_requests_total") -> List[TextContent]:
    """
    Query specified prometheus metric for last 5 minutes and return raw data

    Args:
        metric: The prometheus metric name (default: 'up')
    """
    # 修复弃用时间获取
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(minutes=5)

    url = f"http://localhost:9090/api/v1/query_range"  # 替换实际PROM_URL
    params = {
        "query": metric,
        "start": start_time.timestamp(),
        "end": end_time.timestamp(),
        "step": "15s"
    }

    try:
        resp = requests.get(url, params=params)
        resp.raise_for_status()  # 触发HTTPError异常
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

# 使用示例
if __name__ == "__main__":
    result = get_prometheus_metrics_sync()
    print(result[0].text)
