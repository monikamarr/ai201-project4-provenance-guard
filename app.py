from flask import Flask, request, jsonify
from groq import Groq
from dotenv import load_dotenv
from datetime import datetime, timezone
import os
import json
import uuid

load_dotenv()

app = Flask(__name__)

LOG_FILE = "audit_log.json"
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def classify_with_groq(text):
    """
    First detection signal:
    Uses Groq LLM to return an AI-likeness score from 0.0 to 1.0.
    """

    prompt = f"""
You are an AI-content attribution assistant.

Analyze the following text and estimate whether it is human-written or AI-generated.

Return ONLY valid JSON in this exact format:
{{
  "score": 0.0,
  "attribution": "likely_human",
  "explanation": "brief explanation"
}}

Rules:
- score must be between 0.0 and 1.0
- 0.0 means strongly human-like
- 0.5 means uncertain
- 1.0 means strongly AI-like
- attribution must be one of: likely_human, uncertain, likely_ai

Text:
{text}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
    )

    raw = response.choices[0].message.content.strip()

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        result = {
            "score": 0.5,
            "attribution": "uncertain",
            "explanation": "Model response could not be parsed, so the result was marked uncertain."
        }

    score = float(result.get("score", 0.5))
    score = max(0.0, min(1.0, score))

    attribution = result.get("attribution", "uncertain")

    if attribution not in ["likely_human", "uncertain", "likely_ai"]:
        if score >= 0.7:
            attribution = "likely_ai"
        elif score <= 0.39:
            attribution = "likely_human"
        else:
            attribution = "uncertain"

    return {
        "signal": "llm",
        "score": score,
        "attribution": attribution,
        "explanation": result.get("explanation", "")
    }


def load_log():
    if not os.path.exists(LOG_FILE):
        return []

    with open(LOG_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_log(entries):
    with open(LOG_FILE, "w", encoding="utf-8") as file:
        json.dump(entries, file, indent=2)


def add_log_entry(entry):
    entries = load_log()
    entries.append(entry)
    save_log(entries)


@app.route("/submit", methods=["POST"])
def submit():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body must be JSON."}), 400

    text = data.get("text")
    creator_id = data.get("creator_id")

    if not text:
        return jsonify({"error": "Missing required field: text"}), 400

    if not creator_id:
        return jsonify({"error": "Missing required field: creator_id"}), 400

    content_id = str(uuid.uuid4())

    llm_result = classify_with_groq(text)

    confidence = llm_result["score"]

    label = (
    f"Classification: {llm_result['attribution']} "
    f"(confidence: {confidence:.2f}). "
    "Transparency labels will be expanded in Milestone 4."
    )

    response = {
        "content_id": content_id,
        "creator_id": creator_id,
        "attribution": llm_result["attribution"],
        "confidence": confidence,
        "label": label,
        "signals": {
            "llm": {
                "score": llm_result["score"],
                "explanation": llm_result["explanation"]
            }
        },
        "status": "classified"
    }

    log_entry = {
        "content_id": content_id,
        "creator_id": creator_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "attribution": llm_result["attribution"],
        "confidence": confidence,
        "llm_score": llm_result["score"],
        "status": "classified"
    }

    add_log_entry(log_entry)

    return jsonify(response), 200


@app.route("/log", methods=["GET"])
def get_log():
    entries = load_log()
    return jsonify({"entries": entries[-10:]}), 200


@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Provenance Guard API is running."})


if __name__ == "__main__":
     app.run(debug=True, port=5001)