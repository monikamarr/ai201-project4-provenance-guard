from flask import Flask, request, jsonify
from groq import Groq
from dotenv import load_dotenv
from datetime import datetime, timezone
import os
import json
import uuid
import re
import statistics

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


def stylometric_signal(text):
    """
    Second detection signal:
    Uses simple writing-style metrics to estimate AI-likeness.
    Higher score = more AI-like.
    """

    sentences = re.split(r"[.!?]+", text)
    sentences = [s.strip() for s in sentences if s.strip()]

    words = re.findall(r"\b\w+\b", text.lower())

    if not words or not sentences:
        return {
            "signal": "stylometric",
            "score": 0.5,
            "metrics": {},
            "explanation": "Not enough text to compute stylometric metrics."
        }

    sentence_lengths = [
        len(re.findall(r"\b\w+\b", sentence))
        for sentence in sentences
    ]

    avg_sentence_length = sum(sentence_lengths) / len(sentence_lengths)

    if len(sentence_lengths) > 1:
        sentence_length_variance = statistics.variance(sentence_lengths)
    else:
        sentence_length_variance = 0

    unique_words = set(words)
    type_token_ratio = len(unique_words) / len(words)

    score = 0

    if avg_sentence_length >= 18:
        score += 0.35
    elif avg_sentence_length >= 12:
        score += 0.2

    if sentence_length_variance <= 10:
        score += 0.35
    elif sentence_length_variance <= 25:
        score += 0.2

    if type_token_ratio <= 0.55:
        score += 0.3
    elif type_token_ratio <= 0.7:
        score += 0.15

    score = max(0.0, min(1.0, score))

    return {
        "signal": "stylometric",
        "score": round(score, 2),
        "metrics": {
            "avg_sentence_length": round(avg_sentence_length, 2),
            "sentence_length_variance": round(sentence_length_variance, 2),
            "type_token_ratio": round(type_token_ratio, 2)
        },
        "explanation": "Score based on sentence length, sentence variation, and vocabulary diversity."
    }


def combine_signals(llm_score, stylometric_score):
    """
    Combines both signals into one confidence score.
    LLM signal is weighted more heavily because it is the primary detector.
    """

    combined_score = (0.8 * llm_score) + (0.2 * stylometric_score)
    combined_score = round(combined_score, 2)

    if combined_score >= 0.6:
        attribution = "likely_ai"
        label = "Likely AI-generated"
    elif combined_score <= 0.39:
        attribution = "likely_human"
        label = "Likely human-written"
    else:
        attribution = "uncertain"
        label = "Uncertain origin"

    return {
        "confidence": combined_score,
        "attribution": attribution,
        "label": label
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

    if not text or not text.strip():
        return jsonify({"error": "Missing required field: text"}), 400

    if not creator_id:
        return jsonify({"error": "Missing required field: creator_id"}), 400

    content_id = str(uuid.uuid4())

    try:
        llm_result = classify_with_groq(text)
    except Exception as e:
        llm_result = {
            "signal": "llm",
            "score": 0.5,
            "attribution": "uncertain",
            "explanation": f"LLM signal failed: {str(e)}"
        }

    stylometric_result = stylometric_signal(text)

    combined_result = combine_signals(
        llm_result["score"],
        stylometric_result["score"]
    )

    confidence = combined_result["confidence"]
    attribution = combined_result["attribution"]

    label = (
        f"{combined_result['label']} "
        f"(combined confidence: {confidence:.2f}). "
        "This result is based on an LLM signal and a stylometric signal."
    )

    response = {
        "content_id": content_id,
        "creator_id": creator_id,
        "attribution": attribution,
        "confidence": confidence,
        "label": label,
        "signals": {
            "llm": {
                "score": llm_result["score"],
                "attribution": llm_result["attribution"],
                "explanation": llm_result["explanation"]
            },
            "stylometric": {
                "score": stylometric_result["score"],
                "metrics": stylometric_result["metrics"],
                "explanation": stylometric_result["explanation"]
            }
        },
        "status": "classified"
    }

    log_entry = {
        "content_id": content_id,
        "creator_id": creator_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "attribution": attribution,
        "confidence": confidence,
        "llm_score": llm_result["score"],
        "stylometric_score": stylometric_result["score"],
        "stylometric_metrics": stylometric_result["metrics"],
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