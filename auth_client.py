from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq

import asyncio
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

# Load env vars
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is not set. Please add it to your .env file.")

os.environ["GROQ_API_KEY"] = GROQ_API_KEY

model = ChatGroq(model="llama3-8b-8192", temperature=0)

app = FastAPI()

server_params = StdioServerParameters(
    command="python",
    args=["auth_server.py"]
)

class PromptRequest(BaseModel):
    user_prompt: str

@app.post("/mcp")
async def run_agent(req: PromptRequest):
    user_prompt = req.user_prompt
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("MCP Session Initialized.")

            tools = await load_mcp_tools(session)
            tool_names = [tool.name for tool in tools]
            print(f"Loaded Tools: {tool_names}")

            agent = create_react_agent(model, tools=tools)
            print("ReAct Agent Created.")
            response = await agent.ainvoke({"messages": [("user", user_prompt)]})

            print("Agent invocation complete.")
            return {"output": response["messages"][-1].content}

if __name__ == "__main__": 
    print("Starting MCP Client API...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
