from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from openai import OpenAI
import os

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///memory.db"

db = SQLAlchemy(app)
class Message(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    role = db.Column(db.String(20))

    content = db.Column(db.Text)

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
       db.session.add(
    Message(
        role="user",
        content=message
    )
)

db.session.commit()

        if not message:
            return jsonify({
                "response": "Message is empty"
            }), 400

        response = client.chat.completions.create(
            model="openai/gpt-4o-mini",
        messages=[
        history = Message.query.order_by(
    Message.id.desc()
).limit(10).all()

history.reverse()

messages = []

for msg in history:

    messages.append({
        "role": msg.role,
        "content": msg.content
    })
answer = response.choices[0].message.content

        return jsonify({
            "response": ai_response
        })

    except Exception as e:

        return jsonify({
            "response": str(e)
        }), 500

if __name__ == "__main__":
   with app.app_context():
    db.create_all()
    app.run(host="0.0.0.0", port=5000)


