# NexClinicalMind

**Autonomous AI compliance system for pharmaceutical clinical trials.**  
Five AI agents scan your trial data, identify FDA violations, generate legal guidance, create remediation plans, and decide whether your submission is ready — in under a minute.

[![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.1.3-black?logo=flask)](https://flask.palletsprojects.com)
[![Gemini](https://img.shields.io/badge/Gemini-2.5%20Flash-4285F4?logo=google&logoColor=white)](https://ai.google.dev)
[![MCP](https://img.shields.io/badge/MCP-1.27.1-purple)](https://modelcontextprotocol.io)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Demo](https://img.shields.io/badge/Live%20Demo-demo.nexintai.com-orange)](https://demo.nexintai.com)

---

## Live Demo

**[demo.nexintai.com](https://demo.nexintai.com)**

---

## What Problem Does This Solve?

Before a pharmaceutical company can submit a drug for FDA approval, every piece of clinical trial data must conform to **CDISC SDTM standards** — a strict data format the FDA requires. Manual compliance review is:

- **Slow** — teams of regulatory affairs specialists review data for weeks
- **Error-prone** — missing a single required field can block an entire submission
- **Expensive** — regulatory consultants charge hundreds of dollars per hour

NexClinicalMind automates this entire workflow with AI agents that run in seconds.

---

## How It Works

Five agents run in sequence, each passing results to the next:

```
 ┌──────────────────────────────────────────────────────────────────┐
 │                        ONE SCAN (~50 seconds)                    │
 │                                                                  │
 │  [1] SENTINEL     Monitors data pipelines for failures           │
 │        ↓          Gemini AI diagnoses root cause                 │
 │  [2] GUARDIAN     Checks CDISC compliance rules                  │
 │        ↓          Flags violations by severity (HIGH/MED/LOW)    │
 │  [3] COUNSEL      Looks up the exact FDA regulation broken       │
 │        ↓          Gemini AI writes legal guidance per violation  │
 │  [4] REMEDIATE    Generates step-by-step fix plans               │
 │        ↓          Triggers pipeline reruns automatically         │
 │  [5] PACKAGER     Final gate: READY or ON HOLD                   │
 └──────────────────────────────────────────────────────────────────┘
```

All events are written to an immutable **21 CFR Part 11 compliant audit trail**.

---

## Architecture

```
Browser (index.html — GitHub Pages)
    │
    │  POST /api/start  {X-API-Key header}
    ▼
Flask API (api.py — Google Cloud Run, port 5000)
    │
    │  background thread
    ▼
5-Agent Pipeline ──────────────────────────────────────────────┐
    │                                                           │
    │  MCP protocol (port 8000)          ask_gemini()           │
    ▼                                        ▼                  │
MCP Server (mcp_server.py)          Gemini 2.5 Flash           │
    │                                (Google AI API)            │
    ▼                                                           │
Mock Tools                                                      │
  airflow_mock.py   (pipelines)                                 │
  dbt_mock.py       (CDISC transforms)                          │
  snowflake_mock.py (data quality)                              │
    │                                                           │
    └──────────────────────────────────────────────────────────┘
                              │
                              ▼
                    audit_trail.json
                  (21 CFR Part 11 compliant)
```

---

## Features

- **5 autonomous agents** — each specialised: monitor → validate → advise → fix → gate
- **Real-time dashboard** — live output streaming per agent, audit log table
- **3 scan scenarios** — `violation`, `consent`, `clean` modes for demo/testing
- **AI legal guidance** — Gemini cites exact FDA regulation (e.g. 21 CFR 312.32) per violation
- **AI remediation briefs** — step-by-step fix plans with sign-off requirements
- **Immutable audit trail** — every event logged with `audit_id`, ISO timestamp, 21 CFR Part 11 standard
- **API key authentication** — all endpoints protected via `X-API-Key` header
- **MCP integration** — agents communicate with tools via Model Context Protocol
- **CLI mode** — run the same pipeline from the terminal via `main.py`

---

## Tech Stack

| Layer | Technology |
|---|---|
| AI Model | Google Gemini 2.5 Flash (via `google-genai` SDK) |
| Agent Tools | Model Context Protocol (MCP) + FastMCP |
| Web API | Flask 3.1 + Flask-CORS |
| Frontend | Vanilla HTML/CSS/JS (single file, no framework) |
| Hosting | Google Cloud Run (API) + GitHub Pages (frontend) |
| Data Sources | Apache Airflow, dbt, Snowflake *(mocked for demo)* |
| Compliance | 21 CFR Part 11, CDISC SDTM v3.3 |

---

## Project Structure

```
nexclinicalmind/
├── api.py                  # Flask API + 5 phase functions + scan orchestrator
├── main.py                 # CLI entry point
├── mcp_server.py           # MCP server — 6 tools on port 8000
├── index.html              # Single-page dashboard (GitHub Pages)
├── requirements.txt        # Pinned dependencies
├── .env                    # Secrets — never committed (see .gitignore)
│
├── agents/
│   ├── sentinel.py         # Agent 1: pipeline monitor
│   ├── guardian.py         # Agent 2: CDISC compliance checker
│   ├── counsel.py          # Agent 3: FDA regulatory advisor
│   ├── remediate.py        # Agent 4: fix planner + pipeline rerunner
│   └── packager.py         # Agent 5: submission gatekeeper
│
├── tools/                  # Mock data sources
│   ├── airflow_mock.py     # Simulates Apache Airflow
│   ├── dbt_mock.py         # Simulates dbt
│   └── snowflake_mock.py   # Simulates Snowflake
│
└── utils/
    ├── gemini_brain.py     # ask_gemini(prompt) → str
    ├── audit_log.py        # log_event() → audit_trail.json
    └── mcp_client.py       # MCP tool caller (persistent async loop)
```

---

## Quickstart

### Prerequisites

- Python 3.11+
- A [Google Gemini API key](https://aistudio.google.com/app/apikey)

### 1. Clone & install

```bash
git clone https://github.com/NexIntAI/NexClinicalMind.git
cd NexClinicalMind
pip install -r requirements.txt
```

### 2. Configure secrets

```bash
cp .env.example .env   # or create .env manually
```

Edit `.env`:

```
GEMINI_API_KEY=your_gemini_api_key_here
API_KEY=choose_any_secret_key_here
```

### 3. Start the MCP server (Terminal 1)

```bash
python mcp_server.py
# INFO: Uvicorn running on http://0.0.0.0:8000
```

### 4. Start the Flask API (Terminal 2)

```bash
python api.py
# Running on http://127.0.0.1:5000
```

### 5. Open the dashboard

Open `index.html` directly in your browser, enter your `API_KEY` when prompted, then click **Run Scan**.

### Optional: CLI mode

```bash
python main.py
```

Runs the full 5-agent pipeline in your terminal with no server required.

---

## Scan Modes

Select a mode before running a scan to control what scenario is simulated:

| Mode | What happens | Result |
|---|---|---|
| `violation` | One random pipeline fails; 47 records missing `AETERM` field | **ON HOLD** — 2 HIGH violations |
| `consent` | Patient Records Sync fails; 23 subjects missing informed consent dates | **ON HOLD** — 2 HIGH violations |
| `clean` | All pipelines healthy, all CDISC checks pass | **READY** — submission approved |

---

## API Reference

All endpoints require the `X-API-Key` header.

### `POST /api/start`

Start a compliance scan.

```bash
curl -X POST http://localhost:5000/api/start \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{"mode": "violation"}'
```

```json
{"status": "started", "mode": "violation"}
```

**Errors:** `400` invalid mode · `401` bad key · `409` scan already running

---

### `GET /api/state`

Get the live scan state (poll this during a scan).

```bash
curl http://localhost:5000/api/state -H "X-API-Key: your-key"
```

```json
{
  "status": "running",
  "scan_mode": "violation",
  "agents": {
    "sentinel": {"status": "done", "elapsed": 7.1, "output": [...]},
    "guardian": {"status": "running", "elapsed": null, "output": [...]},
    ...
  },
  "summary": {
    "violations_found": 2,
    "submission_status": "ON HOLD",
    "total_elapsed": 48.8
  },
  "audit_log": [...]
}
```

---

### `POST /api/reset`

Reset all state back to idle.

```bash
curl -X POST http://localhost:5000/api/reset -H "X-API-Key: your-key"
```

```json
{"status": "reset"}
```

---

## Audit Trail

Every significant event is written to `audit_trail.json` (append-only, one entry per line):

```json
{
  "audit_id": "AUD-194510",
  "timestamp": "2026-05-21T13:15:09.105786Z",
  "agent": "SENTINEL",
  "action": "PIPELINE_SCAN",
  "detail": "Scanned 4 pipelines. Found 1 failure(s).",
  "severity": "INFO",
  "standard": "21 CFR Part 11",
  "system": "NexClinicalMind v1.0",
  "immutable": true
}
```

Severity levels: `INFO` · `HIGH` · `CRITICAL`

---

## Deployment

The production system runs on Google Cloud Platform:

| Component | Platform | URL |
|---|---|---|
| Flask API + MCP server | Google Cloud Run | `nexclinicalmind-api-266546549476.us-central1.run.app` |
| Frontend | GitHub Pages | `demo.nexintai.com` |

### Deploy to Cloud Run

```bash
docker build -f Dockerfile.api -t nexclinicalmind-api .
gcloud run deploy nexclinicalmind-api \
  --image nexclinicalmind-api \
  --platform managed \
  --region us-central1 \
  --set-env-vars GEMINI_API_KEY=...,API_KEY=...,ALLOWED_ORIGIN=https://demo.nexintai.com
```

### Environment variables (Cloud Run)

| Variable | Purpose |
|---|---|
| `GEMINI_API_KEY` | Google Gemini API authentication |
| `API_KEY` | Dashboard authentication key |
| `ALLOWED_ORIGIN` | CORS allowed origin (default: `https://demo.nexintai.com`) |
| `FLASK_ENV` | Set to `development` to allow localhost CORS |
| `PORT` | Server port (Cloud Run sets this automatically) |

---

## Extending to Production

The mock tools are drop-in replaceable. To connect real infrastructure:

| File | Replace with |
|---|---|
| `tools/airflow_mock.py` | Airflow REST API client |
| `tools/dbt_mock.py` | dbt Cloud API or dbt Core runner |
| `tools/snowflake_mock.py` | Snowflake Python connector |

The agents, MCP server, and API need no changes — they only interact with the tool interface, not the implementation.

---

## CDISC Domains Covered

| Domain | Full Name | Key Requirement Checked |
|---|---|---|
| AE | Adverse Events | `AETERM` not null, MedDRA coding |
| DM | Demographics | `USUBJID` unique, `RFSTDTC` present |
| LB | Lab Results | `LBORRESU` valid unit codes |
| IC | Informed Consent | `ICDTC` present, `ICVERSION` current |

---

## FDA Regulations Referenced

| Regulation | Applies to |
|---|---|
| 21 CFR 312.32 | IND Safety Reports — AE domain |
| 21 CFR Part 50 | Protection of Human Subjects — DM + IC domains |
| 21 CFR 312.23 | IND Content and Format — LB domain |
| 21 CFR Part 11 | Electronic Records and Signatures — audit trail |
| ICH E6 (R2) | Good Clinical Practice — data integrity |

---

## Known Limitations

- All data sources are **mocks** — no real Airflow/dbt/Snowflake connections
- MCP server is **local only** — must run on the same host as Flask
- **One scan at a time** — concurrent scans are rejected with 409
- **No scan cancellation** — once started, runs to completion
- Frontend polls every **800ms** — no WebSocket
- `audit_trail.json` grows indefinitely — `reset` clears memory but not the file

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "Add your feature"`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## Built With

- [Google Gemini API](https://ai.google.dev) — AI reasoning and text generation
- [Model Context Protocol](https://modelcontextprotocol.io) — standardised AI tool calls
- [FastMCP](https://github.com/jlowin/fastmcp) — MCP server framework
- [Flask](https://flask.palletsprojects.com) — web API framework
- [CDISC SDTM](https://www.cdisc.org/standards/foundational/sdtm) — clinical data standard

---

*NexClinicalMind is a demonstration project. It is not intended for use in actual clinical trial submissions.*
