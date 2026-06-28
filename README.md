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

The primary detection signal uses the **Groq Llama 3.3 70B Versatile** model.

### What it measures

The LLM evaluates overall linguistic patterns such as tone, sentence structure, phrasing, consistency, and characteristics commonly associated with AI-generated writing.

### Why I chose it

An LLM can recognize broader language patterns that are difficult to capture using simple handcrafted rules, making it a strong primary detector.

### What it misses

The LLM may incorrectly classify highly polished human writing or AI-generated text that has been substantially edited by a person.

---

## Signal 2 — Stylometric Analysis

The second signal performs a lightweight statistical analysis of the writing style.

It measures:

- Average sentence length
- Sentence-length variance
- Type-token ratio (vocabulary diversity)

### Why I chose it

These metrics provide an independent signal that can either reinforce or moderate the LLM's prediction while remaining easy to interpret.

### What it misses

Stylometric statistics measure only observable writing characteristics. They cannot understand meaning, context, or author intent, and therefore should not be used as a standalone attribution method.

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

## Transparency Labels

The API returns one of three transparency label variants depending on the combined confidence score.

### High-confidence AI

```
Likely AI-generated (combined confidence: X.XX). This classification is based on a high AI-likeness score from the LLM signal, supported by stylometric analysis. The result is not final and may be appealed.
```

### High-confidence Human

```
Likely human-written (combined confidence: X.XX). This classification is based on a low AI-likeness score from the combined detection signals. The result is not final and may be appealed.
```

### Uncertain

```
Uncertain origin (combined confidence: X.XX). The detection signals did not provide enough confidence to classify the text as clearly human-written or AI-generated. Human review may be needed.
```

---

# Confidence Scoring Design

The final confidence score combines two independent detection signals.

* **80%** LLM detection score
* **20%** Stylometric heuristic score

The LLM receives the greater weight because it evaluates many linguistic patterns beyond the simple statistics captured by the stylometric detector. The stylometric analysis serves as a secondary signal that can either reinforce or slightly moderate the LLM's prediction without dominating the final decision.

This weighted approach was chosen because the LLM generally provides a stronger overall assessment while the stylometric metrics offer additional transparency into measurable characteristics of the writing.

If this system were deployed in production, I would likely replace the fixed weighting with a learned ensemble model trained on labeled examples. That approach could better calibrate confidence scores across many writing styles and domains.

## Example Confidence Scores

### High-confidence AI Example

| Metric      |               Value |
| ----------- | ------------------: |
| Attribution | Likely AI-generated |
| Confidence  |                0.68 |

### High-confidence Human Example

| Metric      |                Value |
| ----------- | -------------------: |
| Attribution | Likely human-written |
| Confidence  |                 0.16 |

These examples demonstrate that the scoring pipeline produces meaningful variation across different writing samples rather than assigning nearly identical confidence values to every submission.

---

# Architecture Design

The application separates each stage of the attribution pipeline into independent components.

1. Client submits text using the `/submit` endpoint.
2. The Groq LLM produces an AI-likeness score.
3. The stylometric analyzer computes writing-style metrics.
4. The confidence combiner merges both signals into a single confidence score.
5. A transparency label is generated based on the confidence score.
6. The classification is recorded in the structured audit log.
7. If requested, creators may submit an appeal using the `/appeal` endpoint.

This modular architecture makes it easy to improve or replace individual detection signals without changing the remainder of the application. The confidence combiner serves as a simple integration layer while preserving each individual score for transparency.

---

# Known Limitations

The current implementation combines one LLM detector with a simple stylometric heuristic.

One type of writing that may be misclassified is carefully edited academic or technical writing produced by humans. Such writing often contains long, consistent sentence structures and formal vocabulary that resemble AI-generated text, increasing both the LLM and stylometric scores.

Conversely, AI-generated text that has been extensively edited to include conversational language, varied sentence lengths, or personal experiences may receive a lower AI confidence score than expected.

The stylometric detector intentionally uses only a small number of writing statistics and does not analyze deeper linguistic features such as discourse structure, syntax, or semantic consistency.

Therefore, the system should be viewed as a decision-support tool rather than a definitive authorship detector.

---

# Specification Reflection

The project specification helped guide the implementation by dividing the system into manageable milestones. Building one detection signal at a time before combining them made the overall architecture easier to design, test, and debug.

One area where my implementation differs slightly from the specification is the appeals workflow. Rather than only updating the original classification record, the system both updates the original entry to **under_review** and creates a separate appeal event in the audit log. This preserves a complete history of actions and more closely resembles how production audit logging systems maintain traceability.

---

# AI Usage

AI tools were used throughout development as programming assistants rather than as automatic code generators.

## Example 1

I used ChatGPT to help implement the Groq API integration and the JSON parsing logic for the LLM detection signal.

After reviewing the generated code, I modified the prompt to encourage consistent JSON responses and added fallback handling for cases where the model returned invalid JSON.

## Example 2

I used ChatGPT to help implement the Flask-Limiter configuration, confidence-based transparency labels, and the appeals workflow.

After reviewing the generated code, I revised the audit logging implementation so that appeals both update the original classification entry and create a separate appeal event, providing a more complete audit trail.

Throughout the project, all AI-generated suggestions were reviewed, tested, and modified before being incorporated into the final implementation.
