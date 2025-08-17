from mcp.server.fastmcp import FastMCP
from firebase_admin import auth, credentials, initialize_app
from firebase_admin.auth import verify_id_token

import firebase_admin
cred_obj = firebase_admin.credentials.Certificate('/Users/bootlabs/mcp_authorization/mcpauth-e277f-firebase-adminsdk-fbsvc-d2f8070387.json')
firebase_admin.initialize_app(cred_obj)

# Create MCP Server on a separate port (e.g., 5000)
mcp = FastMCP(name='auth_tools', port=5000, host='0.0.0.0')

@mcp.tool()
def adding(a: int, b: int, *, token: str):
    from firebase_admin.auth import verify_id_token
    try:
        verified = verify_id_token(token)
        if verified:
            return a + b
        else:
            return {"unauthorized": True}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    print("Starting MCP Server on port 5000...")
    mcp.run(transport="stdio")
