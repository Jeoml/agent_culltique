from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq

from dotenv import load_dotenv
load_dotenv()

import asyncio

async def main():
    client = MultiServerMCPClient(
        {
            "math":{
                "command": "python",
                "args":["mathserver.py"],
                "transport": "stdio"
            },
            "weather": {
                "url": "http://127.0.0.1:8000/mcp",
                "args":["weather.py"],
                "transport": "streamable_http"
            }
            # "product_info":{
            #     "command": "python",
            #     "args":["get_product_info.py"],
            #     "transport": "stdio"
            # },
            # "init_refund_return":{
            #     "command": "python",
            #     "args":["init_return_refund.py"],
            #     "transport": "stdio"
            # },
            # "order_status":{
            #     "command": "python",
            #     "args":["order_status.py"],
            #     "transport": "stdio"
            # },
            # "report_issue":{
            #     "command": "python",
            #     "args":["report_issue.py"],
            #     "transport": "stdio"
            # },
            # "track_shipment":{
            #     "command": "python",
            #     "args":["track_shipment.py"],
            #     "transport": "stdio"
            # }
        }
    )

    import os
    os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
    tools = await client.get_tools()
    model = ChatGroq(model = "llama-3.1-8b-instant")
    agent = create_react_agent(
        model, tools
    )

    math_response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "Whatis 2 + ? please elaborate"}]}
    )

    print("Math response:", math_response['messages'][-1].content)

    math_2_response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "sorry, I meant 2+2"}]}
    )

    print("Math 2 response:", math_2_response['messages'][-1].content)

    # while True:
    #     user_input = input("You: ")
    #     if user_input.lower() in ["exit", "quit"]:
    #         print("Exiting...")
    #         break
    #     response = await agent.ainvoke({"messages": [{"role": "user", "content": user_input}]})
    #     print("Agent:", response['messages'][-1].content)

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
    # asyncio.run(main())