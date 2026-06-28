# Provenance Guard - Planning

## Project Overview

Provenance Guard is a text attribution API for a writing platform. It analyzes submitted text and estimates whether the content is likely human-written, likely AI-generated, or uncertain. The system does not claim perfect detection. Instead, it combines multiple signals, produces a confidence score, shows a plain-language transparency label, logs every decision, and gives creators a way to appeal classifications.

---

## 1. Detection Signals

The system will use two independent detection signals.

---

### Signal 1: LLM-Based Classification

**Component:** Groq API using `llama-3.3-70b-versatile`

**What it measures:**
This signal asks an LLM to evaluate whether the submitted text appears more likely to be AI-generated or human-written. It looks at overall coherence, phrasing, structure, tone, repetition, and stylistic patterns.

**Why it is useful:**
An LLM can notice broad semantic and stylistic patterns that are hard to capture with simple rules.

**Output format:**

```json
{
  "signal": "llm",
  "score": 0.82,
  "explanation": "The text has highly polished structure and consistent phrasing."
}
```

The `score` is a number from `0.0` to `1.0`.

* `0.0` means strongly human-like
* `0.5` means uncertain
* `1.0` means strongly AI-like

**Blind spots:**

* Polished human writing may be mistaken for AI.
* AI text that has been edited by a human may look human.
* The result depends on prompt quality.
* The model may overstate confidence.

---

### Signal 2: Stylometric Heuristics

**Component:** Pure Python text analysis

**What it measures:**
This signal calculates measurable writing statistics:

* Average sentence length
* Sentence length variance
* Vocabulary diversity / type-token ratio
* Punctuation density
* Repetition rate

**Why it is useful:**
AI-generated writing often has smoother sentence patterns, more consistent structure, and less natural variation. Human writing often contains more irregularity, varied sentence length, and less predictable vocabulary use.

**Output format:**

```json
{
  "signal": "stylometric",
  "score": 0.61,
  "features": {
    "average_sentence_length": 18.4,
    "sentence_length_variance": 6.2,
    "type_token_ratio": 0.48,
    "punctuation_density": 0.04,
    "repetition_rate": 0.12
  }
}
```

The `score` is a number from `0.0` to `1.0`.

* `0.0` means strongly human-like
* `0.5` means uncertain
* `1.0` means strongly AI-like

**Blind spots:**

* Short text may not provide enough data.
* Poems and experimental writing may confuse the statistics.
* Professional human writing may look very polished and uniform.
* Edited AI writing may show human-like variation.

---

### Signal Combination

The two signal scores will be combined using weighted averaging.

```text
combined_score = (llm_score * 0.70) + (stylometric_score * 0.30)
```

The LLM signal receives more weight because it can evaluate meaning, tone, and style holistically. The stylometric signal receives less weight but is still important because it provides a separate structural measurement.

Example:

```text
llm_score = 0.80
stylometric_score = 0.60

combined_score = (0.80 * 0.70) + (0.60 * 0.30)
combined_score = 0.74
```

Final confidence score:

```text
0.74 = Likely AI
```

---

## 2. Uncertainty Representation

The confidence score represents how AI-like the content appears after combining all detection signals.

A score of `0.6` means the system sees some AI-like patterns, but not enough evidence to confidently classify the text as AI-generated. In this system, `0.6` falls into the uncertain range.

The system avoids treating `0.5` as a simple binary cutoff. Instead, it uses ranges so that uncertainty is visible to users.

---

### Confidence Thresholds

| Combined Score | Classification        |
| -------------- | --------------------- |
| `0.85 - 1.00`  | High-confidence AI    |
| `0.70 - 0.84`  | Likely AI             |
| `0.40 - 0.69`  | Uncertain             |
| `0.15 - 0.39`  | Likely Human          |
| `0.00 - 0.14`  | High-confidence Human |

---

### Why the Uncertain Range Is Wide

The uncertain range is intentionally wide because a false positive is especially harmful on a writing platform. Incorrectly labeling a human creator's work as AI-generated could damage trust, reputation, or creative ownership.

When the system is not confident, it should say so clearly instead of forcing a binary answer.

---

### Calibration Plan

Raw signal outputs will be mapped into the final combined score using the weighted formula above. The system will be tested using sample inputs:

1. Clearly AI-generated paragraph
2. Clearly human personal reflection
3. Short poem
4. Formal academic-style paragraph
5. Edited or polished blog post

The goal is not perfect detection. The goal is that scores vary meaningfully:

* Clearly AI-like text should score closer to `0.80 - 1.00`
* Clearly human-like text should score closer to `0.00 - 0.30`
* Ambiguous text should land in the `0.40 - 0.69` uncertain range

---

## 3. Transparency Label Design

The platform will show one of three main transparency label variants to readers.

These exact label texts will be implemented in the code and included in the README.

---

### High-Confidence AI Label

> "High-confidence AI label: This content appears likely to be AI-generated. Our system found strong AI-like patterns, but this result is not a final judgment and may be appealed by the creator."

---

### High-Confidence Human Label

> "High-confidence human label: This content appears likely to be human-written. Our system found strong human-like writing patterns, though no automated system can verify authorship with certainty."

---

### Uncertain Label

> "Uncertain label: Our system cannot confidently determine whether this content was written by a human or generated by AI. This content should not be treated as definitively AI-generated or definitively human-written."

---

### Label Mapping

| Classification        |   Score Range | Label Used                                                    |
| --------------------- | ------------: | ------------------------------------------------------------- |
| High-confidence AI    | `0.85 - 1.00` | High-confidence AI label                                      |
| Likely AI             | `0.70 - 0.84` | High-confidence AI label with lower confidence score shown    |
| Uncertain             | `0.40 - 0.69` | Uncertain label                                               |
| Likely Human          | `0.15 - 0.39` | High-confidence human label with lower confidence score shown |
| High-confidence Human | `0.00 - 0.14` | High-confidence human label                                   |

---

## 4. Appeals Workflow

Creators can appeal a classification if they believe the system made an incorrect decision.

---

### Who Can Submit an Appeal?

For this project, any creator with a valid `content_id` can submit an appeal. Authentication is not required for the prototype, but the system is designed as if the creator owns the submitted content.

---

### Appeal Request

Endpoint:

```text
POST /appeal
```

Request body:

```json
{
  "content_id": 1,
  "creator_name": "Example Creator",
  "reason": "I wrote this piece myself and can provide drafts if needed."
}
```

---

### What the System Does

When an appeal is received, the system will:

1. Validate that the `content_id` exists.
2. Store the creator's appeal reason.
3. Update the content status to:

```text
under_review
```

4. Add an appeal entry to the structured audit log.
5. Return a confirmation response.

---

### Appeal Response

```json
{
  "content_id": 1,
  "status": "under_review",
  "message": "Appeal received. This content is now marked for human review."
}
```

---

### What Gets Logged

The audit log will store:

```json
{
  "event_type": "appeal",
  "content_id": 1,
  "creator_name": "Example Creator",
  "reason": "I wrote this piece myself and can provide drafts if needed.",
  "status": "under_review",
  "timestamp": "2026-06-28T12:00:00Z"
}
```

---

### Human Reviewer View

A human reviewer opening the appeal queue would see:

* Content ID
* Original submitted text
* Original classification
* Original confidence score
* Original signal scores
* Transparency label shown
* Creator's appeal reason
* Current status: `under_review`
* Audit history for that content

---

## 5. Anticipated Edge Cases

### Edge Case 1: Short Poems

A short poem may have very few words and intentionally unusual structure. The stylometric signal may not have enough data to calculate meaningful sentence length variance or vocabulary diversity.

**Expected handling:**
The system should avoid high confidence when the text is very short. Short texts should be more likely to fall into the uncertain range.

---

### Edge Case 2: Polished Human Essays

A skilled human writer may produce polished, structured, grammatically consistent writing. Both the LLM and stylometric signal may interpret this as AI-like.

**Expected handling:**
The label should avoid absolute language. The creator should be able to appeal, and the audit log should preserve the original decision for review.

---

### Edge Case 3: Edited AI Text

A user may generate text with AI and then heavily revise it. This can make the text look more human according to both signals.

**Expected handling:**
The system may classify the text as uncertain or human-like. This limitation should be documented clearly in the README.

---

### Edge Case 4: Repetitive Human Writing

Some human writing, especially speeches, poems, or persuasive essays, may intentionally repeat words or phrases. The repetition rate could incorrectly increase the AI-like score.

**Expected handling:**
The stylometric score should not dominate the final classification. The LLM signal and final uncertainty range help reduce the risk of false positives.

---

## Architecture

The system has two main flows: submission and appeal. In the submission flow, text passes through validation, two detection signals, confidence scoring, transparency label generation, and audit logging before a JSON response is returned. In the appeal flow, a creator submits a reason for contesting a classification, the content status changes to `under_review`, and the appeal is stored in the audit log.

```text
                        SUBMISSION FLOW

                   POST /submit
                         |
                    Raw Text
                         |
                         v
               +------------------+
               | Input Validation |
               +------------------+
                         |
                         v
          +-------------------------------+
          | Detection Signal 1: Groq LLM |
          +-------------------------------+
                         |
                     LLM Score
                         |
                         v
     +---------------------------------------+
     | Detection Signal 2: Stylometric Rules |
     +---------------------------------------+
                         |
                 Stylometric Score
                         |
                         v
            +---------------------------+
            | Confidence Score Combiner |
            +---------------------------+
                         |
                 Combined Confidence
                         |
                         v
           +-----------------------------+
           | Transparency Label Generator|
           +-----------------------------+
                         |
                         v
                +------------------+
                | Structured Audit |
                |       Log        |
                +------------------+
                         |
                         v
                  JSON API Response


=====================================================

                      APPEAL FLOW

                  POST /appeal
                         |
             Content ID + Creator Reason
                         |
                         v
              +---------------------+
              | Status: under_review|
              +---------------------+
                         |
                         v
                +------------------+
                | Structured Audit |
                |       Log        |
                +------------------+
                         |
                         v
               Appeal Confirmation Response
```

---

## API Surface

### POST /submit

Accepts text content for attribution analysis.

Request:

```json
{
  "text": "This is the submitted writing sample."
}
```

Response:

```json
{
  "content_id": 1,
  "classification": "Likely AI",
  "confidence": 0.74,
  "label": "This content appears likely to be AI-generated. Our system found strong AI-like patterns, but this result is not a final judgment and may be appealed by the creator.",
  "signals": {
    "llm": {
      "score": 0.80,
      "explanation": "The writing appears highly structured and consistently phrased."
    },
    "stylometric": {
      "score": 0.60,
      "features": {
        "average_sentence_length": 18.4,
        "sentence_length_variance": 6.2,
        "type_token_ratio": 0.48,
        "punctuation_density": 0.04,
        "repetition_rate": 0.12
      }
    }
  },
  "status": "classified"
}
```

---

### POST /appeal

Accepts an appeal from a creator.

Request:

```json
{
  "content_id": 1,
  "creator_name": "Example Creator",
  "reason": "I wrote this myself and can provide earlier drafts."
}
```

Response:

```json
{
  "content_id": 1,
  "status": "under_review",
  "message": "Appeal received. This content is now marked for human review."
}
```

---

### GET /log

Returns structured audit log entries.

Response:

```json
[
  {
    "event_type": "classification",
    "content_id": 1,
    "classification": "Likely AI",
    "confidence": 0.74,
    "llm_score": 0.80,
    "stylometric_score": 0.60,
    "status": "classified"
  },
  {
    "event_type": "appeal",
    "content_id": 1,
    "creator_name": "Example Creator",
    "reason": "I wrote this myself and can provide earlier drafts.",
    "status": "under_review"
  }
]
```

---

## AI Tool Plan

This section explains how this specification will be used during implementation.

---

### M3: Submission Endpoint + First Signal

**Spec sections to provide to the AI tool:**

* Project Overview
* Detection Signals
* Architecture
* API Surface

**What I will ask the AI tool to generate:**

* Flask app skeleton
* `POST /submit` endpoint
* Request validation
* Groq LLM classification function
* Basic JSON response format

**How I will verify the output:**

* Run the Flask app locally.
* Send test requests to `POST /submit`.
* Confirm missing text returns an error.
* Confirm valid text returns a JSON response.
* Confirm the LLM signal returns a score between `0.0` and `1.0`.

---

### M4: Second Signal + Confidence Scoring

**Spec sections to provide to the AI tool:**

* Detection Signals
* Uncertainty Representation
* Architecture
* API Surface

**What I will ask the AI tool to generate:**

* Stylometric heuristic function
* Feature extraction logic
* Weighted confidence scoring function
* Classification threshold logic

**How I will verify the output:**

* Test clearly AI-like text.
* Test clearly human-like text.
* Test a short poem.
* Confirm scores vary meaningfully.
* Confirm uncertain cases fall into the `0.40 - 0.69` range.
* Confirm the combined score uses the correct formula:

```text
combined_score = (llm_score * 0.70) + (stylometric_score * 0.30)
```

---

### M5: Production Layer

**Spec sections to provide to the AI tool:**

* Transparency Label Design
* Appeals Workflow
* Anticipated Edge Cases
* Architecture
* API Surface

**What I will ask the AI tool to generate:**

* Transparency label generation logic
* `POST /appeal` endpoint
* `GET /log` endpoint
* Structured audit logging
* Status update logic
* Rate limiting on `POST /submit`

**How I will verify the output:**

* Confirm all three label variants are reachable.
* Confirm an appeal changes content status to `under_review`.
* Confirm appeal reason is stored in the audit log.
* Confirm classification decisions are logged.
* Confirm rate limiting blocks excessive requests.
* Confirm `GET /log` returns at least three visible entries.

---

## Stretch Feature Planning Rule

Before starting any stretch feature, this `planning.md` file will be updated with:

1. The stretch feature selected
2. Why it was selected
3. How it fits into the existing architecture
4. What endpoint, data structure, or UI change is needed
5. How the feature will be tested

Possible stretch features include:

* Ensemble detection with three or more signals
* Provenance certificate / verified human credential
* Analytics dashboard
* Multi-modal support

---

## Milestone 2 Checkpoint

This planning document addresses:

* Detection signals with specific output formats
* Uncertainty representation and confidence thresholds
* Exact transparency label text for three label variants
* Appeals workflow and audit logging behavior
* Specific anticipated edge cases
* Architecture diagram and flow explanation
* AI Tool Plan for M3, M4, and M5
* Requirement to update planning before stretch features
