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
from mcp.server.fastmcp import FastMCP
from typing import Dict, Any
import firebase_admin
from firebase_admin.auth import verify_id_token
from firebase_admin import auth
import requests
from fastapi.requests import Request
from fastapi.responses import Response
from fastapi import HTTPException
cred_obj = firebase_admin.credentials.Certificate('/Users/bootlabs/mcp_authorization/mcpauth-e277f-firebase-adminsdk-fbsvc-d2f8070387.json')
firebase_admin.initialize_app(cred_obj)

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
os.environ["GROQ_API_KEY"] = GROQ_API_KEY

model = ChatGroq(model="llama3-8b-8192", temperature=0)

app = FastAPI()

server_params = StdioServerParameters(
    command="python",
    args=["auth_server.py"]
)

class PromptRequest(BaseModel):
    user_prompt: str

class usermodel(BaseModel):
    name:str
    email:str
    password:str  

class loginmodel(BaseModel):
    email:str
    password:str      


@app.post('/createuser')
def create_user(user:usermodel):
    try:
        user = auth.create_user(display_name=user.name, email=user.email, password=user.password)
        return {
                "status": "success",
                "message": f"User {user.uid} created successfully"
            } 
    except Exception as err:
        return {
            "status":'error due to {err}'
        }

@app.post('/login')
def login(user:loginmodel,response:Response):
     FIREBASE_API_KEY='AIzaSyA8NOsjH37GwjEsIoWkqjvswb-Qdb5i0f8'
     url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
     payload = {
        
        "email": user.email,
        "password": user.password,
        "returnSecureToken": True
    }
     res = requests.post(url, json=payload)
     data = res.json()
     print(data)
     response.set_cookie('token',data['idToken'])
     if res.status_code == 200:
         return {'data':'login in successfully'}     
     else:
        return {"statuscode": 401, "error": data.get("error", {}).get("message", "Login failed")}       

@app.post("/mcp")
async def run_agent(req: PromptRequest, request: Request):
    user_prompt = req.user_prompt
    token = request.cookies.get("token")

    if not token:
        raise HTTPException(status_code=401, detail="Missing authentication token")

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("MCP Session Initialized.")
            tools = await load_mcp_tools(session)
            tool_names = [tool.name for tool in tools]
            print(f"Loaded Tools: {tool_names}")

            agent = create_react_agent(model, tools=tools)
            print("ReAct Agent Created.")

            response = await agent.ainvoke({
                "messages": [("user", user_prompt)],
                "config": {},
                "token": token  # directly pass token
            })

            print("Agent invocation complete.")
            return {"output": response["messages"][-1].content}

if __name__ == "__main__": 
    print("Starting MCP Client API...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
