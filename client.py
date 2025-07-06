from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq
import sys
import asyncio
from fastapi import FastAPI, Request
import uvicorn

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
            "order_status": {
                "command": "python",
                "args":["order_status.py"],
                "transport": "stdio"
            }
        }
    )

    import os
    os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
    tools = await client.get_tools()
    model = ChatGroq(model = "qwen/qwen3-32b") #worked well
    # model = ChatGroq(model = "gemma2-9b-it") #observer unnecessary (\n)s
    # model = ChatGroq(model = "llama-3.1-8b-instant")
    # model = ChatGroq(model = "qwen-qwq-32b")
    agent = create_react_agent(
        model, tools
    )

    app = FastAPI()

    from collections import defaultdict, deque

    conversation_histories = defaultdict(lambda: deque(maxlen=2))  # 5 user + 5 assistant

    @app.post("/ask")
    async def ask(request: Request):
        data = await request.json()
        user_message = data.get("message", "")
        session_id = data.get("101", "default")  # Optional: for multi-user support

        # Add new user message to conversation history
        conversation_histories[session_id].append({"role": "user", "content": user_message})
        print(f"Session {session_id} conversation history: {conversation_histories[session_id]}")

        # Trimmed context (last 10 messages max)
        context = list(conversation_histories[session_id])

        # Send only this trimmed context to the model
        response = await agent.ainvoke({"messages": context})
        print(f"Response from agent for session {session_id}: {response['messages'][-1].content}")

        # Add assistant's reply to history
        assistant_reply = response['messages'][-1].content
        conversation_histories[session_id].append({"role": "assistant", "content": assistant_reply})
        print(f"Updated conversation history for session {session_id}: {conversation_histories[session_id]}")

        return {"response": assistant_reply}


    # Run FastAPI app
    config = uvicorn.Config(app=app, host="127.0.0.1", port=8080, loop="asyncio")
    server = uvicorn.Server(config)
    await server.serve()

    # order_status_response = await agent.ainvoke(
    #     {"messages": [{"role": "user", "content": "order status for my order whose order id is 10"}]},
    # )

    # print("order status response:", order_status_response['messages'][-1].content)

    # while True:
    #     user_input = input("You: ")
    #     if user_input.lower() in ["exit", "quit"]:
    #         print("Exiting...")
    #         break
    #     response = await agent.ainvoke({"messages": [{"role": "user", "content": user_input}]})
    #     print("Agent:", response['messages'][-1].content)

if __name__ == "__main__":
    import sys
    if sys.platform.startswith("win") and sys.version_info >= (3, 8):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())