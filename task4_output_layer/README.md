# VaakSetu
### AI-Powered Multilingual Conversational Intelligence Platform
**Team AGNISHAKTI | SRMIST Chennai | Hack2Future 2.0**

---

## Team
| Member | Task | Role |
|---|---|---|
| Shaurya Kesarwani | Task 1 — AI Core | Project Lead + ASR + Agent + RLAIF |
| Sudhanshu Kumar | Task 2 — Backend | FastAPI + NLP Pipeline + Database |
| Md Nayaj | Task 3 — Frontend | React UI + Dashboard + Review Interface |
| Mouriyan | Task 4 — Output Layer | TTS + Outbound Calls + Simulation |

---

## Quick Setup (Run in this exact order)

### 1. Prerequisites — Install These First
- Python 3.11 → https://python.org/downloads
- Node.js 20 → https://nodejs.org
- Docker Desktop → https://docker.com/products/docker-desktop
- Git → https://git-scm.com

### 2. Clone the Repo
git clone https://github.com/your-username/vaaksetu.git
cd vaaksetu

### 3. Install Python Packages
pip install -r requirements.txt

### 4. Install spaCy Language Model
python -m spacy download en_core_web_sm

### 5. Start Redis and PostgreSQL (Docker must be running)
docker-compose up -d

### 6. Verify Services Are Running
docker ps
# You should see: vaaksetu_redis and vaaksetu_postgres both showing "Up"

### 7. Start the Backend
uvicorn task2_backend.main:app --reload --port 8000
# Open http://localhost:8000/docs to see the API

### 8. Start the Frontend (in a new terminal)
cd task3_frontend
npm install
npm start
# Opens http://localhost:3000

---

## Folder Structure
- task1_ai_core/     → Shaurya — ASR, Agent, RLAIF
- task2_backend/     → Sudhanshu — FastAPI, NLP, Database
- task3_frontend/    → Nayaj — React UI
- task4_output_layer/ → Mouriyan — TTS, Twilio, Simulation
- configs/           → YAML domain configurations
- tests/             → Integration tests

---

## Branch Naming
- task1-ai-core     (Shaurya)
- task2-backend     (Sudhanshu)
- task3-frontend    (Nayaj)
- task4-output-layer (Mouriyan)

All pull requests go to Shaurya for review and merge.
```

---

### File 7 — Placeholder `README.md` in Each Task Folder

Create a simple `README.md` inside each task folder so teammates know they are in the right place:

**`task1_ai_core/README.md`:**
```
# Task 1 — AI Core
Owner: Shaurya Kesarwani
Files to create here: asr.py, agent.py, reward_engine.py
See the main Solution Blueprint document for full task guide.
```

**`task2_backend/README.md`:**
```
# Task 2 — Backend
Owner: Sudhanshu Kumar
Files to create here: main.py, nlp_pipeline.py, database.py, models.py
See the main Solution Blueprint document for full task guide.
```

**`task3_frontend/README.md`:**
```
# Task 3 — Frontend
Owner: Md Nayaj
Run: npm install && npm start
See the main Solution Blueprint document for full task guide.
```

**`task4_output_layer/README.md`:**
```
# Task 4 — Output Layer
Owner: Mouriyan
Files to create here: tts.py, outbound_call.py, simulation.py
See the main Solution Blueprint document for full task guide.
```

---

## Step 7 — Make Your First Commit and Push Everything
```
git add .
git commit -m "Initial setup: folder structure, configs, env, docker, requirements"
git push origin main
```

Go to GitHub and refresh the page — you should see all the folders and files now visible in the repo.

---

## Step 8 — Verify the Setup Locally Before Tagging Others

Run these checks yourself before telling teammates to clone:
```
# Check Python packages install cleanly
pip install -r requirements.txt

# Check Docker services start
docker-compose up -d
docker ps

# Check .env is readable
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('SARVAM:', os.getenv('SARVAM_API_KEY')[:8], '...')"
# Mouriyan's AI Voice Agent

This project contains three independent modules for building a multilingual, human-sounding AI Voice Agent.

## Sub-tasks
1. **TTS (`tts/`)**: Converts text to natural-sounding Indian speech using Sarvam AI.
2. **Twilio (`twilio_calls/`)**: Automates outbound phone calls and handles speech gathering via a Flask webhook.
3. **Simulation (`simulation/`)**: A Bot-vs-Bot testing engine to evaluate how the AI handles different customer personas (angry, confused, evasive, cooperative).

## Setup Instructions

### 1. Install Dependencies
Make sure you have Python 3.8+ installed.
```bash
# Optional: Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # Mac/Linux
# .venv\Scripts\activate   # Windows

# Install required packages
pip install -r requirements.txt
```

### 2. Configure API Keys
Copy the example environment file and add your actual keys:
```bash
cp .env.example .env
```
Edit `.env` and add:
- `SARVAM_API_KEY` (from dashboard.sarvam.ai)
- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`
- `TWILIO_PHONE_NUMBER`
- `YOUR_PHONE_NUMBER` (your actual phone number for testing)

---

## Running the Tests (Mouriyan's Independent Workflow)

### Test 1: TTS Module (Type text → hear speech)
This tests the connection to Sarvam AI.
```bash
python -m tts.test_tts
```

### Test 2: Twilio Outbound Calls (Your phone rings)
This requires three terminal windows.

**Terminal 1 (Webhook Server):**
```bash
python -m twilio_calls.webhook_server
```

**Terminal 2 (Ngrok Tunnel):**
```bash
ngrok http 5000
```
*Copy the `Forwarding` URL (e.g., `https://abc1234.ngrok-free.app`)*

**Terminal 3 (Test Script):**
```bash
# Add the URL to your .env file as NGROK_URL=..., then run:
python -m twilio_calls.test_call
```

### Test 3: Customer Persona Simulation (Bot talks to Bot)
This runs the behavior testing engine.
```bash
python -m simulation.test_simulation
```
You can optionally enable TTS playback to actually hear the AI responding to the simulated customer text!
