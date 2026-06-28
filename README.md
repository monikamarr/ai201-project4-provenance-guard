# Provenance Guard

**AI201 – Project 4**

Provenance Guard is a Flask-based REST API that estimates whether submitted text is likely human-written or AI-generated. The system combines two independent detection signals—a large language model (LLM) assessment and a stylometric analysis—to produce a single confidence score and attribution label. Every submission is recorded in a structured audit log for transparency.

---

# Features

* Flask REST API
* POST endpoint for text attribution
* Two independent detection signals:

  * **Groq Llama 3.3 70B Versatile**
  * **Stylometric heuristic analysis**
* Combined confidence scoring
* Three attribution categories:

  * Likely AI-generated
  * Uncertain
  * Likely human-written
* Structured JSON audit log
* Endpoint to retrieve recent audit log entries

---

# Technologies

* Python 3
* Flask
* Groq API
* python-dotenv
* JSON

---

# Installation

Clone the repository.

```bash
git clone <repository-url>
cd ai201-project4-provenance-guard
```

Create and activate a virtual environment.

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies.

```bash
pip install -r requirements.txt
```

Create a `.env` file.

```text
GROQ_API_KEY=your_groq_api_key
```

Run the application.

```bash
python app.py
```

The server runs at:

```
http://localhost:5001
```

---

# API Endpoints

## GET /

Health check endpoint.

### Response

```json
{
    "message": "Provenance Guard API is running."
}
```

---

## POST /submit

Submits text for attribution analysis.

### Required JSON

| Field      | Type   |
| ---------- | ------ |
| text       | string |
| creator_id | string |

---

## Example Request

```bash
curl -s -X POST http://localhost:5001/submit \
-H "Content-Type: application/json" \
-d '{
"text":"Artificial intelligence represents a transformative paradigm shift in modern society. It is important to note that while the benefits of AI are numerous, it is equally essential to consider the ethical implications. Furthermore, stakeholders across various sectors must collaborate to ensure responsible deployment.",
"creator_id":"test-ai-1"
}' | python -m json.tool
```

### Example Response

```json
{
    "content_id": "230a5bc1-b733-4266-9360-8bb1c4d391f2",
    "creator_id": "test-ai-1",
    "attribution": "likely_ai",
    "confidence": 0.68,
    "label": "Likely AI-generated (combined confidence: 0.68). This result is based on an LLM signal and a stylometric signal.",
    "signals": {
        "llm": {
            "score": 0.8,
            "attribution": "likely_ai"
        },
        "stylometric": {
            "score": 0.2
        }
    },
    "status": "classified"
}
```

---

# Detection Pipeline

## Signal 1 — Groq LLM

The first detection signal uses the **Groq Llama 3.3 70B Versatile** model.

The model receives submitted text and returns:

* AI-likeness score
* attribution
* explanation

---

## Signal 2 — Stylometric Analysis

The second signal computes writing-style metrics including:

* Average sentence length
* Sentence length variance
* Type-token ratio (vocabulary diversity)

These metrics are combined into a stylometric score between **0.0** and **1.0**.

---

## Combined Confidence

The final confidence score combines both signals:

* **80%** LLM score
* **20%** stylometric score

Final labels are assigned using the combined confidence:

| Confidence | Attribution          |
| ---------- | -------------------- |
| ≥ 0.60     | Likely AI-generated  |
| 0.40–0.59  | Uncertain            |
| ≤ 0.39     | Likely human-written |

---

# Audit Log

Every submission creates a structured audit record containing:

* content ID
* creator ID
* timestamp
* attribution
* combined confidence
* LLM score
* stylometric score
* stylometric metrics
* classification status

Retrieve the log with:

```bash
curl -s http://localhost:5001/log | python -m json.tool
```

Example audit entry:

```json
{
    "attribution": "likely_ai",
    "confidence": 0.68,
    "content_id": "230a5bc1-b733-4266-9360-8bb1c4d391f2",
    "creator_id": "test-ai-1",
    "llm_score": 0.8,
    "stylometric_score": 0.2,
    "stylometric_metrics": {
        "avg_sentence_length": 14.33,
        "sentence_length_variance": 44.33,
        "type_token_ratio": 0.88
    },
    "status": "classified"
}
```

---

# Testing

The detection pipeline was evaluated using four representative inputs.

| Test Case                 | Expected Result     | Observed Result     |
| ------------------------- | ------------------- | ------------------- |
| Clearly AI-generated      | High confidence AI  | Likely AI (0.68)    |
| Clearly human-written     | Low confidence      | Likely human (0.16) |
| Borderline formal writing | Moderate confidence | Likely human (0.23) |
| Borderline edited AI      | Moderate confidence | Likely human (0.20) |

These tests demonstrate that both detection signals execute successfully and produce different confidence scores across a range of writing styles.

---

# Project Structure

```
.
├── app.py
├── planning.md
├── audit_log.json
├── requirements.txt
├── README.md
└── .env
```

---

# Milestone Progress

Completed:

* ✅ Planning document
* ✅ Flask application
* ✅ POST `/submit`
* ✅ GET `/log`
* ✅ Groq LLM detection signal
* ✅ Stylometric detection signal
* ✅ Combined confidence scoring
* ✅ Structured JSON audit logging
* ✅ Four test cases covering AI, human, and borderline inputs

Upcoming work:

* Appeal endpoint
* Final transparency features
* Final documentation


