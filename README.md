# ExecBrief AI

Phase 3 hosted inference and verified analytics are available through EXECBRIEF_MODE=live. See [docs/ai-workflow.md](docs/ai-workflow.md) for setup, formulas, grounding restrictions and verification limits. Default mode remains mock.

Phase 2 data setup and ingestion commands are documented in [docs/rag-pipeline.md](docs/rag-pipeline.md). The chat UI continues to use Phase 1 mock responses until Phase 3.

Phase 1 mock executive briefing for fictional Nexora Solutions. React/Vite, Tailwind, Recharts and FastAPI demonstrate ordered SSE text and charts. No database, retrieval or hosted inference is connected.

## Run locally (PowerShell)

From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r apps/backend/requirements.lock -e "./apps/backend[test]"
.\.venv\Scripts\python -m uvicorn execbrief.main:app --reload
```

In another terminal:

```powershell
cd apps/frontend
npm.cmd ci
npm.cmd run dev
```

Open http://localhost:5173. Vite proxies /api to port 8000. Use Python 3.11+ and Node 22.13+. No secrets are needed. Backend FRONTEND_ORIGIN can be set in the shell; .env.example documents future settings but is not automatically loaded.

Every question returns the same fictional Text → Line Chart → Text → Bar Chart → Recommendations demonstration. Include "text only" to omit charts. Stop response aborts the request; fixtures may finish before you click because no artificial delays are used. Conversation history is maintained in browser memory and clears on reload.

## Verify

```powershell
.\.venv\Scripts\python -m pytest apps/backend/tests
cd apps/frontend
npm.cmd test
npm.cmd run build
```

Tests use fixtures and require no paid inference. Database, embeddings, ingestion and hosted model setup belong to later phases. See docs/progress.md for actual verification results.
