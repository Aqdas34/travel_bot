from flask import Flask, render_template, request, jsonify
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from spacy_chatbot import main as spacy_main

app = Flask(__name__)

# Session context for each user (simple demo, not persistent)
session = spacy_main.Session()

def get_bot_reply(user_message):
    intent, entities = spacy_main.parse_message(user_message)
    reply = spacy_main.generate_reply(intent, entities, user_message)
    return reply

@app.route("/")
def index():
    return render_template("flask_chat.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "")
    bot_reply = get_bot_reply(user_message)
    return jsonify({"reply": bot_reply})

if __name__ == "__main__":
    app.run(debug=True) 