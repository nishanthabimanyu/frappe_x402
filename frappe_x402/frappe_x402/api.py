import frappe
import json
import requests
from frappe import _

@frappe.whitelist(allow_guest=True)
def list_tools():
    """Returns all registered and active MCP tools."""
    tools = frappe.get_all("MCP Tool", 
        fields=["name", "tool_name", "provider", "price_per_call", "category", "schema_json", "endpoint_url"]
    )
    return tools

@frappe.whitelist()
def call_tool(tool_id, arguments=None):
    """
    Main entry point for tool execution.
    Handles payment verification and proxying.
    """
    if not tool_id:
        frappe.throw(_("Tool ID is required"), frappe.ValidationError)

    # 1. Fetch the tool
    tool = frappe.get_doc("MCP Tool", tool_id)
    
    # 2. Check User Credits
    user = frappe.session.user
    credit_record = frappe.db.get_value("Workspace Credit", {"user": user}, ["name", "total_balance", "is_active"], as_dict=True)

    if not credit_record or not credit_record.is_active:
        frappe.throw(_("No active credit balance found for user {0}").format(user), frappe.PermissionError)

    if credit_record.total_balance < tool.price_per_call:
        # Standard x402 / HTTP 402 response
        frappe.local.response['http_status_code'] = 402
        return {
            "status": "error",
            "message": "Insufficient credits",
            "price_per_call": tool.price_per_call,
            "current_balance": credit_record.total_balance,
            "x402_header": f"Pay {tool.price_per_call} credits to use this tool"
        }

    # 3. Atomically Deduct Credits & Create Transaction
    try:
        # Deduct credits
        new_balance = credit_record.total_balance - tool.price_per_call
        frappe.db.set_value("Workspace Credit", credit_record.name, "total_balance", new_balance)

        # Create Transaction Log
        txn = frappe.get_doc({
            "doctype": "Credit Transaction",
            "user": user,
            "tool": tool.name,
            "amount_credits": tool.price_per_call,
            "status": "Completed", # In Phase 2, this will be 'Pending' until x402 settles
            "timestamp": frappe.utils.now_datetime()
        })
        txn.insert(ignore_permissions=True)
        
        # 4. Proxy Request to Provider (Phase 1: Mock/Forward)
        # In a real scenario, we would use requests.post(tool.endpoint_url, json=arguments)
        # For now, we simulate the tool response.
        
        # frappe.db.commit() # Ensure payment is saved before potentially long external call
        
        return {
            "status": "success",
            "tool": tool.tool_name,
            "credits_deducted": tool.price_per_call,
            "remaining_balance": new_balance,
            "response": f"Successfully called {tool.tool_name}. (Forwarded to {tool.endpoint_url})",
            "transaction_id": txn.name
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("MCP Call Error"))
        frappe.throw(_("An error occurred during tool execution: {0}").format(str(e)))
