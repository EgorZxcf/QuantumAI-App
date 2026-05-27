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

class Message(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    role = db.Column(db.String(20))

    content = db.Column(db.Text)


@app.route("/")
def home():

    return "Quantum AI Backend Running"


@app.route("/chat", methods=["POST"])
def chat():

    data = request.json

    message = data.get("message")

    if not message:

        return jsonify({
            "response": "No message"
        })

    db.session.add(
        Message(
            role="user",
            content=message
        )
    )

    db.session.commit()

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
                role="assistant",
                content=full_answer
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
