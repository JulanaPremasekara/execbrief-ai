# ExecBrief AI

ExecBrief AI turns an executive question into an evidence-backed briefing with text, charts, and recommendations.

The demo uses fictional data for **Nexora Solutions (Pvt) Ltd**. The application is a single monorepo:

- `apps/frontend` — React, Vite, Tailwind CSS, Recharts, and the browser SSE client.
- `apps/backend` — FastAPI, application services, domain contracts, analytics, LangChain ingestion/retrieval, and the SSE API.
- Supabase PostgreSQL with `pgvector` — structured KPI data and semantic document search.
- Hosted Hugging Face inference — query planning and response generation. The language model is never hosted locally.

The code follows Clean Architecture. API routes handle HTTP and SSE serialization, application services coordinate use cases, domain contracts define business-facing interfaces, and infrastructure modules connect external systems.

## Current status

The Phase 4 integration is implemented and automated tests pass. The default mode is `mock`, so a new developer can run the interface without external accounts. `live` mode connects Supabase, LangChain retrieval, verified analytics, and Hugging Face inference.

Live acceptance still depends on valid local Supabase and Hugging Face configuration. See [docs/progress.md](docs/progress.md) for the latest verification record.

## Prerequisites

- Python 3.11 or newer (tested with Python 3.13).
- Node.js 22.13 or newer and npm.
- A Supabase project for live mode.
- A Hugging Face token and a chat-capable hosted model for live mode.

The commands below use PowerShell on Windows. On macOS or Linux, replace `.venv\Scripts\python` with `.venv/bin/python` and `npm.cmd` with `npm`.

## Quick start: offline demo

The offline demo needs no database or model credentials.

From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r apps/backend/requirements.lock -e "./apps/backend[test]"
```

Start the API in one terminal:

```powershell
.\.venv\Scripts\python -m uvicorn execbrief.main:app --reload
```

Start the frontend in a second terminal:

```powershell
cd apps/frontend
npm.cmd ci
npm.cmd run dev
```

Open [http://localhost:5173](http://localhost:5173), then ask:

> How is our company performing over the last six months?

Mock mode returns a fixed, clearly labeled demonstration. It shows the intended sequence: text, line chart, text, bar chart, and recommendations. Include `text only` in a question to exercise the text-only response.

## Configure live mode

Create a local environment file. It is ignored by Git and must never be committed:

```powershell
Copy-Item .env.example .env.local
```

Set these values in `.env.local`:

| Variable | Purpose |
| --- | --- |
| `EXECBRIEF_MODE=live` | Selects the real retrieval, analytics, and inference pipeline. |
| `DATABASE_URL` | Supabase PostgreSQL Session Pooler URI on port `5432`. |
| `HF_TOKEN` | Hugging Face token with inference-provider access. |
| `HF_MODEL` | Hosted chat/instruction model ID available to your account. |
| `HF_PROVIDER=auto` | Hugging Face provider selection; `auto` is the default. |
| `FRONTEND_ORIGIN=http://localhost:5173` | Allowed browser origin for the API. |

To get `DATABASE_URL`, open your Supabase project, select **Connect**, choose the **Session pooler** PostgreSQL connection string, and use port `5432`. Replace its password with your database password and URL-encode special characters. Do not use the transaction pooler on port `6543`; the application requires session affinity. SSL is enforced by the backend.

Do not put any secret in a `VITE_` variable. Vite variables are available to browser code. Existing process environment variables take precedence over `.env.local`.

## Prepare live data

The repository generates one deterministic fictional dataset shared by six CSV files and six PDF reports. Run these commands from the repository root:

```powershell
.\.venv\Scripts\python scripts/generate_synthetic_data.py
.\.venv\Scripts\python scripts/check_database.py
.\.venv\Scripts\python scripts/seed_database.py
.\.venv\Scripts\python scripts/ingest_documents.py
.\.venv\Scripts\python scripts/check_hf.py
```

These steps generate May–October 2026 data, verify Supabase and `pgvector`, apply migrations, import KPI records, ingest documents with LangChain, create local CPU embeddings, and check Hugging Face access. The database uses the `execbrief` schema and discovers the actual `pgvector` schema.

## Run the live application

Restart the backend after changing `.env.local`:

```powershell
.\.venv\Scripts\python -m uvicorn execbrief.main:app --reload
```

Keep the frontend running with `npm.cmd run dev` and submit the six-month question again. Live chart rows come from backend analytics. The model can choose a chart specification, but it cannot provide chart data, execute SQL, or execute generated code.

## Streaming behavior

`POST /api/chat/stream` emits the documented event types in order: `status`, `block_start`, `text_delta`, `block_end`, `chart`, `error`, and `done`. See [docs/api-contracts.md](docs/api-contracts.md).

Live mode currently uses a **validated-block fallback**. The complete structured model response is validated before blocks are displayed, so text is emitted per validated block rather than token by token. This is labeled in the UI. No artificial delays are added. True hosted token streaming has not been claimed because provider capability is not verified.

The frontend keeps completed blocks and sources when a later block fails or the user cancels. A synchronous database or embedding operation already running in a worker cannot be forcibly interrupted; its resources are disposed when the worker finishes.

## Test and build

```powershell
.\.venv\Scripts\python -m pytest apps/backend/tests -q
cd apps/frontend
npm.cmd test
npm.cmd run build
```

Tests mock paid/external services and do not require inference quota. Current results are recorded in [docs/progress.md](docs/progress.md); skipped live tests are not successful live checks.

To opt into live database tests and the exact executive-question workflow check:

```powershell
cd D:\execbrief-ai
$env:RUN_SUPABASE_TESTS="1"
.\.venv\Scripts\python -m pytest apps/backend/tests/integration -q --tb=no
Remove-Item Env:RUN_SUPABASE_TESTS
.\.venv\Scripts\python scripts/check_workflow.py
```

The workflow check uses local credentials and may consume Hugging Face quota. It prints only sanitized status messages.

## Troubleshooting

**The UI cannot connect:** confirm the backend runs on port `8000`, the frontend on port `5173`, and the Vite proxy is active.

**The database hostname cannot be resolved:** copy a current Session Pooler URI from Supabase Dashboard → Connect, check port `5432`, network access, and the rotated password. Never paste the URI into chat or commit it.

**The Hugging Face check fails:** confirm `HF_TOKEN` has inference access and `HF_MODEL` is a hosted chat/instruction model supported by the provider.

**The response says validated blocks:** this is expected until a compatible hosted model and safe incremental response contract are verified. It is not token-level streaming.

## Production boundary

This repository contains the application integration and a backend Dockerfile, but it is not a complete production deployment. Before exposing it to users, add authentication, authorization, rate limiting, secret management, observability, backups, HTTPS, an SSE-compatible reverse proxy, and deployment-specific readiness checks. The Vite server is a development server and should not be used as the production frontend server.

For implementation details, read [AGENTS.md](AGENTS.md), [docs/architecture.md](docs/architecture.md), [docs/implementation-plan.md](docs/implementation-plan.md), [docs/ai-workflow.md](docs/ai-workflow.md), and [docs/rag-pipeline.md](docs/rag-pipeline.md).
