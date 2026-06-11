# Multilingual Conversational Intelligence Platform
### AI-Powered Speech Documentation & Automation System
**Hackathon Project — AI / Speech Technology / Conversational AI Track**

---

> **How to read this document:**
> This file is your complete build guide. Every section describes *what* a component does, *why* it exists, *how* it connects to everything else, and *what* Claude Code needs to build it. There is no code here — Claude Code will write the code. Your job is to understand this deeply enough to guide it, review what it builds, and run the tasks in order.

---

## Table of Contents

1. [What Are We Building — Plain English](#1-what-are-we-building--plain-english)
2. [The Problem We Are Solving](#2-the-problem-we-are-solving)
3. [Complete System Architecture](#3-complete-system-architecture)
4. [Component Deep Dives](#4-component-deep-dives)
   - 4.1 Audio Capture Layer
   - 4.2 Pre-Processing Layer
   - 4.3 Multilingual ASR Layer
   - 4.4 Language Identification & Alignment
   - 4.5 Conversational Intelligence Engine
   - 4.6 Structured Data Extractor
   - 4.7 Editable Review Interface
   - 4.8 Longitudinal Dashboard
   - 4.9 Storage Layer
5. [Data Flow — End to End](#5-data-flow--end-to-end)
6. [Domain Configuration System](#6-domain-configuration-system)
7. [How the Documentation Agent Works](#7-how-the-documentation-agent-works)
8. [Edge Cases & How We Handle Them](#8-edge-cases--how-we-handle-them)
9. [Technology Choices — Final List](#9-technology-choices--final-list)
10. [Implementation Tasks](#10-implementation-tasks)
11. [Folder Structure](#11-folder-structure)
12. [Environment Variables & API Keys Needed](#12-environment-variables--api-keys-needed)
13. [Testing Checkpoints](#13-testing-checkpoints)

---

## 1. What Are We Building — Plain English

Imagine two people talking on a phone call — a bank agent and a customer, or a doctor and a patient. Normally, someone has to manually write down what was said, fill forms, and maintain records. This is slow, error-prone, and expensive.

We are building an AI system that acts as a **silent third-party observer** sitting on that call. It:

- Listens to both speakers simultaneously
- Understands what they are saying in **Kannada, Hindi, English, or any mix of these**
- Knows **who said what** (differentiates between the two speakers)
- Handles real-world messiness — background noise, pauses, people talking over each other, switching languages mid-sentence
- Automatically writes a **structured report** of what happened on the call (like symptoms noted, diagnosis given, payment confirmed, etc.)
- Produces a **human-readable narrative summary** as if a professional was sitting there taking notes
- Stores everything in a searchable history
- Provides a **web interface** where a human reviewer can read, edit, and approve the generated report

The system works for **two domains out of the box**: Healthcare (doctors, patients, clinics) and Financial Services (banks, loan recovery, surveys). Switching between domains only requires changing a configuration file — the core engine stays the same.

---

## 2. The Problem We Are Solving

The hackathon problem statement identifies these specific pain points in multilingual Indian organisations:

| Pain Point | Our Solution Component |
|---|---|
| Manual documentation — slow and incomplete | Conversational Intelligence Engine + auto-narrative |
| Loss of contextual information during long calls | Persistent context window managed by LangGraph |
| No automation for outbound voice workflows | Outbound call handler via Twilio SDK |
| Poor structured data extraction from speech | Domain-specific JSON extractor with Outlines |
| No longitudinal tracking of past interactions | PostgreSQL history + pgvector semantic search |
| High operational cost from human documentation | End-to-end automated pipeline |

The system must handle **Kannada, Hindi, English, and code-mixed speech** — the reality of how people actually talk in India, not how textbooks say they do. Someone might say "Okay maadi, ₹15,000 credit aagoithu" (Kannada + Hindi numerals + English word) and the system must transcribe, understand, and document that correctly.

---

## 3. Complete System Architecture

The system has **seven sequential layers**. Audio goes in one end, a structured intelligent report comes out the other end. Here is the full picture:

```
┌─────────────────────────────────────────────────────────────────┐
│                    LAYER 0: AUDIO CAPTURE                       │
│   Phone Call (RTP/SIP) │ WebRTC │ Microphone │ Twilio Stream    │
└─────────────────────────────────┬───────────────────────────────┘
                                  │ raw audio (8kHz / 16kHz PCM)
┌─────────────────────────────────▼───────────────────────────────┐
│                  LAYER 1: PRE-PROCESSING                        │
│  DeepFilterNet (noise) → Silero VAD (speech/silence) →          │
│  pyannote.audio 3.3 (who is speaking)                           │
└─────────────────────────────────┬───────────────────────────────┘
                                  │ clean, speaker-tagged audio chunks
┌─────────────────────────────────▼───────────────────────────────┐
│               LAYER 2: MULTILINGUAL ASR                         │
│  Sarvam Saarika v2 (primary) → AI4Bharat IndicASR (fallback) →  │
│  Meta SeamlessM4T v2 (last resort)                              │
└─────────────────────────────────┬───────────────────────────────┘
                                  │ raw text with confidence scores
┌─────────────────────────────────▼───────────────────────────────┐
│         LAYER 3: LANGUAGE ID + WORD ALIGNMENT                   │
│  IndicLID (per-token language label) + WhisperX (timestamps)    │
└─────────────────────────────────┬───────────────────────────────┘
                                  │ timestamped, language-tagged transcript
┌─────────────────────────────────▼───────────────────────────────┐
│         LAYER 4: CONVERSATIONAL INTELLIGENCE ENGINE             │
│  LangGraph Agent → Claude Sonnet / Sarvam-M LLM →              │
│  Intent recognition + Context retention + Narrative updater     │
└─────────────────────────────────┬───────────────────────────────┘
                                  │ updated narrative + intent labels
┌─────────────────────────────────▼───────────────────────────────┐
│          LAYER 5: STRUCTURED DATA EXTRACTOR                     │
│  Domain config (YAML) → Outlines JSON generator →               │
│  IndicNER (named entity recognition in Indic languages)         │
└─────────────────────────────────┬───────────────────────────────┘
                                  │ structured JSON report (domain-specific fields)
┌─────────────────────────────────▼───────────────────────────────┐
│         LAYER 6: STORAGE + RETRIEVAL                            │
│  PostgreSQL (records) + pgvector (embeddings) +                  │
│  Redis (active session cache) + MinIO (audio files)             │
└─────────────────────────────────┬───────────────────────────────┘
                                  │ stored, indexed, searchable
┌─────────────────────────────────▼───────────────────────────────┐
│         LAYER 7: OUTPUT — REVIEW INTERFACE + DASHBOARD          │
│  React frontend: live transcript view │ editable report form │   │
│  past interactions dashboard │ analytics                        │
└─────────────────────────────────────────────────────────────────┘
```

The backend is built in **Python** (FastAPI). The frontend is built in **JavaScript** (React + Vite). They communicate over **REST API** and **WebSockets** (for the real-time streaming parts).

---

## 4. Component Deep Dives

### 4.1 Audio Capture Layer

**What it does:** Gets the audio into our system from whatever source the call is coming from.

**Three capture modes are supported:**

**Mode A — File Upload (for prototyping and demos):** The user uploads a pre-recorded audio file (MP3, WAV, OGG) through the web interface. The system processes it as if it were a live call. This is what you will build and demonstrate at the hackathon.

**Mode B — Live Microphone (in-person recording):** The web interface captures audio through the browser's microphone using the WebRTC API. Audio is streamed over WebSocket to the backend in 100ms chunks. This simulates an in-person consultation.

**Mode C — Telephony Integration (production-grade):** For real phone calls, integration with Twilio's Media Streams API provides a WebSocket feed of the call audio in real time. This is the "real world" version. For the hackathon, this mode is described in the architecture but implemented as optional.

**Audio format requirements:** The pipeline expects 16kHz, mono PCM audio. Any other format must be converted at the capture stage using FFmpeg (a command-line audio tool) before passing downstream. The backend handles this conversion automatically.

**Why dual-channel matters:** If the system can get a phone call where the two speakers are on separate audio channels (which happens with SIP/VoIP systems), speaker identification becomes trivially accurate. When only a mixed mono stream is available, the diarization model has to work harder. The system handles both cases.

---

### 4.2 Pre-Processing Layer

**What it does:** Cleans the audio and figures out who is speaking and when. This layer runs in real time on every 100–200ms audio chunk.

**Component 1 — DeepFilterNet v3 (Noise Suppression)**

Real Indian environments are noisy. Hospital waiting rooms have TVs. Bank offices have multiple conversations happening. Mobile calls have compression artifacts, road noise, and echo.

DeepFilterNet v3 is a neural network trained specifically to separate human speech from environmental noise. It works at the frequency level — it identifies which parts of the audio spectrum are "voice" and which are "background," then attenuates (reduces) everything that isn't voice.

It runs as a Python library that takes a numpy audio array as input and returns a cleaned numpy audio array. Processing time is roughly 5–10ms per 100ms chunk on CPU — fast enough to keep up with live audio.

**Component 2 — Silero VAD (Voice Activity Detection)**

Not all parts of an audio stream contain speech. People pause, think, put callers on hold, and stay silent. Sending silence through the ASR model wastes compute and introduces garbage tokens.

Silero VAD runs on every 50ms chunk and outputs one of three states: `SPEECH`, `SILENCE`, or `SPEECH_ENDING` (a trailing detection to avoid cutting words off). Only chunks marked `SPEECH` are passed to the ASR layer.

It also produces pause timing data — when a pause is longer than 1.5 seconds, the system interprets this as a speaker-turn boundary or a "hold" moment, which gets flagged in the transcript metadata.

**Component 3 — pyannote.audio 3.3 (Speaker Diarization)**

This is the component that answers: "Who is speaking right now — Speaker A or Speaker B?"

Diarization works by extracting a "voice fingerprint" (called a speaker embedding) from each detected speech segment. The embedding is a 256-dimensional vector that numerically represents the acoustic characteristics of a voice. Two segments from the same person will have embeddings that are mathematically close to each other (measured using cosine similarity). Two segments from different people will have embeddings that are far apart.

pyannote uses a model called ECAPA-TDNN to compute these embeddings. It also uses a segmentation model to find the exact timestamps where speaker changes happen.

The output of this component is a **diarization timeline** — a list of segments like:
- `00:00:00 → 00:00:08` : SPEAKER_00
- `00:00:08 → 00:00:15` : SPEAKER_01
- `00:00:15 → 00:00:23` : SPEAKER_00

The system keeps these speaker embeddings stored in a session registry. If the same person reconnects or calls again later, their voice can be re-identified by matching against stored embeddings.

**What it handles:**
- **Crosstalk / interruptions:** When both speakers are detected simultaneously, both segments are processed in parallel and flagged as `[OVERLAP]`
- **Speaker re-identification:** If a speaker goes silent for a long time and comes back, their voice is matched against the session registry, not treated as a new unknown speaker
- **Unknown speakers:** If a third voice is detected (e.g., someone in the background), it gets labeled `SPEAKER_02` and flagged as background

---

### 4.3 Multilingual ASR Layer

**What it does:** Converts the cleaned, speaker-tagged audio chunks into text. This is the core technical challenge of the project.

The system uses a **confidence-gated cascade** — three ASR models stacked in priority order. Each transcript segment gets a confidence score (0.0 to 1.0). If the score is too low, the segment gets passed to the next model.

**Why one model isn't enough:**
Whisper (OpenAI's famous ASR model) is great at English but achieves 25–35% Word Error Rate on Indian code-mixed speech. That means roughly 1 in 3 words is wrong — useless for medical documentation. Specialist Indic ASR models trained on real conversational Indian speech do much better (8–12% WER). But they sometimes struggle with rare medical terms or very strong regional accents. Hence the cascade.

**Model 1 — Sarvam AI Saarika v2 (Primary)**

Saarika is currently the best available ASR for Indian languages in a production context. It was trained on 10,000+ hours of real Indian conversational speech across 10 Indic languages including Kannada, Hindi, and Tamil.

Key capability: It handles code-mixed speech natively. It was trained on real data where people switch between Kannada and English within a single sentence — not clean, textbook language. This makes it dramatically better than Whisper for our use case.

Access method: Sarvam provides an API. You send an audio file or audio bytes, specify the language (or set it to `auto-detect`), and receive back the transcript text with a confidence score. The API returns results in typically 200–400ms per 5-second audio segment.

**Model 2 — AI4Bharat IndicASR (Fallback, confidence < 0.6)**

AI4Bharat is a research initiative by IIT Madras funded by the Indian government. Their IndicASR model is a fine-tuned version of Whisper Large v3, retrained on 17,000 hours of Indic language data.

This model is open-source and can be run locally (no API calls needed). It is particularly strong on formal Indic language speech and domain-specific vocabulary — medical terms in Kannada, financial terminology in Hindi — because it was trained on diverse domain data.

When Saarika returns a confidence score below 0.6, the same audio segment is passed to IndicASR. If IndicASR's confidence is higher, its output is used instead.

**Model 3 — Meta SeamlessM4T v2 (Last Resort, confidence < 0.6 on both)**

SeamlessM4T (Massively Multilingual and Multimodal Machine Translation) is Meta's unified model supporting 100+ languages including all major Indian ones. Its strength is handling truly ambiguous audio — very heavy accents, highly mixed language, or degraded audio quality.

This model is the slowest (it's very large) but is used rarely — only for segments that stumped both primary and secondary models. These segments are also flagged in the output with a `low_quality` marker so the human reviewer knows to pay special attention.

**ASR output format:**
Every text segment coming out of this layer includes:
- The transcript text
- The confidence score (0.0–1.0)
- Which model produced it
- The original speaker label (SPEAKER_00 or SPEAKER_01)
- Start and end timestamps (millisecond precision)
- A quality flag (`ok`, `low_quality`, `uncertain`)

---

### 4.4 Language Identification & Alignment

**What it does:** Labels every word with the language it was spoken in, and aligns the transcript text to precise timestamps.

**Component 1 — IndicLID**

IndicLID (Indian Language Identifier) from AI4Bharat identifies language at the **word level**, not at the sentence level. This distinction is critical.

A sentence-level identifier might label "Maadi okay doctor saab, aaj appointment fix maadona" as "Kannada." But word-level identification gives: KN KN EN EN KN EN KN. This per-token language metadata feeds the LLM downstream so it knows which parts of the transcript are which language and can apply appropriate NLP processing.

IndicLID can identify 47 Indic scripts and languages. It runs as a Python model and takes a text string as input, returning a list of `(word, language_code)` pairs.

**Component 2 — WhisperX Forced Alignment**

The ASR models give us transcript text, but the word-level timestamps from ASR can be imprecise. WhisperX uses a technique called CTC Forced Alignment to precisely match each word in the transcript to its exact start and end time in the audio.

This is non-negotiable for the documentation use case. When a doctor says "The patient reports chest pain starting three days ago" and the system needs to create a timestamped record, we need to know precisely when those words were spoken — not just the segment-level timestamp.

The output of this layer is a fully enriched transcript object:

```
[
  {
    "speaker": "SPEAKER_00",
    "word": "maadi",
    "language": "KN",
    "start_ms": 1240,
    "end_ms": 1560,
    "confidence": 0.87
  },
  ...
]
```

---

### 4.5 Conversational Intelligence Engine

**What it does:** This is the brain of the system. It reads the enriched transcript stream, understands what is happening in the conversation, maintains context across the entire call, and generates a running third-person narrative document.

**The Orchestrator — LangGraph**

LangGraph is a Python library built on top of LangChain that lets you build stateful AI agent workflows as a graph. Instead of a simple "one prompt → one response" LLM call, LangGraph lets you define a network of nodes (AI processing steps) connected by edges (conditional routing logic).

Our agent graph has four nodes:

**Node 1 — Ingest Node:** Receives the latest transcript chunk from the ASR/alignment layer. Appends it to the running conversation history. Checks whether the conversation history has enough new content to warrant an LLM pass (batches ~5 turns together to avoid making an LLM call for every single word).

**Node 2 — Speaker Role Classifier Node:** On the first few turns of a conversation, this node asks the LLM to identify which speaker is playing which role. Is SPEAKER_00 the doctor or the patient? The bank agent or the customer? This is determined from context cues — the way they introduce themselves, the questions they ask, their vocabulary. Once identified, this role mapping is stored in the session state and used for all future processing.

**Node 3 — Structured Extractor Node:** Reads the updated conversation history and extracts domain-specific fields into a JSON object. The exact fields extracted depend on the domain configuration (see Section 6). This node runs every 10 turns or when key events are detected (a diagnosis is stated, a payment amount is confirmed, etc.).

**Node 4 — Narrative Updater Node:** This is the documentation agent. It reads the last few conversation turns and the existing narrative document, then produces an updated version. It does not rewrite the whole document — it appends or modifies only the section relevant to the latest turns. This incremental approach keeps latency low and maintains narrative coherence.

**The LLM Backbone**

The LangGraph agent uses an LLM as its reasoning engine. Two options are configured:

**Claude Sonnet (via Anthropic API):** Best for calls where English is the dominant language or the transcript has been well-translated. Produces the most nuanced, coherent narratives. This is the default.

**Sarvam-M (via Sarvam API):** An instruction-following LLM specifically trained on Indic language data. Better for calls that are predominantly in Kannada or Hindi, where the LLM needs to understand cultural context, regional idioms, and domain vocabulary in those languages.

The system prompt given to the LLM for the narrative generation node is structured carefully:

> *System: You are a professional documentation specialist observing a recorded phone call. You have access to a timestamped, speaker-labeled transcript. Your task is to write a clear, factual, third-person narrative of what occurred during this call. Rules: (1) Write in past tense if the call has ended, present tense if ongoing. (2) Refer to speakers by their identified role (Doctor / Patient / Agent / Customer), never by speaker ID numbers. (3) Where speech was in Kannada or Hindi, translate the meaning accurately and add [Originally in Kannada] or [Originally in Hindi] in brackets. (4) Capture all clinically or financially significant statements verbatim within quotes. (5) Note hesitations, commitments, and emotional tone only when significant. (6) Do not invent, infer, or editorialize beyond what was said.*

**Intent Recognition**

During the conversation, the LLM is also asked to label each speaker turn with an intent from a predefined taxonomy:

Healthcare intents: `REPORTING_SYMPTOM`, `ASKING_QUESTION`, `GIVING_DIAGNOSIS`, `PRESCRIBING_TREATMENT`, `CONFIRMING_HISTORY`, `EXPRESSING_CONCERN`, `CLOSING_CONSULTATION`

Financial intents: `IDENTITY_VERIFICATION`, `CONFIRMING_ACCOUNT`, `REPORTING_PAYMENT`, `DISPUTING_CHARGE`, `REQUESTING_EXTENSION`, `PROVIDING_REASON`, `CONFIRMING_RESOLUTION`

These intent labels feed the **dynamic question branching** feature. If the system detects that the agent hasn't asked about payment mode after a payment confirmation intent, it can surface a prompt to the agent: "You may want to ask about the payment mode."

**Context Retention**

The full conversation history is too long to fit in an LLM's context window for a 30-minute call. The system uses a sliding window approach: the LLM always sees the last 20 turns in full, plus a compressed summary of everything before that. The summary is generated progressively — whenever the context window fills up, the oldest 10 turns are compressed into a summary paragraph that is prepended to the context.

---

### 4.6 Structured Data Extractor

**What it does:** Pulls specific, required data fields out of the conversation and organises them into a structured JSON document that matches the domain's data requirements.

**The Problem with Asking an LLM to Output JSON Freely**

If you simply ask an LLM "extract the patient's symptoms as JSON," it might output valid JSON, or it might output JSON with differently named fields, or it might output JSON wrapped in markdown code blocks that your parser can't handle, or it might hallucinate field names that don't exist in your schema. For a medical or financial record, this is unacceptable.

**The Solution — Outlines**

Outlines is a Python library that constrains LLM output generation at the token level. You define a JSON schema (what fields exist, what types they are, which are required), and Outlines mathematically ensures the LLM can only output tokens that produce valid JSON matching that schema. The constraint is applied during the LLM's generation process, not after it — so it is impossible for the output to violate the schema.

This means if the schema requires a field called `diagnosis` of type `string`, the output will always have a `diagnosis` field of type `string`. It might be `"Not yet determined"` if the doctor hasn't diagnosed yet, but it will never be missing or malformed.

**The Domain Schema System**

Schema definitions are stored in YAML files in a `domains/` folder. When a call starts, the operator selects the domain (Healthcare or Financial), and the system loads the corresponding schema. This makes the extractor completely domain-agnostic — you can add new domains by adding a new YAML file, with no code changes.

Healthcare schema fields extracted:
- `chief_complaint` — the main reason for the visit/call
- `symptoms` — list of reported symptoms with duration if mentioned
- `symptom_onset_date` — when symptoms started
- `past_medical_history` — any mentioned prior conditions
- `current_medications` — what the patient is currently taking
- `clinical_observations` — what the doctor observed
- `diagnosis` — the stated diagnosis or differential diagnoses
- `treatment_plan` — prescribed treatments, drugs, dosages
- `followup_instructions` — what the patient should do next
- `risk_indicators` — any flags like high risk pregnancy, cardiac history, etc.
- `immunization_status` — if discussed
- `referral_needed` — whether a referral to specialist was made
- `call_outcome` — overall outcome of the consultation

Financial schema fields extracted:
- `customer_name` — verified name of the customer
- `account_number` — account or loan number confirmed
- `identity_verified` — boolean, was identity verification completed
- `identity_method` — how identity was verified (OTP, DOB, etc.)
- `outstanding_amount` — the amount discussed
- `payment_status` — paid / pending / disputed / partial
- `payment_amount` — amount paid if applicable
- `payment_date` — date of payment if applicable
- `payment_mode` — UPI / NEFT / cash / cheque / etc.
- `payer_name` — who made the payment (self or third party)
- `reason_for_non_payment` — if payment is pending
- `commitment_date` — if customer committed to paying by a date
- `executive_name` — the bank agent's name if stated
- `call_outcome` — resolution / escalation / follow-up needed

**IndicNER for Indic Named Entities**

Standard NER models miss names, places, and organisations in Indic languages. "Ramanna" might not be recognized as a person's name by an English NER model. AI4Bharat's IndicNER model is trained specifically to recognize named entities across 11 Indian languages.

IndicNER runs on the raw transcript text (before translation) and produces entity tags: `PERSON`, `LOCATION`, `ORGANISATION`, `DATE`, `AMOUNT`, `MEDICAL_CONDITION`, `DRUG`. These tags are used to pre-populate fields in the structured extractor and to validate that the LLM's extraction matches what was actually mentioned.

---

### 4.7 Editable Review Interface

**What it does:** Presents the generated transcript, structured report, and narrative to a human reviewer who can edit, correct, and approve the record before it is stored permanently.

**Why this exists:** AI systems make mistakes. A transcription might be wrong. A diagnosis field might be misattributed. The narrative might mischaracterize the tone of a statement. Before any AI-generated medical or financial record is stored as ground truth, a human must review and approve it. This is both ethically correct and required for regulatory compliance.

**The Interface Has Three Panels:**

**Panel 1 — Live Transcript View:** Shows the full conversation transcript with speaker labels, timestamps, and language tags. Each segment is colour-coded by speaker. Segments flagged as `low_quality` are highlighted in yellow. The reviewer can click any segment to edit the transcription manually if the ASR made an error.

**Panel 2 — Structured Report Form:** Shows all the extracted fields for the domain in an editable form. Every field shows its current value and which part of the transcript that value was extracted from (clicking it highlights the source segment in Panel 1). The reviewer can edit any field value.

**Panel 3 — Narrative Document:** Shows the auto-generated third-person narrative. This is a rich text editor. The reviewer can edit the narrative directly. When they make changes to the structured report form, the relevant sentence in the narrative is highlighted so they know it needs updating.

**Approval Workflow:** A submission button at the bottom of the interface locks the record and saves it to permanent storage with a `reviewed: true` flag and the reviewer's identifier. Un-reviewed records are stored separately and clearly labelled as AI-generated drafts pending review.

---

### 4.8 Longitudinal Dashboard

**What it does:** Provides a searchable, filterable view of all past interactions, with analytics.

**Search Functionality:**
The search bar supports both keyword and semantic search. Keyword search uses PostgreSQL's full-text search. Semantic search uses the pgvector extension — every conversation is stored with an embedding (a numerical representation of its meaning). When you search "patient complained about fever twice this month," the system finds conversations that are semantically similar even if those exact words weren't used.

**Filters available:**
- Date range
- Domain (Healthcare / Financial)
- Speaker role (Doctor / Patient / Agent / Customer)
- Call outcome
- Has risk flags (yes/no)
- Reviewed / Unreviewed status

**Analytics Panel:**
- Total calls processed (by week/month)
- Average call duration
- Most common chief complaints (Healthcare) or reasons for non-payment (Financial)
- Intent distribution chart — what are people mostly calling about?
- Language distribution — what percentage of calls are Kannada, Hindi, English, mixed?
- Documentation time saved (estimated based on call duration vs. manual documentation baseline)

**Patient / Customer History View:**
When a known customer calls again, the system can pull up their entire call history and display a timeline. For healthcare, this creates a longitudinal clinical record. For finance, it shows the full engagement history.

---

### 4.9 Storage Layer

**What it does:** Persists all data securely and makes it efficiently retrievable.

**PostgreSQL — Primary Database**

Stores all structured records, user accounts, session metadata, and the reviewed final versions of call records. Tables include:
- `calls` — one row per call, with metadata (timestamp, domain, duration, speakers, outcome, reviewed status)
- `transcripts` — word-level transcript rows linked to a call
- `structured_reports` — the JSON report for each call
- `narratives` — the text narrative document for each call
- `speakers` — speaker identity records with names if known

**pgvector Extension — Vector Search**

An extension for PostgreSQL that adds a special column type for storing 1536-dimensional embedding vectors. Every call's narrative is converted into an embedding using the `text-embedding-3-small` model from OpenAI (or IndicBERT embeddings for Indic content) and stored in this column. The dashboard's semantic search uses cosine similarity queries against this column.

**Redis — Session Cache**

A fast in-memory data store. During an active call, the current conversation state (last 20 turns, speaker registry, partial structured report, running narrative) is stored in Redis keyed by session ID. Redis is fast enough (sub-millisecond read/write) to support the real-time pipeline. When a call ends, the final state is written to PostgreSQL and the Redis keys are cleaned up.

**MinIO — Object Storage**

Stores the raw audio files. MinIO is an open-source object storage system compatible with Amazon S3 API. All audio is encrypted at rest using AES-256. Files are named by call UUID and accessible only through the application server (not directly via URL).

**Qdrant — Dedicated Vector Database (Optional for Scale)**

For large deployments with thousands of calls, pgvector can slow down. Qdrant is a dedicated vector database optimised for fast similarity search at scale. It runs as a separate Docker container and can replace pgvector for the embedding search functionality.

---

## 5. Data Flow — End to End

Here is the complete journey of a single sentence spoken during a call:

1. **Microphone/phone** captures audio: raw 8kHz PCM bytes
2. **Audio capture layer** buffers 200ms chunks and sends them to the backend via WebSocket
3. **FFmpeg** resamples to 16kHz if needed
4. **DeepFilterNet** removes background noise from the chunk
5. **Silero VAD** checks if this chunk contains speech. If silence → discard. If speech → continue
6. **pyannote.audio** computes speaker embedding, matches against session registry, assigns SPEAKER_00 or SPEAKER_01
7. **Saarika ASR** transcribes the cleaned speech chunk, returns text + confidence score
8. If confidence < 0.6: **IndicASR** re-processes the same audio chunk
9. If still < 0.6: **SeamlessM4T** processes and the segment is flagged `low_quality`
10. **IndicLID** labels each word with a language code (KN, HI, EN, etc.)
11. **WhisperX** aligns each word to its precise millisecond timestamp
12. The enriched segment is appended to the session's `transcript` list in **Redis**
13. Every 5 turns: **LangGraph ingest node** fires, reads the latest batch from Redis
14. **Speaker role classifier** checks if roles have been identified. If not, runs classification
15. **Structured extractor** runs the domain-specific extraction with Outlines, updates the JSON report in Redis
16. **Narrative updater** runs the LLM with the latest turns and the existing narrative, produces updated narrative text, saves to Redis
17. All updates are pushed to the **React frontend** via WebSocket — the reviewer sees the transcript and report update in real time
18. When the call ends: entire session state is written from **Redis** to **PostgreSQL**, audio file is stored in **MinIO**, embeddings are computed and stored in pgvector
19. Record appears in the **dashboard** as a draft pending human review

---

## 6. Domain Configuration System

This is one of the most important architectural decisions. The entire extraction and documentation system adapts to a domain without any code changes.

Each domain has a configuration file in the `domains/` directory structured as follows:

**What the config file contains:**

- `domain_name` — human readable name (e.g., "Healthcare — General Consultation")
- `primary_language` — expected dominant language of calls in this domain
- `speaker_roles` — what the two speakers are called (e.g., `["Doctor", "Patient"]` or `["Agent", "Customer"]`)
- `structured_fields` — the list of fields to extract, with field name, description, data type, and whether it's required
- `intent_taxonomy` — the list of valid intent labels for this domain
- `narrative_style` — style instructions for the narrative (clinical and formal / conversational and brief)
- `system_prompt_additions` — domain-specific additions to the LLM system prompt (e.g., for healthcare: "Always record medication dosages exactly as stated. Never infer a dosage not explicitly mentioned.")
- `pii_fields` — list of fields that contain personally identifiable information and must be encrypted
- `required_coverage` — which fields must be populated before a call can be marked complete

When adding a third domain (e.g., "Survey Research" or "Insurance Claims"), a developer just creates a new YAML file in the `domains/` directory. The rest of the system picks it up automatically.

---

## 7. How the Documentation Agent Works

This section explains the "third-person observer" capability in depth because it is the centerpiece output of the system.

**The Core Idea**

A human professional taking notes during a call does not write down every word. They synthesise, translate jargon into plain language, identify what matters, and organise information into a coherent record. The documentation agent attempts to replicate this behaviour using an LLM.

**Incremental vs. Full Regeneration**

The naive approach is to wait until the call ends, then send the entire transcript to the LLM and ask for a summary. This has two problems: (1) you get nothing useful until the call is over, and (2) the transcript from a 30-minute call may exceed the LLM's context limit.

Our approach is incremental. Every 5 turns, the agent runs and receives:
- The narrative document as it stands so far
- The 5 new turns
- The current structured report

The LLM is instructed to append to and refine the narrative based on the new turns, not rewrite it from scratch. The narrative grows continuously throughout the call, and the reviewer can watch it build in real time.

**What Makes a Good Narrative**

The narrative the system generates aims to match the quality of documentation a trained clinical assistant or customer service supervisor would produce. Key properties:

- **Third person:** "The doctor asked…", "The customer stated…", not "I asked…"
- **Role-referenced:** Uses the identified roles, not speaker numbers
- **Translation embedded:** Regional language statements are rendered in English with a bracketed note indicating the original language
- **Clinically/financially accurate:** Numbers, dates, drug names, account numbers are transcribed exactly as stated — never paraphrased
- **Tonally neutral:** Does not describe anyone as "angry" or "confused" unless those exact words were used. Uses observable descriptions: "The customer repeated the question three times" rather than "The customer seemed frustrated"
- **Chronologically faithful:** Events are recorded in the order they occurred in the call

**Sample output for a healthcare call:**

> At 10:14 AM, the call was initiated between Dr. Venkataraman (Doctor) and Lakshmi Devi (Patient). The patient confirmed her name and date of birth for identification.
>
> The patient reported that she had been experiencing chest discomfort for the past three days [Originally in Kannada: "Mooru dina aaitu, echcharike aaguttide — chest alli"]. She described the sensation as pressure rather than sharp pain and noted it worsened upon climbing stairs.
>
> Dr. Venkataraman asked about history of hypertension and diabetes. The patient confirmed she has had hypertension for seven years and is currently taking Amlodipine 5mg daily, which she has not missed. She denied any history of cardiac events.
>
> The doctor noted the patient's blood pressure reading from her home monitor as 148/92, recorded by the patient this morning. He assessed this as elevated and instructed her to come in for an ECG today. He stated [quote]: "Do not wait for tomorrow, come to the clinic before 4 PM today."
>
> The doctor prescribed a chest X-ray and ECG as immediate investigations. He advised the patient not to engage in strenuous activity until reviewed. No new medication was prescribed at this stage. The call was concluded at 10:22 AM.

---

## 8. Edge Cases & How We Handle Them

The system must handle everything that happens in the real world, not just clean test recordings.

**Long Pauses (Caller on Hold, Thinking, Distracted)**

Detection: Silero VAD detects silence lasting more than 1.5 seconds. After 3 seconds, the system enters a `HOLD` state.

Handling: The current speaker's turn is not closed until speech resumes. A metadata tag `[PAUSE: 12s]` is inserted into the transcript at the pause location. The narrative does not document pauses unless they are exceptionally long (> 30 seconds), in which case "The agent placed the caller on hold for approximately 45 seconds" is inserted.

**Crosstalk — Both Speakers Talking Simultaneously**

Detection: pyannote's overlap detection module identifies segments where two speaker embeddings are both active.

Handling: Both audio streams are processed in parallel through the ASR layer. Both transcriptions are included in the transcript with an `[OVERLAP]` tag. The narrative records this as "Both speakers spoke simultaneously; [Speaker A]'s statement was: '...' while [Speaker B] stated: '...'" The reviewer is asked to verify overlapping segments.

**Background Noise Spike (Traffic, TV, Other People Talking)**

Detection: SNR (Signal-to-Noise Ratio) monitoring. When SNR drops below 15dB (meaning noise is nearly as loud as speech), the segment is flagged.

Handling: DeepFilterNet suppresses as much noise as possible. If the transcript confidence score is still low after suppression, the segment gets a `low_quality` flag. In the review interface, these segments are highlighted in yellow and the reviewer is prompted to listen to the original audio.

**Filler Words and Non-Lexical Sounds**

Indian conversational speech is full of fillers: "uh," "hmm," "acha," "haanji," "okay okay," throat clearing. These are transcribed accurately in the raw transcript (for authenticity) but are filtered out of the narrative and do not feed the structured extractor.

A domain-configurable filler word list covers common English and Indic fillers.

**Speaker Identity Re-Identification**

If the connection drops briefly and re-establishes, or if one speaker goes silent for a long time and comes back, their new speech segment gets a new embedding computed. The system compares this against all stored embeddings from the current session using cosine similarity. A score above 0.85 is considered a match, and the existing speaker label is assigned. A score below 0.7 gets a new SPEAKER_XX label. Between 0.7 and 0.85, the segment is flagged for human review.

**Very Heavy Accents or Dialectal Speech**

Some regional accents (Havyaka Kannada, Bhojpuri Hindi) can have WERs of 30%+ even on Indic-trained models. The system handles this by lowering the confidence threshold for fallback (to 0.5 instead of 0.6) and by including the `low_quality` flag prominently in the review interface. The structured extractor is also instructed to prioritise fields where it has high confidence and explicitly mark uncertain fields rather than guessing.

**Code-Switching Mid-Word (Transliteration)**

Sometimes speakers produce words that are Indic language words written/spoken in a mix — "doctor-ra hatrake hogi" (go to the doctor's — Kannada with "doctor" in English). IndicLID handles this at the word level. The transcript preserves the original mixed spelling, and the narrative translates semantically.

---

## 9. Technology Choices — Final List

### Backend (Python)

| Purpose | Technology | Why This One |
|---|---|---|
| Web framework | FastAPI | Async-native, WebSocket support, auto-generates API docs |
| Agent orchestration | LangGraph 0.2+ | Stateful graph-based agents, built for this exact use case |
| Noise suppression | DeepFilterNet v3 | SOTA on DNS Challenge benchmark, CPU-friendly |
| Voice activity detection | Silero VAD | Best balance of accuracy and speed |
| Speaker diarization | pyannote.audio 3.3 | Best DER (Diarization Error Rate) on phone call benchmarks |
| Primary ASR | Sarvam AI Saarika v2 API | Best code-mixed Indic ASR available |
| Secondary ASR | AI4Bharat IndicASR | Open-source, runs locally |
| Fallback ASR | Meta SeamlessM4T v2 | Multi-language, handles ambiguous audio |
| Language ID | AI4Bharat IndicLID | Word-level, 47 Indic languages |
| Word alignment | WhisperX | CTC forced alignment, millisecond precision |
| Named entity recognition | AI4Bharat IndicNER | Indic-trained NER |
| Structured output | Outlines library | Schema-constrained LLM generation |
| Primary LLM | Claude Sonnet (Anthropic API) | Best narrative generation quality |
| Indic LLM | Sarvam-M API | Indic-native instruction following |
| Audio conversion | FFmpeg (subprocess) | Universal audio format handling |
| Task queue | Celery + Redis | Async processing of long audio files |
| Primary DB | PostgreSQL | Reliable, supports pgvector extension |
| Vector search | pgvector | Semantic search without a separate DB |
| Session cache | Redis | Sub-millisecond read/write for live sessions |
| Object storage | MinIO | S3-compatible, self-hosted, encrypted |

### Frontend (JavaScript)

| Purpose | Technology | Why This One |
|---|---|---|
| Framework | React + Vite | Modern, fast, component-based |
| UI components | shadcn/ui + Tailwind CSS | Clean, accessible, no design overhead |
| Real-time comms | WebSocket (native browser API) | For live transcript and report updates |
| Rich text editor | TipTap | For the editable narrative panel |
| Charts / analytics | Recharts | React-native charting library |
| State management | Zustand | Lightweight, simple for this scale |
| Audio recording | WebRTC (native browser API) | For microphone capture mode |
| HTTP client | Axios | For REST API calls to backend |

### Infrastructure

| Purpose | Technology |
|---|---|
| Containerisation | Docker + Docker Compose |
| Reverse proxy | Nginx |
| Process management | Uvicorn (ASGI server for FastAPI) |

---

## 10. Implementation Tasks

These tasks are designed to be executed in order. Each task is a clear, self-contained unit of work. You will give each task to Claude Code one at a time, showing it this document for context.

---

### TASK 1 — Project Scaffolding & Environment Setup

**What needs to happen:**

Create the complete folder structure for the project. Set up both the Python backend and the React frontend as separate sub-projects within one monorepo. Create a `docker-compose.yml` file that spins up PostgreSQL, Redis, MinIO, and the backend and frontend services together with a single command.

Create the `.env.example` file listing all the environment variables the project needs (API keys, database URLs, secrets). Create a `requirements.txt` for the Python backend with all the libraries listed in Section 9. Create a `package.json` for the React frontend.

Set up the FastAPI app with a single health-check endpoint (`GET /health` returns `{"status": "ok"}`). Set up the React app with a placeholder home page. Confirm both start successfully with `docker-compose up`.

**Why this is first:** Nothing else can be built until the foundation exists. Getting the environment working correctly from the start saves enormous debugging time later.

**Acceptance criteria:** `docker-compose up` starts all services without errors. `http://localhost:8000/health` returns `{"status": "ok"}`. `http://localhost:3000` shows the React placeholder page.

---

### TASK 2 — Database Schema & Storage Setup

**What needs to happen:**

Write the PostgreSQL database schema as SQL migration files. Create the tables: `calls`, `transcripts`, `structured_reports`, `narratives`, `speakers`, `users`, and `review_logs`. Enable the pgvector extension and add the embedding column to the `calls` table.

Write a Python database connection module using SQLAlchemy (async version). Write a MinIO client wrapper that provides `upload_audio(call_id, audio_bytes)` and `get_audio_url(call_id)` functions.

Write the domain YAML configuration files for both Healthcare and Financial domains. Define all the structured fields listed in Section 6 in those files. Write a Python `DomainConfigLoader` class that reads these YAML files and validates them.

**Why this is second:** The schema is the backbone of the entire system. Every other component reads from and writes to it.

**Acceptance criteria:** Running the migration script creates all tables in PostgreSQL. The DomainConfigLoader correctly parses both YAML files and raises helpful errors if a YAML file is malformed.

---

### TASK 3 — Audio Pre-Processing Pipeline

**What needs to happen:**

Build a Python `AudioPreprocessor` class with the following methods:
- `resample(audio_bytes, target_hz=16000)` — uses FFmpeg subprocess to convert any audio format to 16kHz mono WAV
- `denoise(audio_array)` — applies DeepFilterNet v3 noise suppression, returns cleaned audio array
- `detect_speech(audio_array)` — runs Silero VAD on 50ms chunks, returns a list of speech segment start/end times

Build a `SpeakerDiarizer` class with:
- `diarize(audio_array)` — runs pyannote.audio 3.3, returns a list of `{speaker_id, start_ms, end_ms}` diarization segments
- `get_embedding(audio_segment)` — returns the 256-dim ECAPA-TDNN embedding for a given audio segment
- `match_speaker(embedding, session_registry)` — cosine similarity comparison against stored embeddings, returns best match speaker ID or "NEW_SPEAKER"

Build a `SessionSpeakerRegistry` class that stores speaker embeddings during an active call in Redis, keyed by `{session_id}:speakers`.

**Why this task:** The pre-processing pipeline is the most hardware-intensive part of the system. Getting it right and benchmarked early is critical. On a laptop CPU, it should process audio at 2–3x real-time speed (meaning a 10-second audio chunk should take 3–5 seconds to process).

**Acceptance criteria:** Given a noisy test audio file with two speakers, the pipeline outputs a clean diarized transcript with correct speaker labels and timestamps. Test with a sample Kannada/Hindi audio clip downloaded from a public dataset.

---

### TASK 4 — Multilingual ASR Cascade

**What needs to happen:**

Build an `ASRCascade` class that implements the three-model confidence-gated cascade described in Section 4.3.

- `transcribe_saarika(audio_array, language="auto")` — calls the Sarvam AI Saarika API, returns `{text, confidence, model: "saarika"}`
- `transcribe_indic_asr(audio_array)` — loads and runs the AI4Bharat IndicASR model locally, returns `{text, confidence, model: "indic_asr"}`
- `transcribe_seamless(audio_array)` — loads and runs SeamlessM4T v2, returns `{text, confidence, model: "seamless"}`
- `transcribe(audio_array)` — the main method that applies the cascade logic: try Saarika → if confidence < 0.6, try IndicASR → if still < 0.6, try SeamlessM4T → return result with appropriate quality flag

Build a `LanguageAligner` class:
- `identify_languages(text)` — runs IndicLID on the text, returns a list of `{word, language_code}` pairs
- `align_words(audio_array, text)` — runs WhisperX forced alignment, returns a list of `{word, start_ms, end_ms, confidence}` pairs
- `enrich_transcript(audio_array, text)` — combines both, returns the fully enriched transcript segment object

**Why this task:** ASR is the single most complex and fragile component. It needs its own task with extensive testing. Use a diverse test set: a clean English sentence, a Kannada sentence, an English-Kannada code-mixed sentence, and a noisy sentence.

**Acceptance criteria:** The cascade correctly falls back when Saarika's confidence is low. IndicLID correctly identifies language per word in a code-mixed test sentence. WhisperX produces word timestamps within 100ms accuracy.

---

### TASK 5 — Conversational Intelligence Engine (LangGraph Agent)

**What needs to happen:**

Build the LangGraph agent described in Section 4.5.

Define the `ConversationState` TypedDict with all the fields: `transcript_chunks`, `speaker_map`, `context_window`, `structured_data`, `narrative`, `domain`, `session_id`, `turn_count`.

Implement the four nodes:
- `ingest_node` — appends the new transcript chunk to state, increments turn count
- `speaker_role_classifier_node` — runs only on turns 1–5, prompts the LLM to identify which SPEAKER_XX maps to which domain role (Doctor/Patient, Agent/Customer), stores the map in state
- `structured_extractor_node` — runs every 10 turns or on key intent triggers; uses Outlines with the domain schema to produce structured JSON; merges it with existing structured_data in state
- `narrative_updater_node` — reads the last 5 turns and current narrative; prompts the LLM to produce an updated narrative; replaces the narrative in state

Define the edges:
- After `ingest_node`: always route to `speaker_role_classifier_node` if speaker map is not yet established; else route to `structured_extractor_node` on multiples of 10 turns; else route to `narrative_updater_node`

Build a `ConversationSession` class that wraps the LangGraph graph:
- `start_session(domain, session_id)` — initialises state in Redis, returns session_id
- `process_chunk(session_id, enriched_segment)` — retrieves state from Redis, runs the graph, saves updated state to Redis, returns `{narrative_update, structured_data_update}`
- `end_session(session_id)` — runs final graph pass, writes final state to PostgreSQL, clears Redis keys

**Why this task:** The LangGraph agent is the core intelligence of the system. It is also the most prompt-engineering-intensive part — the narrative quality depends entirely on how the system prompts are written.

**Acceptance criteria:** Given a simulated 10-turn conversation (as a list of enriched transcript segments, not real audio), the agent produces a coherent third-person narrative and a correctly populated structured JSON report matching the domain schema.

---

### TASK 6 — REST API & WebSocket Endpoints

**What needs to happen:**

Build all the FastAPI API endpoints that the frontend will call.

REST endpoints:
- `POST /sessions/start` — body: `{domain}`, response: `{session_id}`
- `POST /sessions/{session_id}/upload` — multipart audio file upload, triggers full pipeline processing as a background task, returns `{task_id}`
- `GET /sessions/{session_id}/status` — returns current processing status
- `GET /sessions/{session_id}/transcript` — returns full transcript
- `GET /sessions/{session_id}/report` — returns structured JSON report
- `GET /sessions/{session_id}/narrative` — returns narrative text
- `PUT /sessions/{session_id}/report` — body: updated JSON report (from reviewer edits)
- `PUT /sessions/{session_id}/narrative` — body: updated narrative text
- `POST /sessions/{session_id}/approve` — marks session as reviewed and approved
- `GET /calls` — paginated list of all completed calls with filters
- `GET /calls/{call_id}` — full record for a specific call
- `GET /analytics` — summary analytics data
- `GET /search?q=...` — semantic + keyword search across calls

WebSocket endpoint:
- `WS /sessions/{session_id}/stream` — the frontend connects here during live microphone mode. Frontend sends audio chunks (base64-encoded bytes). Backend responds with events: `{type: "transcript_update", data: {...}}` and `{type: "report_update", data: {...}}` and `{type: "narrative_update", data: "..."}`

**Why this task:** The API is the contract between frontend and backend. Defining it cleanly and completely now means the frontend task can be done in parallel without confusion.

**Acceptance criteria:** All REST endpoints return the correct response shapes when tested with a tool like Postman or httpie. The WebSocket endpoint accepts a connection and sends back mock events.

---

### TASK 7 — React Frontend: Core Pages & Transcript Viewer

**What needs to happen:**

Build the core React application structure with routing (React Router v6). Pages needed: Home/Dashboard, New Session (start a call), Session Review, Call History, Call Detail.

Build the core components for the Session Review page:
- `TranscriptPanel` — displays enriched transcript with speaker labels, timestamps, language tags, and quality flags. Speaker A and Speaker B are colour-coded. Low quality segments have a yellow background and a warning icon. Each segment is editable inline.
- `AudioPlayer` — a waveform audio player component that lets the reviewer seek through the recording and listen to individual segments. When the reviewer clicks a transcript segment, the audio player jumps to that timestamp.
- `LiveTranscriptFeed` — a variant of TranscriptPanel that opens a WebSocket connection and appends new segments as they arrive in real time.

Connect `LiveTranscriptFeed` to the backend WebSocket endpoint. Test it with a file upload to the backend and verify that transcript segments appear on the frontend as they are processed.

**Why this task:** The transcript viewer is the foundation of the review interface. Getting it right — especially the WebSocket live updates — is the biggest frontend challenge.

**Acceptance criteria:** Uploading a test audio file through the UI causes the transcript to appear on screen as the pipeline processes it. Speaker labels are correct. Timestamps are displayed.

---

### TASK 8 — React Frontend: Report Form & Narrative Editor

**What needs to happen:**

Build the domain-adaptive structured report form. The form fields should be dynamically generated from the domain configuration — when the domain is "Healthcare," healthcare fields appear; when it is "Financial," financial fields appear. The form state is initialised with values from the backend's structured report.

Each form field should show a "source" indicator — a small clickable link that says which part of the transcript this value was extracted from. Clicking it scrolls the transcript panel to and highlights the source segment.

Build the `NarrativeEditor` component using the TipTap rich text editor library. Pre-populate it with the narrative text from the backend. When the reviewer saves, send the updated narrative text to `PUT /sessions/{session_id}/narrative`.

Build the `ApprovalPanel` — a sidebar showing: current review status, a checklist of required fields (from the domain config), a submission button that enables only when all required fields are populated, and a confirmation dialog explaining that submission is permanent.

**Why this task:** The review interface is what makes the system trustworthy. No AI-generated medical or financial record should be stored without human review.

**Acceptance criteria:** For a Healthcare domain session, the form shows all healthcare fields. For a Financial domain session, the form shows all financial fields. Editing a field in the form and clicking save updates the record in the database.

---

### TASK 9 — Dashboard, Search & Analytics

**What needs to happen:**

Build the Call History page with a paginated table of past calls. Each row shows: call date, domain, duration, speakers, call outcome, reviewed status. Clicking a row opens the Call Detail page.

Build the search bar at the top of the Call History page. It should support keyword search (via the REST API's `GET /search` endpoint) and display results with highlighted matching text.

Build the Analytics panel as a collapsible section on the dashboard home page. Include:
- A bar chart of calls per week (Recharts BarChart)
- A pie chart of language distribution (English / Kannada / Hindi / Mixed)
- A pie chart of call outcomes
- Stat cards showing: total calls, average call duration, percentage reviewed

Build the Patient/Customer History view — a timeline page accessible from any call record showing all past calls from the same identified speaker (matched via voice embedding or verified name).

**Why this task:** The dashboard and longitudinal tracking features are explicitly required by the problem statement. They transform the system from a single-call tool into an ongoing intelligence platform.

**Acceptance criteria:** The analytics page renders correctly with mock data. The search bar returns relevant results from the database. The patient history timeline shows multiple calls linked to the same person.

---

### TASK 10 — Integration Testing, Polish & Demo Preparation

**What needs to happen:**

Run the complete end-to-end pipeline with a set of test audio files covering all the edge cases:
1. A clean English call (baseline)
2. A Hindi-dominant call
3. A Kannada-dominant call
4. A code-mixed call (Kannada + English)
5. A noisy call with background traffic
6. A call with a long pause (> 10 seconds)
7. A call with significant crosstalk

For each test, verify:
- Speaker identification is correct
- ASR WER is acceptable (< 20% for clean audio, < 35% for noisy audio)
- Structured fields are correctly extracted
- Narrative reads naturally and is factually accurate
- Review interface correctly highlights issues

Fix any bugs found. Improve system prompts based on narrative quality. Tune the confidence thresholds if the fallback cascade is triggering too often or not enough.

Prepare a 5-minute demo script with a pre-recorded sample call (healthcare domain) that showcases: (1) live transcription appearing, (2) structured fields populating, (3) narrative building, (4) review and approval, (5) dashboard history view.

Create a `README.md` explaining how to run the project for the hackathon judges.

**Why this task:** Demos win hackathons, not just working code. A polished, well-rehearsed demo of a working system beats a technically impressive but buggy one every time.

**Acceptance criteria:** All 7 test audio files process without crashing. The demo script runs cleanly from start to finish in under 5 minutes.

---

## 11. Folder Structure

```
multilingual-conv-agent/
│
├── backend/
│   ├── main.py                        # FastAPI app entry point
│   ├── requirements.txt
│   ├── .env.example
│   │
│   ├── api/
│   │   ├── sessions.py               # Session start, upload, status endpoints
│   │   ├── calls.py                  # Call history, detail endpoints
│   │   ├── search.py                 # Search endpoint
│   │   ├── analytics.py              # Analytics endpoint
│   │   └── websocket.py              # WebSocket streaming endpoint
│   │
│   ├── pipeline/
│   │   ├── audio_preprocessor.py     # DeepFilterNet + Silero VAD
│   │   ├── speaker_diarizer.py       # pyannote.audio + embedding registry
│   │   ├── asr_cascade.py            # Saarika + IndicASR + SeamlessM4T
│   │   ├── language_aligner.py       # IndicLID + WhisperX
│   │   └── pipeline_runner.py        # Orchestrates the full pipeline
│   │
│   ├── agent/
│   │   ├── graph.py                  # LangGraph graph definition + nodes
│   │   ├── nodes/
│   │   │   ├── ingest.py
│   │   │   ├── speaker_classifier.py
│   │   │   ├── extractor.py
│   │   │   └── narrative_updater.py
│   │   ├── prompts.py                # All LLM system prompts
│   │   └── session_manager.py       # ConversationSession class
│   │
│   ├── extraction/
│   │   ├── structured_extractor.py   # Outlines-based JSON extraction
│   │   └── ner.py                    # IndicNER wrapper
│   │
│   ├── storage/
│   │   ├── database.py               # SQLAlchemy async engine + models
│   │   ├── redis_client.py           # Redis wrapper
│   │   └── minio_client.py           # MinIO audio storage wrapper
│   │
│   ├── domains/
│   │   ├── healthcare.yaml           # Healthcare domain config
│   │   └── financial.yaml            # Financial domain config
│   │
│   └── utils/
│       ├── domain_loader.py          # YAML config reader
│       └── audio_utils.py            # FFmpeg helpers
│
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   │
│   ├── src/
│   │   ├── App.jsx                   # Router + layout
│   │   ├── main.jsx
│   │   │
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx
│   │   │   ├── NewSession.jsx
│   │   │   ├── SessionReview.jsx
│   │   │   ├── CallHistory.jsx
│   │   │   ├── CallDetail.jsx
│   │   │   └── PatientHistory.jsx
│   │   │
│   │   ├── components/
│   │   │   ├── TranscriptPanel.jsx
│   │   │   ├── LiveTranscriptFeed.jsx
│   │   │   ├── AudioPlayer.jsx
│   │   │   ├── ReportForm.jsx
│   │   │   ├── NarrativeEditor.jsx
│   │   │   ├── ApprovalPanel.jsx
│   │   │   ├── AnalyticsPanel.jsx
│   │   │   ├── CallHistoryTable.jsx
│   │   │   └── SearchBar.jsx
│   │   │
│   │   ├── hooks/
│   │   │   ├── useWebSocket.js       # WebSocket connection hook
│   │   │   └── useSession.js         # Session state management
│   │   │
│   │   ├── api/
│   │   │   └── client.js             # Axios API client with all endpoints
│   │   │
│   │   └── store/
│   │       └── useAppStore.js        # Zustand global state
│
├── docker-compose.yml                # PostgreSQL, Redis, MinIO, backend, frontend
├── nginx.conf                        # Reverse proxy config
└── README.md                         # How to run for judges
```

---

## 12. Environment Variables & API Keys Needed

You will need to obtain these before starting Task 1. All go in the `.env` file.

| Variable | What it is | Where to get it |
|---|---|---|
| `ANTHROPIC_API_KEY` | Claude Sonnet API access | console.anthropic.com |
| `SARVAM_API_KEY` | Saarika ASR + Sarvam-M LLM | sarvam.ai developer portal |
| `DATABASE_URL` | PostgreSQL connection string | Set in docker-compose.yml |
| `REDIS_URL` | Redis connection string | Set in docker-compose.yml |
| `MINIO_ENDPOINT` | MinIO server address | Set in docker-compose.yml |
| `MINIO_ACCESS_KEY` | MinIO access credential | Set in docker-compose.yml |
| `MINIO_SECRET_KEY` | MinIO secret credential | Set in docker-compose.yml |
| `SECRET_KEY` | App-level secret for session signing | Generate randomly |
| `HUGGINGFACE_TOKEN` | For downloading pyannote models | huggingface.co/settings/tokens |
| `PYANNOTE_AUTH_TOKEN` | pyannote model access | Accept terms at hf.co/pyannote |

The `HUGGINGFACE_TOKEN` and `PYANNOTE_AUTH_TOKEN` are needed because pyannote's diarization model requires you to accept a user agreement on the Hugging Face model page before you can download it.

---

## 13. Testing Checkpoints

Use these checkpoints after each task to verify the system is on track before proceeding.

| After Task | What to test | Expected result |
|---|---|---|
| Task 1 | `docker-compose up` | All 5 containers start, health check passes |
| Task 2 | Run migration script | All tables appear in PostgreSQL. Both YAML files load without errors |
| Task 3 | Run preprocessor on a test audio file | Clean audio + diarization timeline with correct speaker segments |
| Task 4 | Run ASR cascade on a code-mixed audio clip | Transcription with per-word language labels and timestamps |
| Task 5 | Feed 10 simulated transcript turns to the agent | Coherent narrative + populated structured report |
| Task 6 | Upload a test audio file via `POST /sessions` | Polling the status endpoint shows the pipeline progressing |
| Task 7 | Open the web app and upload an audio file | Transcript segments appear on screen in real time |
| Task 8 | Edit a field in the report form and save | Database record reflects the edit |
| Task 9 | Open the Call History page | Past calls appear in the table with correct metadata |
| Task 10 | Run all 7 test audio files end-to-end | No crashes, acceptable quality on all test cases |

---

*This document is the single source of truth for the project. When in doubt about how any component should behave, refer back to the relevant section here. Every architectural decision described in this document traces directly to a requirement in the hackathon problem statement.*
