from flask import Flask, render_template, request
import json
import random

app = Flask(__name__)

# Load chatbot data
with open("intents.json") as file:
    data = json.load(file)

# Chatbot response function
def chatbot_response(user_input):
    user_input = user_input.lower()

    for intent in data["intents"]:
        for pattern in intent["patterns"]:
            if pattern.lower() in user_input:
                return random.choice(intent["responses"])

    return "Sorry, I could not understand your question. You can ask about admissions, fees, exam timetable, departments, hostel facilities, library timings, or contact details."

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get")
def get_bot_response():
    userText = request.args.get('msg')
    return chatbot_response(userText)

if __name__ == "__main__":
    app.run()