from mcp.server.fastmcp import FastMCP
from typing import Dict, Any
import firebase_admin
from firebase_admin.auth import verify_id_token
from firebase_admin import auth
import requests
cred_obj = firebase_admin.credentials.Certificate('/Users/bootlabs/mcp_authorization/mcpauth-e277f-firebase-adminsdk-fbsvc-d2f8070387.json')
firebase_admin.initialize_app(cred_obj)

mcp=FastMCP(name='authorisation',port=8000,host='0.0.0.0')

@mcp.tool()
def create_users(name: str, email: str, password: str) -> Dict[str, Any]:
    try:
        user = auth.create_user(display_name=name, email=email, password=password)
        return {
            "status": "success",
            "message": f"User {user.uid} created successfully"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

# @mcp.tool()
# def login(name: str, email: str,password: str):
#     FIREBASE_API_KEY='AIzaSyA8NOsjH37GwjEsIoWkqjvswb-Qdb5i0f8'
#     url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
#     payload = {
        
#         "email": email,
#         "password": password,
#         "returnSecureToken": True
#     }
#     res = requests.post(url, json=payload)
#     data = res.json()

#     if res.status_code == 200:
#         return {'data':'login in successfully','token':data['token']}     
#     else:
#         return {"statuscode": 401, "error": data.get("error", {}).get("message", "Login failed")}
if __name__ =="__main__":
   print("Starting MCP Server....")
   mcp.run(transport="stdio")    

