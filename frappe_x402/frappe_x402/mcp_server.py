import frappe
import json
from frappe import _

def get_mcp_server():
    """Initializes and returns the MCP server with dynamic tool discovery."""
    try:
        from mcp.server import Server
        import mcp.types as types
    except ImportError:
        frappe.throw(_("MCP SDK not found. Please install with 'pip install mcp'"))

    server = Server("frappe-x402-marketplace")

    @server.list_tools()
    async def handle_list_tools() -> list[types.Tool]:
        """Dynamically list tools from the Frappe database."""
        tools = frappe.get_all("MCP Tool", fields=["tool_name", "schema_json"])
        mcp_tools = []
        
        for t in tools:
            schema = json.loads(t.schema_json or '{}')
            mcp_tools.append(types.Tool(
                name=t.tool_name.replace(" ", "_"),
                description=schema.get("description", f"AI Tool: {t.tool_name}"),
                inputSchema=schema.get("input_schema", {"type": "object", "properties": {}})
            ))
        return mcp_tools

    @server.call_tool()
    async def handle_call_tool(name: str, arguments: dict | None) -> list[types.TextContent]:
        """Intercept call, deduct credits, and execute tool."""
        # Find the tool in DB
        frappe_tool_name = name.replace("_", " ")
        tool_id = frappe.db.get_value("MCP Tool", {"tool_name": frappe_tool_name}, "name")
        
        if not tool_id:
            raise ValueError(f"Tool {name} not found in marketplace.")

        # Use our existing monetized API logic
        from frappe_x402.frappe_x402.api import call_tool
        result = call_tool(tool_id=tool_id, arguments=arguments)
        
        if result.get("status") == "success":
            # Format real tool response for MCP
            provider_resp = result.get("response", {})
            text = ""
            if isinstance(provider_resp, dict) and "content" in provider_resp:
                text = provider_resp["content"][0].get("text", "")
            else:
                text = str(provider_resp)
                
            return [types.TextContent(type="text", text=text)]
        else:
            return [types.TextContent(type="text", text=f"Error: {result.get('message')}")]

    return server

@frappe.whitelist()
def handle_sse():
    """
    Experimental SSE endpoint for Claude Desktop.
    Wraps the MCP server logic into a streamable HTTP response.
    """
    # This requires an SSE transport adapter for Frappe
    # In Phase 1, we provide the logic. In Phase 2, we implement the full SSE stream.
    return {"message": "MCP Server logic initialized. SSE Transport pending."}
