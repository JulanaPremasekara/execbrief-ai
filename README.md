# ExecBrief AI

Executive briefings for fictional Nexora Solutions: React/Recharts, FastAPI, LangChain retrieval, Supabase PostgreSQL/pgvector analytics and hosted Hugging Face inference. Domain contracts, application orchestration and infrastructure adapters remain separate.

Phase 4 connects the live pipeline to the existing SSE interface. Automated tests mock external services. Live acceptance remains blocked by local Supabase/HF configuration; see [progress](docs/progress.md).

## Local setup (PowerShell)

Use Python 3.11+ (tested with 3.13) and Node 22.13+. From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r apps/backend/requirements.lock -e "./apps/backend[test]"
Copy-Item .env.example .env.local
```

Copy the example only if `.env.local` does not already exist. Configure secrets locally; never paste them in chat or expose them in `VITE_` variables. Existing process environment variables take precedence over `.env.local`.

- `DATABASE_URL`: in your existing Supabase dashboard, open **Connect**, select the **Session pooler** PostgreSQL URI on port **5432**, substitute your database password and URL-encode special characters. Do not use transaction pooling on port 6543. SSL is enforced.
- `HF_TOKEN`: Hugging Face token with inference-provider access.
- `HF_MODEL`: hosted chat/instruction model ID available to your account/provider. Availability is not assumed. `HF_PROVIDER=auto` is the default.
- `FRONTEND_ORIGIN=http://localhost:5173`.
- `EXECBRIEF_MODE=live` enables retrieval/analytics/inference. Default `mock` returns a fixed, visibly labeled demonstration without external services.

For live mode, generate fictional data, verify access, migrate/import and ingest:

```powershell
.\.venv\Scripts\python scripts/generate_synthetic_data.py
.\.venv\Scripts\python scripts/check_database.py
.\.venv\Scripts\python scripts/seed_database.py
.\.venv\Scripts\python scripts/ingest_documents.py
.\.venv\Scripts\python scripts/check_hf.py
```

Seeding runs Alembic. Setup discovers pgvector's actual schema and enables it if missing, requiring database permission. Relational/vector tables use `execbrief`. Ingestion downloads MiniLM for local CPU embeddings; language generation remains hosted. Live setup has not succeeded against the currently configured services. See [RAG setup](docs/rag-pipeline.md) for provenance and repeat-ingestion behavior.

Start the backend:

```powershell
.\.venv\Scripts\python -m uvicorn execbrief.main:app --reload
```

In another terminal:

```powershell
cd apps/frontend
npm.cmd ci
npm.cmd run dev
```

Open http://localhost:5173. Vite proxies `/api` to port 8000. Ask **"How is our company performing over the last six months?"**. Live charts use backend analytics; mock charts are fixtures. History persists in browser memory until reload. **Stop response** aborts the request while retaining displayed content.

## Streaming and limitations

The seven-event [SSE contract](docs/api-contracts.md) preserves text/chart order and stable IDs. Live mode uses **validated-block fallback**, visibly labeled: complete structured output is validated before blocks are emitted. Text arrives once per validated block; this is not token streaming. There are no artificial display delays. React may batch blocks received together into one paint.

Hosted token-stream capability remains unverified because the configured provider check fails. Raw unvalidated model tokens are never displayed. Genuine token streaming requires a successful capability check and a grounding-safe incremental response contract. Factual prose is extractive; recommendations are suggestions, not mechanically proven conclusions. See [AI workflow](docs/ai-workflow.md).

Cancellation closes asynchronous inference and request resources. Blocking database/embedding work already running in a worker cannot be forcibly stopped; initialization resources are disposed when the worker completes. Production authentication, access controls, rate limits, deployment packaging and an SSE proxy have not been implemented or deployment-tested. Vite's development proxy is not a production server.

## Verification

```powershell
.\.venv\Scripts\python -m pytest apps/backend/tests -q
cd apps/frontend
npm.cmd test
npm.cmd run build
```

Automated inference is mocked and consumes no paid inference quota. Opt into live checks from the repository root:

```powershell
$env:RUN_SUPABASE_TESTS="1"
.\.venv\Scripts\python -m pytest apps/backend/tests/integration -q --tb=no
Remove-Item Env:RUN_SUPABASE_TESTS
.\.venv\Scripts\python scripts/check_workflow.py
```

The workflow check submits the exact executive question through FastAPI in-process with real configured services. It may consume inference quota; it is not a browser walkthrough. Actual results and remaining acceptance checks are in [progress](docs/progress.md).
