<div align="center">

<br/>

# 🔊 VaakSetu
### AI-Powered Multilingual Conversational Intelligence Platform

*वाक् + सेतु — The Voice Bridge for Bharat*

<br/>

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-15-000000?style=for-the-badge&logo=nextdotjs&logoColor=white)](https://nextjs.org)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![SQLite](https://img.shields.io/badge/SQLite-Primary_DB-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://sqlite.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Infra_Ready-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org)
[![Redis](https://img.shields.io/badge/Redis-7-DC382D?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io)
[![Twilio](https://img.shields.io/badge/Twilio-SDK-F22F46?style=for-the-badge&logo=twilio&logoColor=white)](https://twilio.com)
[![Docker Compose](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)

<br/>

> **VaakSetu** is an autonomous voice AI stack that can observe or run multilingual call flows, understand Indian code-mixed speech in real time, and generate structured records with human-readable summaries for healthcare and financial operations.

<br/>

---

</div>

## 📋 Table of Contents

- [The Problem](#-the-problem)
- [What VaakSetu Does](#-what-vaaksetu-does)
- [System Architecture](#-system-architecture)
- [Tech Stack](#-tech-stack)
- [Key Features](#-key-features)
- [Outbound Calling Pipeline](#-autonomous-outbound-calling-with-auto-documentation)
- [Supported Domains](#-supported-domains)
- [Quick Start](#-quick-start)
- [Project Structure](#-project-structure)
- [Environment Variables](#-environment-variables)
- [Team](#-team)

---

## 🚨 The Problem

India runs on voice. But documentation still runs on manual entry.

| Pain Point | Operational Impact |
|---|---|
| ASHA / field workflows require manual call notes | High overhead, delayed reporting |
| Clinical and support teams spend time on post-call paperwork | Reduced service throughput |
| Code-mixed inputs (Hinglish/Kanglish) break rigid bots | Lost context and poor extraction |
| Loan collection / follow-up calls lack structured records | Compliance and audit friction |

Every doctor-patient call and every recovery call still depends on someone writing everything down after the conversation.

**VaakSetu reduces that manual burden with real-time extraction + structured storage.**

---

## 💡 What VaakSetu Does

VaakSetu acts as a conversational intelligence layer for live calls and session workflows. It:

- 🎙️ **Listens / transcribes** multilingual and code-mixed speech with Sarvam-first ASR
- 👥 **Tracks roles and context** across turns for agent-quality interactions
- 🧠 **Runs configurable dialogue agents** using dynamic agent templates (built from UI)
- 📋 **Auto-collects structured fields** per domain (healthcare / financial)
- ✍️ **Generates readable summaries** and logs conversation history
- 📞 **Supports Twilio call paths** for outbound and media-stream integration
- 🔄 **Switches domain behavior by config** (YAML + agent settings)
- 🤖 **Scores completed sessions** with programmatic + LLM-judge reward signals

---

## 🏗️ System Architecture

```mermaid
flowchart TD
    classDef frontend fill:#1E293B,stroke:#38BDF8,stroke-width:2px,color:#F8FAFC
    classDef ai fill:#0F172A,stroke:#F43F5E,stroke-width:2px,color:#F8FAFC
    classDef orchestrator fill:#172554,stroke:#A855F7,stroke-width:2px,color:#F8FAFC
    classDef db fill:#020617,stroke:#2DD4BF,stroke-width:2px,color:#F8FAFC
    classDef outbound fill:#0F2B1E,stroke:#22C55E,stroke-width:2px,color:#F8FAFC

    FE[Next.js Dashboard<br/>Build · Session · Analysis]:::frontend
    BE[FastAPI Backend<br/>/api routes + websocket]:::orchestrator
    AI[task1_ai_core<br/>ASR · Smart Agent · TTS · Reward]:::ai
    DB[(SQLite: vaaksetu.db<br/>Agents · Sessions · Messages)]:::db
    INFRA[(Redis + PostgreSQL containers<br/>via docker-compose)]:::db
    TW[Twilio Calls + Media Stream]:::outbound

    FE --> BE
    BE --> AI
    AI --> BE
    BE --> DB
    BE --> TW
    TW --> BE
    BE -. optional .-> INFRA
```

**Current runtime note:** backend persistence is currently SQLite (`vaaksetu.db`). Redis/PostgreSQL services are available in docker-compose for infra alignment and future migration.

---

## 🛠️ Tech Stack

<table>
<tr>
<td valign="top" width="50%">

**AI / ML**
- `Sarvam STT (saaras:v3)` — primary ASR
- `AI4Bharat IndicWhisper` — fallback ASR
- `Sarvam-M` — conversational LLM via LangChain/OpenAI-compatible interface
- `pyannote.audio` — diarization support
- `LangGraph` — stateful conversational graph
- `LLM Judge (OpenAI-compatible)` — reward scoring

</td>
<td valign="top" width="50%">

**Application / Infra**
- `FastAPI` + `uvicorn` — backend APIs
- `Next.js 15` + `React 19` — frontend
- `SQLite (aiosqlite)` — active persistence
- `Redis` + `PostgreSQL (pgvector image)` — dockerized infra services
- `Twilio SDK` — outbound/media flow
- `Docker Compose` — local infrastructure bootstrap

</td>
</tr>
</table>

---

## ✨ Key Features

### 🗣️ Multi-Script & Code-Mixed Dynamic Language Switching
Supports seamless turn-by-turn language switching across 11 major Indic languages (Hindi, Kannada, Tamil, Telugu, Malayalam, Bengali, Marathi, Gujarati, Punjabi, Odia) and English. Includes a Unicode-based script detector in `tts.py` that identifies script block boundaries and handles Hinglish code-switching to change TTS voices dynamically mid-session.

### ⚡ Parallel Execution Loop (Low Latency)
To keep phone interactions responsive, the dialogue agent executes `SmartExtractor` (structured data collection) and `SmartDialogueAgent` (conversational response generation) in parallel using `asyncio.gather`. This architecture cuts total response latency in half, reducing turnaround times from ~60s down to ~30s.

### 🎙️ Barge-In & Interruption Support
*   **Twilio calls**: Configured with nested TwiML gather tags and `barge_in=True` in `webhook_server.py`, so the call immediately silences the AI speaker and starts STT recording the moment the caller speaks.
*   **Browser Playground**: Triggers browser synthesis cancel (`window.speechSynthesis.cancel()`) on typing or microphonic events in the Next.js frontend to dynamically interrupt the audio stream.

### 🧠 Reasoning Token Headroom & Think-tag Stripper
Integrated support for deep reasoning models (like `sarvam-30b`) by expanding `max_tokens` headroom to `4096` and implementing a robust trimming parser that cleans `<think>...</think>` tags (including truncated unclosed tags) and outputs safe conversational fallbacks.

### 🏥 Simplified Clinical Manager (Aarogya Sahayak)
Configured under `configs/healthcare.yaml` to triage patient cases naturally. Collects 7 core fields: `patient_name`, `age`, `gender`, `symptoms`, `symptom_duration`, `risk_level`, and `appointment_date_time`.

### 🔄 Config-Driven Domain Control
Domain behavior is governed by `configs/healthcare.yaml` and `configs/financial.yaml` plus dynamic agent settings from the Build UI.

### 🤖 RLAIF-Inspired Quality Loop
Completed sessions can be scored on politeness, accuracy, fluency, policy, and resolution quality for iterative agent tuning.

### 👥 Session + Transcript Persistence
Agents, sessions, messages, collected fields, and reward results are persisted and retrievable from API routes.

### 🖥️ Analysis Operations Dashboard
`/analysis` provides CRUD operations for agents and live interaction sessions.

### 📞 Autonomous Outbound Calling with Auto-Documentation
Twilio routes support initiating calls, streaming media, and retrieving call summaries after completion.

---

## 📞 Autonomous Outbound Calling with Auto-Documentation

```text
Trigger (API) -> Twilio outbound call
     -> TwiML webhook
     -> Media stream websocket
     -> ASR + conversation processing
     -> Structured summary + transcript state
```

**Current implementation paths**
- `POST /api/calls/outbound`
- `POST /api/calls/twiml`
- `POST /api/calls/status`
- `GET /api/calls/{call_sid}/summary`
- `WS /api/calls/media-stream`

---

## 🏥 Supported Domains

<table>
<tr>
<td width="50%" valign="top">

**Healthcare** (`configs/healthcare.yaml`)
- Patient identity + demographics
- Symptoms and duration
- History / medications / allergies
- Clinical and risk indicators
- Escalation triggers for emergency language

</td>
<td width="50%" valign="top">

**Financial Services** (`configs/financial.yaml`)
- Customer and loan identifiers
- Payment status and details
- Delay reasons and follow-up notes
- Escalation triggers for legal/fraud phrases

</td>
</tr>
</table>

> Adding new behavior can be done through new config + agent template updates.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Docker Desktop (optional but recommended)

### 1. Clone
```bash
git clone <your-repo-url>
cd iiitD
```

### 2. Configure Environment
Create/update root `.env` with required keys.

### 3. (Optional) Start Infra Containers
```bash
docker-compose up -d
```

### 4. Backend Setup
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
# source venv/bin/activate

pip install -r task4_output_layer/requirements.txt
python -m uvicorn task2_backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. Frontend Setup
```bash
cd frontend
npm install
npm run dev -- --port 3000
```

### 6. Verify
- Backend: `http://localhost:8000/health`
- Live UI: `http://localhost:8000/live`
- Frontend: `http://localhost:3000`

---

## 📁 Project Structure

```text
iiitD/
├── task1_ai_core/              # ASR, smart agent, graph agent, reward, TTS
├── task2_backend/              # FastAPI routes + DB layer
├── frontend/                   # Next.js dashboard UI
├── task4_output_layer/         # Standalone TTS/Twilio/simulation modules
├── configs/                    # Domain YAML configs (healthcare, financial)
├── docs/                       # Architecture and planning docs
├── tests/                      # Integration/support tests
├── docker-compose.yml          # Redis + PostgreSQL + ngrok
├── vaaksetu.db                 # Active SQLite DB file
└── README.md
```

---

## 🔑 Environment Variables

```env
# Sarvam
SARVAM_API_KEY=

# OpenAI-compatible judge endpoint
OPENAI_API_KEY=
OPENAI_BASE_URL=https://models.inference.ai.azure.com
MODEL_NAME=gpt-4o

# Twilio
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=
YOUR_PHONE_NUMBER=
PUBLIC_BASE_URL=

# Infra
REDIS_URL=redis://localhost:6379
DATABASE_URL=postgresql://postgres:vaaksetu@localhost:5432/vaaksetu

# HuggingFace / diarization
HF_TOKEN=

# App
APP_ENV=development
APP_PORT=8000
FRONTEND_URL=http://localhost:3000
```

| Key | Where to Get It |
|---|---|
| `SARVAM_API_KEY` | `https://dashboard.sarvam.ai` |
| `OPENAI_API_KEY` | `https://platform.openai.com/api-keys` |
| `TWILIO_*` | `https://console.twilio.com` |
| `HF_TOKEN` | `https://huggingface.co/settings/tokens` |

---

## 👥 Team

**Team AGNISHAKTI** — SRMIST Kattankulathur, Chennai

| Member | Role |
|---|---|
| **Shaurya Kesarwani** | Project Lead · AI Core · ASR Pipeline · Reward Loop |
| **Sudhanshu Kumar** | Backend · FastAPI · Database |
| **Md Nayaj** | Frontend · Dashboard UX |
| **Mouriyan** | TTS · Twilio Outbound · Simulation |

---

<div align="center">

<br/>

**VaakSetu** — *Bridging Languages, Automating Workflows*

Built by Team AGNISHAKTI

<br/>

</div>
