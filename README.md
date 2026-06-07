<!-- hero -->
<p align="center">
<img width="900" height="220" alt="hero_banner" src="https://github.com/user-attachments/assets/690d2223-5062-4b33-a4d2-fa60d1505fa5" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-00c8ff?style=flat-square&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/FastAPI-0.111-00FFB4?style=flat-square&logo=fastapi&logoColor=white"/>
  <img src="https://img.shields.io/badge/React-18-6496FF?style=flat-square&logo=react&logoColor=white"/>
  <img src="https://img.shields.io/badge/PostgreSQL-16-FFD050?style=flat-square&logo=postgresql&logoColor=white"/>
  <img src="https://img.shields.io/badge/Redis-7-FF5050?style=flat-square&logo=redis&logoColor=white"/>
  <img src="https://img.shields.io/badge/Anthropic-Claude-FF9050?style=flat-square"/>
  <img src="https://img.shields.io/badge/Pinecone-Vector_DB-32E6B4?style=flat-square"/>
  <img src="https://img.shields.io/badge/Docker-Compose-00B4FF?style=flat-square&logo=docker&logoColor=white"/>
</p>

<br/>

> **RegWatch** scrapes regulatory websites on a schedule, runs every update through Claude to extract meaning, stores it in a vector database for semantic search, and delivers it to a real-time dashboard — so your team stops copy-pasting PDFs into email threads and starts actually understanding what changed.

---

## What It Is

Compliance teams waste hours every week hunting for regulatory updates across dozens of government portals, financial bodies, and standards organizations. Most end up with a spreadsheet, a broken alert email, and a Friday panic.

RegWatch automates the boring part — finding what changed — and uses AI to do the hard part: figuring out *what it means for you*. Every regulation gets scraped, classified, summarized, embedded for semantic similarity search, and surfaced on a live dashboard with risk scores and alert routing. The whole thing runs on a single `docker compose up`.

---

## Tech Stack

<p align="center">
<img width="900" height="100" alt="techstack" src="https://github.com/user-attachments/assets/e1a53769-2ffe-4a1d-89ef-30d0c04bb7c1" />
</p>

| Layer | Technology | Why |
|---|---|---|
| Backend API | **FastAPI** (Python 3.12, async) | Non-blocking I/O; perfect for orchestrating multiple scrapers and AI calls concurrently |
| Database | **PostgreSQL 16** via `asyncpg` + SQLAlchemy | Durable storage for regulations, diffs, and audit history |
| Cache / Queue | **Redis 7** | Schedule locking, background task state, rate-limit counters |
| Scraping Engine | **Playwright** (headless Chromium) | Handles JS-rendered regulatory portals that `requests` simply can't reach |
| AI Engine | **Anthropic Claude** (`claude-sonnet-4-20250514`) | Classifies risk level, generates structured summaries, extracts obligation owners |
| Vector Search | **Pinecone** | Semantic similarity across thousands of regulation chunks — find related rules instantly |
| Notifications | **Resend** (email) + **Slack Webhooks** | Push alerts the moment a high-risk regulation changes |
| Frontend | **React 18 + TypeScript** (Vite) | Fast SPA, served via Nginx in production |
| Containerization | **Docker Compose** | One-command full stack deployment, zero dependency hell |

---

## System Architecture

<p align="center">
<img width="900" height="380" alt="architecture" src="https://github.com/user-attachments/assets/96ff5cd2-8b02-4975-855d-5921ed0b01e0" />
</p>

```
┌─────────────────────────────────────────────────────────────────────┐
│                          RegWatch System                            │
│                                                                     │
│  ┌──────────────┐   REST/WS    ┌──────────────────────────────┐    │
│  │  React SPA   │ ──────────▶  │       FastAPI Backend        │    │
│  │  (Vite/TS)   │ ◀──────────  │       /api/v1/*              │    │
│  └──────────────┘              └────────────┬─────────────────┘    │
│                                             │                       │
│              ┌──────────────────────────────┼───────────────────┐  │
│              ▼              ▼               ▼           ▼        │  │
│     ┌──────────────┐ ┌──────────┐ ┌──────────────┐ ┌─────────┐ │  │
│     │  PostgreSQL  │ │  Redis   │ │  Playwright  │ │ Resend/ │ │  │
│     │  (pgdata)    │ │  (cache) │ │  Scraper     │ │ Slack   │ │  │
│     └──────────────┘ └──────────┘ └──────┬───────┘ └─────────┘ │  │
│                                           │                      │  │
│                              ┌────────────┼───────────┐         │  │
│                              ▼            ▼           ▼         │  │
│                     ┌──────────────┐ ┌─────────┐ ┌─────────┐   │  │
│                     │  Claude AI   │ │Pinecone │ │ Sentry  │   │  │
│                     │  (Anthropic) │ │Vector DB│ │ (logs)  │   │  │
│                     └──────────────┘ └─────────┘ └─────────┘   │  │
└─────────────────────────────────────────────────────────────────────┘
```

The backend is the brain — it coordinates every other piece. Scrapers run on APScheduler jobs (every 24h for incremental watches, every 168h for a full pipeline refresh), dump raw HTML/PDF content into Postgres, hand it to Claude for structured classification, push embeddings to Pinecone, and trigger Resend/Slack when anything is flagged `HIGH`.

---

## Data Pipeline

<p align="center">
<img width="900" height="200" alt="dataflow" src="https://github.com/user-attachments/assets/3e238d74-3c1c-484a-a134-2277be312057" />
</p>

```
Scheduler fires
      │
      ▼
Playwright scrapes target URL
  (handles JS-rendered portals, respects rate limits)
      │
      ▼
Raw content diffed against last snapshot in Postgres
  (no change? skip. changed? continue.)
      │
      ▼
Claude classifies + summarizes
  → risk_level: HIGH | MEDIUM | LOW
  → obligation_owners: ["Legal", "Engineering", "Finance"]
  → effective_date, enforcement_date
  → plain-English summary
      │
      ▼
Embedding generated → pushed to Pinecone
  (enables "find me regulations similar to GDPR Art. 17")
      │
      ▼
Postgres updated, WebSocket broadcast to all dashboard clients
      │
      └──▶ if risk_level == HIGH → Resend email + Slack alert
```

---

## Dashboard

<p align="center">
<img width="900" height="420" alt="dashboard" src="https://github.com/user-attachments/assets/2045be6c-310b-4389-9709-f2490ddaf5a4" />
</p>

The React frontend (served on port `5173` dev / `80` prod) gives you:

- **Live overview** — active regulation count, new-today count, critical count, coverage percentage
- **Regulation table** — sortable, filterable, with inline risk badges and direct links to AI summaries
- **AI Analysis modal** — full Claude-generated breakdown: what changed, who owns it, what's the deadline
- **Semantic search** — powered by Pinecone; find related regulations by meaning, not just keywords
- **Alert history** — timeline of all notifications sent, with links to the triggering change

---

## Repo Structure

```
RegWatch/
│
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI app factory, CORS, lifespan hooks
│   │   ├── api/              # Route handlers (regulations, alerts, search, health)
│   │   ├── models/           # SQLAlchemy ORM models
│   │   ├── schemas/          # Pydantic request/response schemas
│   │   ├── services/
│   │   │   ├── scraper.py    # Playwright orchestrator
│   │   │   ├── ai.py         # Claude integration (classify, summarize, embed)
│   │   │   ├── vector.py     # Pinecone upsert + query
│   │   │   └── notify.py     # Resend + Slack dispatch
│   │   ├── tasks/
│   │   │   └── scheduler.py  # APScheduler: watcher (24h), full pipeline (168h)
│   │   └── core/
│   │       ├── config.py     # Pydantic Settings, env validation
│   │       └── db.py         # Async SQLAlchemy engine + session factory
│   ├── alembic/              # DB migration history
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── components/       # Reusable UI components
│   │   ├── pages/            # Dashboard, Regulations, AI Summary, Alerts
│   │   ├── hooks/            # Data-fetching hooks (React Query)
│   │   ├── api/              # Typed API client (axios)
│   │   └── types/            # Shared TypeScript interfaces
│   ├── package.json
│   └── Dockerfile
│
├── scripts/                  # DB seed, migration helpers, manual scrape triggers
│
├── docker-compose.yml        # Full stack: postgres, redis, backend, frontend
└── .env.example              # All required env vars documented
```

---

## Project Setup

### Prerequisites

- Docker + Docker Compose (v2.x)
- An [Anthropic API key](https://console.anthropic.com/) (required for AI features)
- Optional: Pinecone API key (semantic search), Resend API key (email alerts), Slack Webhook URL

### Run in 60 seconds

```bash
# 1. Clone
git clone https://github.com/sat1828/RegWatch.git
cd RegWatch

# 2. Configure
cp .env.example .env
# → Set ANTHROPIC_API_KEY at minimum
# → Set PINECONE_API_KEY, RESEND_API_KEY, SLACK_WEBHOOK_URL if you want full features

# 3. Start everything
docker compose up --build

# Backend:  http://localhost:8000
# Frontend: http://localhost:5173
# API docs: http://localhost:8000/docs
```

### Development (without Docker)

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Start Postgres + Redis separately (or use docker compose for just infra)
docker compose up postgres redis -d

# Run migrations
alembic upgrade head

# Start backend
uvicorn app.main:app --reload --port 8000

# Frontend (separate terminal)
cd frontend
npm install
npm run dev    # Vite dev server at http://localhost:5173
```

---

## Environment Variables

All variables from `.env.example`:

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | ✅ | Async PostgreSQL URL (`postgresql+asyncpg://...`) |
| `DATABASE_SYNC_URL` | ✅ | Sync URL for Alembic migrations |
| `REDIS_URL` | ✅ | Redis connection (`redis://localhost:6379/0`) |
| `ANTHROPIC_API_KEY` | ✅* | Claude API key — falls back to mock if unset |
| `ANTHROPIC_MODEL` | — | Defaults to `claude-sonnet-4-20250514` |
| `PINECONE_API_KEY` | — | Vector search disabled if unset |
| `PINECONE_INDEX_NAME` | — | Defaults to `regwatch` |
| `RESEND_API_KEY` | — | Email alerts disabled if unset |
| `SLACK_WEBHOOK_URL` | — | Slack alerts disabled if unset |
| `API_KEY` | ✅ | Static API key for inter-service auth |
| `SCHEDULER_WATCHER_INTERVAL_HOURS` | — | How often to check tracked regulations (default: 24) |
| `SCHEDULER_FULL_PIPELINE_INTERVAL_HOURS` | — | Full re-scrape interval (default: 168 = 1 week) |
| `MAX_CONCURRENT_SCRAPES` | — | Playwright concurrency cap (default: 5) |
| `LOG_LEVEL` | — | `DEBUG` / `INFO` / `WARNING` |
| `SENTRY_DSN` | — | Error tracking — silent if unset |

`*` Set to empty string to run in mock mode (AI responses are stubbed, useful for UI dev).

---

## API Reference

Interactive docs at `http://localhost:8000/docs` (Swagger UI) or `/redoc`.

Key endpoints:

```
GET  /api/v1/regulations          List all tracked regulations (paginated, filterable)
GET  /api/v1/regulations/{id}     Get regulation detail + AI summary
POST /api/v1/regulations          Add a new URL to track
GET  /api/v1/regulations/search   Semantic search via Pinecone
GET  /api/v1/alerts               Alert history
POST /api/v1/pipeline/trigger     Manually kick off a scrape + classify run
GET  /health                      Health check (DB + Redis + AI service status)
```

---

## How the AI Classification Works

When a scrape returns new content, the service sends the diff to Claude with a structured prompt that requests a JSON response:

```python
{
  "risk_level": "HIGH" | "MEDIUM" | "LOW",
  "summary": "Plain-English description of what changed",
  "obligation_owners": ["Legal", "Engineering", "Security"],
  "effective_date": "2025-07-01",
  "enforcement_date": "2026-01-01",
  "key_changes": ["Change 1", "Change 2"],
  "action_required": true | false
}
```

The same content then gets embedded via Claude's embedding endpoint and upserted to Pinecone with the regulation's metadata as payload, enabling similarity search across your full regulatory corpus.

---

## Scheduler

Two recurring jobs configured via APScheduler, backed by Redis for distributed locking so the same job never runs twice across replicas:

| Job | Interval | What it does |
|---|---|---|
| `watcher` | Every 24 hours | Fetches watched URLs, diffs against stored snapshot, triggers classify → notify pipeline on changes |
| `full_pipeline` | Every 168 hours (1 week) | Complete re-scrape of every tracked URL regardless of change detection |

Both intervals are environment-configurable, so you can tighten them for high-stakes regulatory environments.

---

## Contributing

1. Fork and clone
2. `docker compose up postgres redis -d` to get infra
3. `cd backend && uvicorn app.main:app --reload` for hot-reload dev
4. Make your changes. Keep them focused — one feature or fix per PR.
5. Run `pytest` in `/backend` before opening a PR

There's no issue template drama. Open an issue describing the problem, we'll talk.

---

## License

MIT — do what you want, just don't remove the attribution.

---

<p align="center">
  Built to stop regulatory surprises before they become Friday-night emergencies.
</p>
