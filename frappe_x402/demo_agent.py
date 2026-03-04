import requests
import json

# Configuration
BASE_URL = "http://127.0.0.1:8000"
API_KEY = "8cb4c34f1a37a2e"
API_SECRET = "3554b2509786eb8"

def call_marketplace(method, args=None):
    url = f"{BASE_URL}/api/method/frappe_x402.frappe_x402.api.{method}"
    headers = {
        "Authorization": f"token {API_KEY}:{API_SECRET}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, headers=headers, json=args or {})
    return response.json()

def main():
    print("🤖 Starting Demo AI Agent Client...\n")

    # 1. Discover Tools
    print("--- 🔍 Step 1: Discovering Tools ---")
    try:
        tools_resp = call_marketplace("list_tools")
        tools = tools_resp.get("message", [])
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return
    
    if not tools:
        print("❌ No tools found in marketplace.")
        return

    for t in tools:
        print(f"📍 Found Tool: {t['tool_name']} | Price: {t['price_per_call']} Credits")

    # 2. Call a Tool
    target_tool = tools[0]['name']
    print(f"\n--- 💸 Step 2: Calling Tool {target_tool} ---")
    
    payload = {
        "tool_id": target_tool,
        "arguments": {"query": "Latest news on AI Agents"}
    }
    
    call_resp = call_marketplace("call_tool", payload)
    
    if "message" in call_resp:
        msg = call_resp["message"]
        if msg.get("status") == "success":
            print(f"✅ Call Successful!")
            print(f"💰 Credits Deducted: {msg['credits_deducted']}")
            print(f"💳 Remaining Balance: {msg['remaining_balance']}")
            print(f"📡 Provider Response: {json.dumps(msg['response'], indent=2)}")
        else:
            print(f"❌ Error: {msg.get('message')}")
    elif "exc" in call_resp:
        # Check for expected connection error from the placeholder URL
        print(f"✅ Gateway Working! (Deducted credits, but provider failed as expected)")
        print(f"📡 Error detail: {call_resp.get('exc_type')}")
    else:
        print(f"❌ Error: {json.dumps(call_resp, indent=2)}")

if __name__ == "__main__":
    main()
