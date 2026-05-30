from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from openai import OpenAI
import os

app = Flask(__name__)

CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///memory.db"

db = SQLAlchemy(app)

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

# ======================
# DATABASE MODELS
# ======================

lass Chat(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200))


class Message(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    chat_id = db.Column(
        db.Integer,
        db.ForeignKey("chat.id")
    )

    role = db.Column(db.String(20))

    content = db.Column(db.Text)

# ======================
# HOME
# ======================

@app.route("/")
def home():

    return "Quantum AI Backend Running"

# ======================
# CREATE CHAT
# ======================

@app.route("/new_chat", methods=["POST"])
def new_chat():

    chat = Chat(
        title="New Chat"
    )

    db.session.add(chat)

    db.session.commit()

    return jsonify({
        "chat_id": chat.id
    })

# ======================
# GET CHATS
# ======================

@app.route("/chats")
def get_chats():

    chats = Chat.query.all()

    result = []

    for chat in chats:

        result.append({
            "id": chat.id,
            "title": chat.title
        })

    return jsonify(result)

# ======================
# CHAT
# ======================
@app.route("/chat", methods=["POST"])
def chat():

    data = request.json

    message = data.get("message")
    chat_id = data.get("chat_id")

    chat = Chat.query.get(chat_id)

    if chat and chat.title == "New Chat":
      chat.title = message[:25] + "..." if len(message) > 25 else message
      db.session.commit()

    user_message = Message(
        chat_id=chat_id,
        role="user",
        content=message
    )

    db.session.add(user_message)
    db.session.commit()

    history = Message.query.filter_by(
        chat_id=chat_id
    ).order_by(
        Message.id.desc()
    ).limit(10).all()

    messages = []

    for msg in reversed(history):
        messages.append({
            "role": msg.role,
            "content": msg.content
        })

    try:

        response = client.chat.completions.create(
            model="openai/gpt-3.5-turbo",
            messages=messages
        )

        answer = response.choices[0].message.content

        ai_message = Message(
            chat_id=chat_id,
            role="assistant",
            content=answer
        )

        db.session.add(ai_message)
        db.session.commit()

        return answer

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


@app.route("/messages/<int:chat_id>")
def get_messages(chat_id):

    messages = Message.query.filter_by(
        chat_id=chat_id
    ).order_by(
        Message.id
    ).all()

    result = []

    for msg in messages:
        result.append({
            "role": msg.role,
            "content": msg.content
        })

    return jsonify(result)
@app.route("/delete_chat/<int:chat_id>", methods=["DELETE"])
def delete_chat(chat_id):

    Message.query.filter_by(
        chat_id=chat_id
    ).delete()

    Chat.query.filter_by(
        id=chat_id
    ).delete()

    db.session.commit()

    return jsonify({
        "success": True
    })

# ======================
# START
# ======================

with app.app_context():

    db.create_all()

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000
    )
