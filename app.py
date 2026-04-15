from flask import Flask, render_template, request
import json
import random

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

# Load intents
with open("intents.json", encoding="utf-8") as file:
    data = json.load(file)

# Prepare training data
patterns = []
tags = []

for intent in data["intents"]:
    for pattern in intent["patterns"]:
        patterns.append(pattern)
        tags.append(intent["tag"])

# Vectorizer
vectorizer = TfidfVectorizer()
pattern_vectors = vectorizer.fit_transform(patterns)

chat_history = []

def chatbot_response(user_input):
    user_input = user_input.lower()
    chat_history.append(user_input)

    # Convert input to vector
    input_vector = vectorizer.transform([user_input])

    # Compute similarity
    similarity = cosine_similarity(input_vector, pattern_vectors)[0]

    # Get best match
    best_index = similarity.argmax()
    best_score = similarity[best_index]
    predicted_tag = tags[best_index]

    # Logging
    with open("chat_logs.txt", "a", encoding="utf-8") as log:
        log.write(f"{user_input} | {predicted_tag} | {best_score}\n")

    # 🔥 STRICT THRESHOLD (KEY FIX)
    if best_score < 0.55:
        return "I’m sorry, I didn’t understand that.\n\nPlease ask about admissions, fees, exams, hostel, departments, or contact details."

    # 🔥 EXTRA FILTER (IMPORTANT)
    # prevents wrong answers like hostel -> fees
    keywords_map = {
        "fees": ["fee", "fees"],
        "hostel": ["hostel"],
        "admission": ["admission", "enroll", "join"],
        "exam": ["exam"],
        "library": ["library"],
        "department": ["department"],
        "contact": ["contact", "phone", "email"]
    }

    for tag, words in keywords_map.items():
        for word in words:
            if word in user_input:
                # If keyword exists but predicted tag is different → reject
                if tag != predicted_tag:
                    return "I’m not fully sure about your question.\n\nTry asking more clearly about one topic like fees, hostel, or admission."

    # Return response
    for intent in data["intents"]:
        if intent["tag"] == predicted_tag:
            return random.choice(intent["responses"])

    return "Something went wrong."


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get")
def get_response():
    msg = request.args.get("msg")
    return chatbot_response(msg)

@app.route("/history")
def history():
    return {"history": chat_history}

if __name__ == "__main__":
    app.run(debug=True)
