from flask import Flask, render_template, request, jsonify
import requests
import json
app = Flask(__name__)

# Ollama API endpoint
OLLAMA_URL = "http://localhost:11434/api/chat"

# Customer Service System Prompt
system_prompt = (
    "You are a professional and friendly customer service assistant.\n"
    "Always greet users politely.\n"
    "Help users solve their problems accurately and efficiently.\n"
    "If you don't know an answer, apologize and offer to escalate the issue.\n"
    "Use a warm, helpful, and positive tone.\n"
    "Keep responses short, clear, and easy to understand."
)

# This will store the conversation history
conversation = [
    {"role": "system", "content": system_prompt}
]

@app.route("/")
def index():
    return render_template("chat.html")

@app.route("/send", methods=["POST"])
def send():
    user_message = request.json["message"]

    conversation.append({"role": "user", "content": user_message})

    payload = {
        "model": "deepseek-llm:latest",
        "messages": conversation
    }

    response = requests.post(OLLAMA_URL, json=payload, stream=True)

    if response.ok:
        # Streaming response handling
        bot_message = ""
        for line in response.iter_lines(decode_unicode=True):
            if line:
                try:
                    part = json.loads(line)
                    bot_message += part.get("message", {}).get("content", "")
                except Exception:
                    pass

        conversation.append({"role": "assistant", "content": bot_message})

        return jsonify({"reply": bot_message})
    else:
        return jsonify({"reply": "❌ Error contacting Ollama."})


if __name__ == "__main__":
    app.run(debug=True)
