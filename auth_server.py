from mcp.server.fastmcp import FastMCP
import os
import firebase_admin
cred_obj = firebase_admin.credentials.Certificate(os.getenv('FIREBASE_SECURITY_FILE_PATH'))
firebase_admin.initialize_app(cred_obj)
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
