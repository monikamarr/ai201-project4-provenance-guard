# ai201-project4-provenance-guard# Provenance Guard

**AI201 – Project 4**

Provenance Guard is a Flask-based REST API that analyzes submitted text and estimates whether it is likely human-written or AI-generated. The application uses the Groq API (Llama 3.3 70B Versatile) as its first detection signal and maintains a structured audit log for transparency.

---

# Features

* REST API built with Flask
* POST endpoint for text submission
* Groq LLM-based attribution detection
* Unique content ID generated for every submission
* Confidence score and attribution result returned
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

Create a virtual environment.

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

The server runs on:

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

Accepts submitted text and returns an attribution assessment.

### Required JSON Fields

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
"text":"In conclusion, artificial intelligence offers numerous benefits across multiple sectors, including healthcare, education, finance, and transportation. By leveraging advanced algorithms, organizations can optimize workflows, enhance productivity, and drive innovation in an increasingly competitive global landscape.",
"creator_id":"test-ai-1"
}' | python -m json.tool
```

### Example Response

```json
{
    "attribution": "likely_ai",
    "confidence": 0.8,
    "content_id": "01ffbd56-d55e-4635-9a0e-bbc55905a717",
    "creator_id": "test-ai-1",
    "label": "Classification: likely_ai (confidence: 0.80). Transparency labels will be expanded in Milestone 4.",
    "signals": {
        "llm": {
            "score": 0.8,
            "explanation": "The writing is highly structured, generic, and exhibits characteristics commonly associated with AI-generated text."
        }
    },
    "status": "classified"
}
```

---

# Audit Log

Each submission is written to `audit_log.json`.

Each log entry contains:

* content ID
* creator ID
* timestamp
* attribution result
* confidence score
* LLM score
* classification status

Retrieve recent entries using:

```bash
curl -s http://localhost:5001/log | python -m json.tool
```

Example output:

```json
{
    "entries": [
        {
            "attribution": "likely_human",
            "confidence": 0.2,
            "content_id": "7cc46cc4-382c-4129-a197-3b2b9ecd450b",
            "creator_id": "test-user-1",
            "llm_score": 0.2,
            "status": "classified",
            "timestamp": "2026-06-28T18:57:52.882382+00:00"
        },
        {
            "attribution": "likely_human",
            "confidence": 0.2,
            "content_id": "8c2a5a57-1657-4c00-9fbe-265ecc0a253a",
            "creator_id": "test-user-2",
            "llm_score": 0.2,
            "status": "classified",
            "timestamp": "2026-06-28T19:02:32.934012+00:00"
        },
        {
            "attribution": "likely_human",
            "confidence": 0.0,
            "content_id": "a41d3d2c-b88b-4d6b-8dc4-9542478e2698",
            "creator_id": "test-user-3",
            "llm_score": 0.0,
            "status": "classified",
            "timestamp": "2026-06-28T19:02:49.727146+00:00"
        },
        {
            "attribution": "likely_ai",
            "confidence": 0.8,
            "content_id": "01ffbd56-d55e-4635-9a0e-bbc55905a717",
            "creator_id": "test-ai-1",
            "llm_score": 0.8,
            "status": "classified",
            "timestamp": "2026-06-28T19:08:34.618078+00:00"
        }
    ]
}
```

---

# Detection Signal

The first detection signal uses the **Groq Llama 3.3 70B Versatile** model.

The submitted text is sent to the model with a prompt requesting structured JSON output containing:

* AI-likeness score (0.0–1.0)
* attribution (`likely_human`, `uncertain`, or `likely_ai`)
* explanation

The application parses the JSON response and includes the results in both the API response and the audit log.

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

# Current Progress

Completed:

* ✅ Planning document
* ✅ Flask application
* ✅ POST `/submit`
* ✅ GET `/log`
* ✅ Groq LLM detection signal
* ✅ Structured JSON responses
* ✅ JSON audit logging

Upcoming milestones:

* Transparency labels
* Second detection signal
* Appeal endpoint
* Final documentation and testing

