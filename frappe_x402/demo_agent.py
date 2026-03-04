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
    print("🤖 Starting Multi-Tool Agent Demo (Web Search Edition)...\n")

    # 1. Discover Tools
    tools_resp = call_marketplace("list_tools")
    tools = tools_resp.get("message", [])
    if not tools:
        print("❌ No tools found.")
        return

    # 2. Call Web Search
    target_tool_name = "Web Search"
    tool_id = next((t['name'] for t in tools if t['tool_name'] == target_tool_name), None)
    
    if tool_id:
        print(f"--- 💸 Calling: {target_tool_name} ---")
        payload = {
            "tool_id": tool_id, 
            "arguments": {"query": "What is Frappe Framework?"}
        }
        
        try:
            resp = call_marketplace("call_tool", payload)
            msg = resp.get("message", {})
            
            if msg.get("status") == "success":
                print(f"✅ Success!")
                print(f"📡 Data: {msg['response']['content'][0]['text']}")
                print(f"💳 Remaining: {msg['remaining_balance']} Credits\n")
            else:
                print(f"❌ API Error: {msg.get('message')}\n")
        except Exception as e:
            print(f"❌ Request Failed: {e}\n")
    else:
        print(f"❌ Tool '{target_tool_name}' not found.")

if __name__ == "__main__":
    main()
