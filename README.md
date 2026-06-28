# Provenance Guard

**AI201 – Project 4**

Provenance Guard is a Flask-based REST API that estimates whether submitted text is likely human-written or AI-generated. The application combines two independent detection signals—a Large Language Model (LLM) assessment and a stylometric analysis—to produce a single confidence score and attribution label. Every submission is recorded in a structured audit log for transparency and traceability.

---

# Features

* Flask REST API
* POST endpoint for submitting text
* Two independent detection signals

  * Groq Llama 3.3 70B Versatile
  * Stylometric heuristic analysis
* Combined confidence scoring
* Three attribution categories

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

## GET /log

Returns the most recent audit log entries.

Example request:

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

# Detection Pipeline

## Signal 1 — Groq LLM

The first detection signal uses the **Groq Llama 3.3 70B Versatile** model. Submitted text is analyzed by the LLM, which returns:

* AI-likeness score (0.0–1.0)
* Attribution
* Explanation

---

## Signal 2 — Stylometric Analysis

The second detection signal computes simple writing-style metrics:

* Average sentence length
* Sentence length variance
* Type-token ratio (vocabulary diversity)

These metrics are combined into a stylometric score between 0.0 and 1.0.

---

## Combined Confidence

The final confidence score combines both signals.

* **80%** LLM score
* **20%** Stylometric score

Confidence is mapped to the following labels:

| Combined Score | Attribution          |
| -------------: | -------------------- |
|         ≥ 0.60 | Likely AI-generated  |
|    0.40 – 0.59 | Uncertain            |
|         ≤ 0.39 | Likely human-written |

---

# Milestone 4 Testing

The combined detection pipeline was evaluated using four representative inputs.

---

## Test 1 — Clearly AI-generated

### Input

```text
Artificial intelligence represents a transformative paradigm shift in modern society. It is important to note that while the benefits of AI are numerous, it is equally essential to consider the ethical implications. Furthermore, stakeholders across various sectors must collaborate to ensure responsible deployment.
```

### Result

| Metric              |               Value |
| ------------------- | ------------------: |
| Attribution         | Likely AI-generated |
| LLM Score           |                0.80 |
| Stylometric Score   |                0.20 |
| Combined Confidence |                0.68 |

---

## Test 2 — Clearly Human-written

### Input

```text
ok so i finally tried that new ramen place downtown and honestly? underwhelming. the broth was fine but they put WAY too much sodium in it and i was thirsty for like three hours after. my friend got the spicy version and said it was better. probably wont go back unless someone drags me there
```

### Result

| Metric              |                Value |
| ------------------- | -------------------: |
| Attribution         | Likely human-written |
| LLM Score           |                 0.20 |
| Stylometric Score   |                 0.00 |
| Combined Confidence |                 0.16 |

---

## Test 3 — Borderline Formal Human Writing

### Input

```text
The relationship between monetary policy and asset price inflation has been extensively studied in the literature. Central banks face a fundamental tension between their mandate for price stability and the unintended consequences of prolonged low interest rates on equity and real estate valuations.
```

### Result

| Metric              |                Value |
| ------------------- | -------------------: |
| Attribution         | Likely human-written |
| LLM Score           |                 0.20 |
| Stylometric Score   |                 0.35 |
| Combined Confidence |                 0.23 |

---

## Test 4 — Borderline Edited AI Output

### Input

```text
I have been thinking a lot about remote work lately. There are genuine tradeoffs between flexibility and isolation. Studies show productivity varies widely depending on the individual, the organization, and the type of work being performed.
```

### Result

| Metric              |                Value |
| ------------------- | -------------------: |
| Attribution         | Likely human-written |
| LLM Score           |                 0.20 |
| Stylometric Score   |                 0.20 |
| Combined Confidence |                 0.20 |

---

## Discussion

The four test cases demonstrate that the combined scoring pipeline produces different confidence values for different writing styles. The clearly AI-generated example received the highest confidence score and was classified as **Likely AI-generated**, while the conversational human-written example received the lowest confidence score. The two borderline cases produced intermediate confidence values, illustrating how the stylometric heuristics influence—but do not dominate—the final decision.

---

# Project Structure

```text
.
├── app.py
├── planning.md
├── audit_log.json
├── requirements.txt
├── README.md
└── .env
```

---

## Rate Limiting

The `/submit` endpoint is protected using Flask-Limiter.

Limits:

- 10 submissions per minute
- 100 submissions per day

These limits allow normal use by individual writers while helping prevent automated abuse.

### Test Results

```text
200
200
200
200
200
200
200
200
200
200
429
429
```

The first ten requests succeeded. The final two requests exceeded the configured limit and returned HTTP 429 (Too Many Requests).