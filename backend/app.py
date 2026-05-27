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

class Chat(db.Model):

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

@app.route("/")
def home():

    return "Quantum AI Backend Running"


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

@app.route("/chat", methods=["POST"])
def chat():

    data = request.json

    message = data.get("message")
    chat_id = data.get("chat_id")
    if not message:

        return jsonify({
            "response": "No message"
        })

    db.session.add(
      Message(
    chat_id=chat_id,
    role="user",
    content=message
)
        )
    )

    db.session.commit()

history = Message.query.filter_by(
    chat_id=chat_id
).order_by(
    Message.id.desc()
).limit(10).all()

    history.reverse()

    messages = []

    for msg in history:

        messages.append({
            "role": msg.role,
            "content": msg.content
        })

    response = client.chat.completions.create(
        model="openai/gpt-4o-mini",
        messages=messages,
        stream=True
    )

    def generate():

        full_answer = ""

        for chunk in response:

            try:

                content = chunk.choices[0].delta.content

                if content:

                    full_answer += content

                    yield content

            except:

                pass

        db.session.add(
        Message(
    chat_id=chat_id,
    role="assistant",
    content=full_answer
)
            )
        )

        db.session.commit()

    return Response(
        generate(),
        mimetype="text/plain"
    )


with app.app_context():

    db.create_all()


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000
    )
