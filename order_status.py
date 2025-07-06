from fastmcp import FastMCP
import requests

mcp = FastMCP()

@mcp.tool()
def order_status(prod_id: str) -> str:
    """Get the status of an order by its ID (e.g. 10, 25, etc). Do not try any other number than the number provided to you by the client. If someone is complaining about status of order and do not provide the order id then ask them for the order id"""

    try:
        response = requests.get(
            f"http://127.0.0.1:8001/order-status/{prod_id}",
            headers={"Accept": "application/json"}
        )

        if response.status_code == 404:
            # 🚨 CLEAR, FINAL LANGUAGE THAT STOPS REASONING
            return (
                f"❌ No order found with ID {prod_id}. "
                "Please double-check the ID and try again. "
                "This order does not exist in our system."
            )

        response.raise_for_status()
        data = response.json()

        status = data.get("status")
        if status:
            return f"✅ Order ID {prod_id} is currently '{status}'."
        else:
            return f"ℹ️ Order ID {prod_id} was found, but its status is not available."

    except Exception as e:
        return f"⚠️ Error while checking order {prod_id}: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="stdio")