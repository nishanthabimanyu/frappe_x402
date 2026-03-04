from flask import Flask, request, jsonify
import requests
from duckduckgo_search import DDGS

app = Flask(__name__)

@app.route('/mcp/search', methods=['POST'])
def web_search():
    data = request.json
    args = data.get("arguments", {})
    query = args.get("query", "")
    
    if not query:
        return jsonify({"error": "Query is required"}), 400
        
    try:
        results = DDGS().text(query, max_results=3)
        result_text = "\n".join([f"- {r['title']}: {r['body']} ({r['href']})" for r in results])
        
        if not result_text:
            result_text = "No results found for this query."
            
        return jsonify({
            "content": [{"type": "text", "text": f"Search Results for '{query}':\n{result_text}"}]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/mcp/crypto', methods=['POST'])
def get_crypto_price():
    data = request.json
    args = data.get("arguments", {})
    coin = args.get("coin", "bitcoin").lower()
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd"
        resp = requests.get(url)
        price_data = resp.json()
        if coin in price_data:
            price = price_data[coin]['usd']
            return jsonify({"content": [{"type": "text", "text": f"Current price of {coin.capitalize()} is ${price} USD."}]})
        return jsonify({"error": "Coin not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/mcp/weather', methods=['POST'])
def get_weather():
    data = request.json
    args = data.get("arguments", {})
    location = args.get("location", "London")
    try:
        resp = requests.get(f"https://wttr.in/{location}?format=3")
        return jsonify({"content": [{"type": "text", "text": resp.text.strip()}]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/mcp/dictionary', methods=['POST'])
def get_definition():
    data = request.json
    args = data.get("arguments", {})
    word = args.get("word", "agent")
    try:
        resp = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}")
        data = resp.json()
        definition = data[0]['meanings'][0]['definitions'][0]['definition']
        return jsonify({"content": [{"type": "text", "text": f"Definition of {word}: {definition}"}]})
    except Exception as e:
        return jsonify({"error": "Word not found"}), 404

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
