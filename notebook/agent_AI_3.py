from typing import TypedDict, List, Union, Sequence, Annotated
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages
from langchain_core.tracers import LangChainTracer
from langsmith import traceable
from langchain_core.tools import tool
import asyncio
import uvicorn
import uuid
import sys
import os
from dotenv import load_dotenv
import langchain
load_dotenv()

# from typing import TypedDict, List, Union, Sequence, Annotated
# from langchain_core.messages import HumanMessage, AIMessage, BaseMessage, SystemMessage
# from langgraph.graph import StateGraph, START, END
# from dotenv import load_dotenv
# from langchain_groq import ChatGroq
# from langgraph.prebuilt import ToolNode
# from langgraph.graph.message import add_messages
# from langchain_core.tracers import LangChainTracer # Not strictly needed for LangSmith tracing, but good to have
# from langsmith import traceable
# from langchain_core.tools import tool
# import asyncio
# import uvicorn
# import uuid
# import sys
# import os

load_dotenv() # Load environment variables from .env first

# --- LangChain/LangSmith Configuration ---
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY") # Assuming GROQ_API_KEY is in .env
os.environ["LANGCHAIN_TRACING_V2"] = "true" # Explicitly enable V2 tracing
os.environ["LANGCHAIN_ENDPOINT"] = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGSMITH_API_KEY")
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGSMITH_PROJECT", "default") # Use LANGCHAIN_PROJECT

langchain.debug = True
langchain.tracing_enabled = True # This is for LangChain's internal debug logging, not LangSmith directly

# Your existing code follows
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

@tool
def add(a: int, b: int) -> int:
    """Adds two numbers together."""
    return a + b

tools = [add]

model = ChatGroq(model = "meta-llama/llama-4-maverick-17b-128e-instruct").bind_tools(tools)

@traceable(name="model_call")
def model_call(state: AgentState) -> AgentState:
    system_prompt = SystemMessage(
        content="You are my AI assistant, please answer my query to the best of you ability."
    )
    response = model.invoke([system_prompt]+ state['messages'])
    return {"messages": [response]}

@traceable(name="should_continue")
def should_continue(state: AgentState):
    messages = state['messages']
    last_message = messages[-1]
    if not last_message.tool_calls:
        return "end"
    else:
        return "tools"
    
graph = StateGraph(AgentState)
tool_node = ToolNode(tools=tools)
graph.add_node("our_agent", model_call)
graph.add_node("tools", tool_node)
graph.set_entry_point("our_agent")
graph.add_conditional_edges(
    "our_agent",
    should_continue,
    {
        "tools": "tools",
        "end": END,
    },
)
graph.add_edge("tools", "our_agent")

app = graph.compile()

graph.compile()

@traceable(name="print_stream")
def print_stream(stream):
    for s in stream:
        message = s['messages'][-1]
        if isinstance(message, tuple):
            print(f"AI: {message}")
        else:
            message.pretty_print()

inputs = {"messages": [("user","What is the sum of 1 and 3?")]}

@traceable(name="LangGraphAgent")
def run_agent():
    print_stream(app.stream(inputs, stream_mode="values"))

if __name__ == "__main__":
    run_agent()