from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os

app = Flask(__name__)

# Разрешаем запросы от приложения
CORS(app)

# OpenRouter API
client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

@app.route("/")
def home():
    return "Quantum AI Backend Working"

@app.route("/chat", methods=["POST"])
def chat():

    try:

        data = request.json

        if not data:
            return jsonify({
                "response": "No JSON received"
            }), 400

        message = data.get("message")

        if not message:
            return jsonify({
                "response": "Message is empty"
            }), 400

        response = client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": message
                }
            ]
        )

        ai_response = response.choices[0].message.content

        return jsonify({
            "response": ai_response
        })

    except Exception as e:

        return jsonify({
            "response": str(e)
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
