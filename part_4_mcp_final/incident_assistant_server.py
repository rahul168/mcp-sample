import json
from pathlib import Path

from mcp.server.fastmcp import FastMCP

server = FastMCP("incident-assistant")

DATA_DIR = Path(__file__).resolve().parent / "data"


def _load(filename: str):
    with open(DATA_DIR / filename) as f:
        return json.load(f)


@server.tool()
def get_order(order_id: str) -> dict:
    """
    Look up an order by its ID. Returns customer, status, service, amount,
    items, created_at, and error (if the order failed).
    """
    for order in _load("orders.json"):
        if order["order_id"] == order_id:
            return order
    return {"error": f"No order found with id '{order_id}'"}


@server.tool()
def search_logs(order_id: str) -> list[dict]:
    """
    Return all log lines associated with an order ID, sorted by timestamp.
    """
    matches = [log for log in _load("logs.json") if log["order_id"] == order_id]
    matches.sort(key=lambda log: log["timestamp"])
    return matches


@server.tool()
def latest_deployment(service: str) -> dict:
    """
    Return the most recent deployment record for a given service name.
    """
    matches = [d for d in _load("deployments.json") if d["service"] == service]
    if not matches:
        return {"error": f"No deployment records found for service '{service}'"}
    return max(matches, key=lambda d: d["deployed_at"])


@server.tool()
def similar_incidents(error: str) -> list[dict]:
    """
    Search past incidents for ones whose error matches the given error
    string. Returns each match's root cause and resolution.
    """
    needle = error.lower()
    return [
        incident
        for incident in _load("incidents.json")
        if needle in incident["error"].lower() or incident["error"].lower() in needle
    ]


if __name__ == "__main__":
    print("Incident Assistant MCP server running...")
    server.run()
