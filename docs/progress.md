# Project progress

## Phase 1 SSE timing diagnosis

- Real Uvicorn endpoint tested with curl.exe -N using scripts/check_mock_stream.py. Without pacing, all text/chart/done events arrived at 0.027 seconds. With optional 400ms mock pacing, first text arrived at 0.410s, line chart at 1.623s, bar chart at 3.655s, and done at 5.677s. The route yields each event directly; no complete-response collection was found. The parser reads response.body incrementally and preserves partial frames.
- Root cause: the mock generator has all data ready and emits events without waiting, allowing network coalescing and React batching before a paint. Separate SSE frames do not guarantee separate browser paints. Also corrected the hook's queued updater to capture an immutable per-event snapshot instead of closing over the changing state variable.
- Added MOCK_STREAM_DIAGNOSTIC=1 (mock mode only) to enable explicitly labeled 400ms diagnostic pacing; default remains unpaced. This is a temporary observation aid, not LLM token streaming. Existing live providers were not integrated or changed in this task.
- Verification: 10 backend contract tests passed; 10 frontend tests passed. Expanded fragmented-stream integration test renders ChatMessage after each block and asserts summary text and zero/one/two chart figures while loading=true and done=false. This is DOM evidence before completion, not a manual browser/network walkthrough. curl timing directly verifies backend arrival before completion. Initial sandbox frontend launch failed with EPERM; authorized rerun passed.
- Reproduce in PowerShell: set $env:EXECBRIEF_MODE='mock' and $env:MOCK_STREAM_DIAGNOSTIC='1', then start uvicorn execbrief.main:app --reload. Start the frontend normally. Remove the diagnostic variable and restart the backend to disable pacing.

## Additional Google provider

Added explicitly selected Google Gemini hosted adapter, GOOGLE_API_KEY/GOOGLE_MODEL configuration and selected-provider diagnostic. Hugging Face remains the default. Same domain interface, structured validation, grounding and backend chart datasets apply. No automatic fallback or live Google success is claimed; a local API key and available model are required. Google adapter tests: 3 passed with mocked HTTP, covering valid/invalid structured output and provider selection.

Last updated: 2026-11-14 (Asia/Colombo).

## Current status

Phase 4 integration is implemented and automated verification passes. Final live acceptance is NOT complete: the configured Supabase hostname does not resolve and the hosted-model capability check fails. Earlier phase notes below are historical records, not current authorization or completion claims.

## Phase 4 delivery and verification

- Authorized by the user's explicit Phase 4 instruction. Preserved mock mode and the seven-event SSE contract; live dependency composition connects the existing LangChain retriever, Supabase repository, Pandas analytics and hosted HF provider to the endpoint.
- Added resource lifecycle ownership in core/live_chat.py. Cancellation closes generation and disposes the engine; cancellation during blocking initialization disposes the resource when initialization finishes. Failed vector/embedding initialization also disposes its engine.
- Loaded backend configuration before CORS settings; health reports configured execution mode. The frontend distinguishes mock/live configuration and visibly labels validated-block output without claiming service readiness.
- Preserved ordered blocks, earlier conversation content and sources after errors. Failed/partial assistant output is excluded from future history; history entries are bounded. Unmount aborts requests and suppresses subsequent state updates.
- Added endpoint integration coverage for the exact question **"How is our company performing over the last six months?"**. Real orchestration/Pandas/SSE with fake repository/retriever/model produces Text -> Line -> Text -> Bar -> Recommendations, sourced rows and October revenue 14,000,000. This proves wiring and calculations, not hosted model interpretation or live retrieval.
- Added cancellation/resource cleanup tests and frontend integration through real fetch/SSE parsing with fragmented frames; verifies progressive state updates and source retention. Existing tests cover actual Recharts DOM, errors, cancellation and incomplete streams.
- `python -m pytest apps/backend/tests -q -p no:cacheprovider`: **37 passed, 2 skipped**, one upstream langchain-community deprecation warning. The skipped tests require live Supabase. Initial restricted run hit Windows temporary-directory permission errors; the authorized unrestricted run passed.
- `npm.cmd test`: **10 passed** across three files. Initial restricted launch failed with spawn EPERM. The new HTTP fixture initially lacked response headers; corrected it and reran successfully.
- `npm.cmd run build`: **passed**, approximately 648 kB main bundle / 193 kB gzip; Vite warns above 500 kB. No bundle optimization claim.
- `scripts/check_database.py`: **failed**, configured hostname cannot resolve, including outside sandbox.
- `scripts/check_hf.py`: **failed**, sanitized hosted capability diagnostic. Availability/access/token or model configuration requires local correction; the exact provider cause is not established.
- `scripts/check_workflow.py`: **failed**, exact requested question submitted through FastAPI in-process using live configuration; endpoint emitted sanitized failure. No live briefing, ingestion, retrieval or chart success is claimed.
- Updated README, architecture, API/RAG documentation and phase plan with actual setup, fallback behavior and limitations. The existing `docs/` Git ignore rule excludes untracked documentation (including API/RAG workflow guides); tracked architecture, plan and progress changes appear normally. Untracked guides require explicit inclusion if committing them.

### Decisions and remaining acceptance

- Use the specification's validated-block fallback. Full structured output must pass grounding/chart validation before publication. No artificial delays or raw model-token replay. True hosted token streaming is not implemented or verified; no compatible provider capability has been established. React may paint several immediately arriving blocks together.
- Live mode contains no fixed demonstration chart rows. The default remains explicitly labeled mock for offline testing. Health reports configuration only, not external readiness.
- Blocking embedding/database work cannot be forcibly cancelled once executing in a worker. Per-request adapter initialization can be expensive. Production auth/rate limits, deployment/container verification and a real-browser network walkthrough remain unverified/out of this delivery.
- Existing limitations remain: extractive factual prose, qualitative recommendations not mechanically proven, mixed monetary/percentage revenue columns requiring compatible chart series, source replacement convergence rather than atomic batch replacement, and mutable metadata-based initial Alembic migration.
- Configure rotated secrets locally in `.env.local`; obtain the current Supabase Session pooler URI from Dashboard > Connect (5432), and an available hosted HF model/token. Do not paste secrets into chat. Then run connection check, seed/migrations, ingestion, live integration tests, hosted capability check and workflow smoke check, followed by the browser question/cancellation walkthrough.
- Stop after Phase 4. Final product acceptance remains pending these live checks; no further phase is started.

## Historical phase records

## Phase 3 delivery and verification

- Added replaceable LLM, analytics and metrics repository contracts; hosted Hugging Face async provider with bounded timeouts, sanitized failures, one transient retry and Pydantic structured-output validation.
- Added executive query planning with allowlisted operations and May–October period validation; retrieval supplies domain evidence through the existing retriever.
- Added Pandas calculations over SQLAlchemy repository records for revenue/growth/targets, expenses/budgets, sales, turnover, project delays and operational trends.
- Added grounded response validation and backend dataset resolution. Factual text must exactly match supplied evidence/analytical facts. Recommendations are explicitly labeled; their qualitative quality still requires live evaluation.
- Integrated the opt-in live path through dependency composition while preserving default mock behavior. The live path uses validated_blocks fallback, not incremental model tokens. Added docs/ai-workflow.md.
- Backend suite: 34 passed, 2 live tests skipped. Includes ten representative question workflow tests with mocked planning, numerical expected values, zero denominator/empty data, invented-number rejection, invalid operations, missing evidence, provider failures, malformed output and rate-limit retry.
- Live database diagnostic failed: configured hostname does not resolve. Phase 2 live schema/ingestion verification is still pending.
- Hosted HF capability check failed with sanitized output. Model availability, token permissions or provider access must be corrected locally before live planning/generation can be verified.
- Remaining acceptance: live retrieval, hosted question interpretation/grounding, all ten real-provider demo outcomes and browser integration. No live success is claimed.
- Phase 4 remains unauthorized.

## Phase 2 delivery and verification

- Added deterministic fictional May–October 2026 data generation: six CSVs (126 records total) and six PDFs derived from shared facts. Sales totals reconcile to monthly revenue; October revenue is LKR 14,000,000. Reports preserve the fictional explanation for deferred Atlas billing.
- Added server-side .env.local loading, SQLAlchemy/psycopg SSL connections, bounded pooling, extension schema discovery, dedicated execbrief schema, Alembic relational migration and idempotent structured imports.
- Added domain document/ingestion/retriever ports, modular PyPDFLoader and CSVLoader adapters, 1000/200 recursive splitting, CPU HuggingFaceEmbeddings, LangChain PostgreSQL storage and configurable similarity retrieval.
- Added source-scoped content-addressed chunk replacement, with stale-chunk cleanup after successful insertion. Concurrent writers use a session advisory lock. Interrupted replacement may temporarily expose old and new chunks; rerunning converges. Removed files require explicit cleanup and are not automatically deleted.
- Added CLI generation, safe database diagnostics, seeding and ingestion, and docs/rag-pipeline.md setup instructions. Chat remains the Phase 1 mock flow.
- Dependency installation completed; requirements.lock refreshed from the installed environment.
- Generation command passed and created all 12 artifacts.
- Backend suite: 15 passed, 2 live tests skipped by default. Tests cover Phase 1 regression plus deterministic PDF/CSV generation, reconciliation, metadata, splitting, invalid imports, repeat orchestration and mocked retriever contract.
- Real CPU embedding smoke check passed: all-MiniLM-L6-v2 downloaded and returned 384-dimensional embeddings. Windows cache emitted a non-fatal symlink warning.
- Live seed and ingestion commands failed with OperationalError. A separate DNS check established that the configured hostname could not be resolved, including outside the sandbox.
- Explicit live integration test run: 2 failed due to connection unavailability. No successful database mutation or retrieval is claimed.
- Installed langchain-community emits a deprecation warning; the specification explicitly requires its PyPDFLoader and CSVLoader, so those adapters remain isolated for future migration.
- Security correction: the interrupted initial inspection printed .env.local contents. User was informed and asked to rotate the database password and HF token locally. Subsequent commands do not print credentials; .env.local is ignored and was not tracked.
- User action needed: configure the existing Supabase dashboard Session pooler URI (port 5432) as DATABASE_URL in .env.local, with a rotated password. Then rerun safe connection check, migration/seed, ingestion and live tests.
- Remaining Phase 2 acceptance: successful live schema/extension/import/retrieval and duplicate-ingestion verification. Phase 3 is not authorized.

## Phase 1 delivery and verification

- Created React/Vite JavaScript frontend with Tailwind, modular chat components, source references, Recharts bar/line strategies and registry.
- Created FastAPI backend with separate domain provider contract/block entity, mock infrastructure adapter, application use case, dependency composition, Pydantic request/chart schemas, health endpoint and POST SSE endpoint.
- Implemented the fictional sequence Text → Line Chart → Text → Bar Chart → Recommendations. Every question receives the fixed fixture; "text only" omits charts. Fixtures are isolated in infrastructure and explicitly labeled mock.
- Implemented fetch/ReadableStream parsing, fragmented UTF-8 and CRLF handling, stable message/block state, history, errors, completion and cancellation. No artificial streaming delays or live inference claims.
- Added README setup instructions, API contract, blank-secret environment example, ignores, frontend lockfile and backend dependency snapshot. Existing Git repository was preserved.
- Backend: ` .venv/Scripts/python -m pytest apps/backend/tests ` — 10 passed. Covers endpoint event order, metadata, chart validation, invalid requests, text-only response, health and sanitized failure events.
- Frontend: `npm.cmd test` — 8 passed with Vitest 4.1.12. Covers byte-fragmented streams, incomplete frames, ordered text and chart DOM rendering using real Recharts, append behavior, errors, cancellation, early EOF and conversation preservation.
- Frontend: `npm.cmd run build` — passed. Build reports a 647 kB main bundle (192.51 kB gzip); bundle splitting remains a possible improvement.
- Dependency installation initially encountered sandbox restrictions. Tests/build ran successfully after permission to spawn compiler/test processes. Chart JSX syntax was corrected after the first failed build.
- Initial test-runner dependency audit reported vulnerabilities. Upgraded Vitest to 4.1.12; npm 11.1 encountered an internal edgesOut error, resolved by running `npx.cmd --yes npm@11.12.0 install`. Final install audit reported zero vulnerabilities.
- Backend test warnings: upstream Starlette HTTPX TestClient deprecation and sandbox denial of pytest cache creation; neither failed a test.
- Live browser walkthrough, browser-to-running-server flow and disconnect cleanup under a real network connection have not been verified. No Supabase, RAG, analytics or hosted inference work was performed.
- Next action: stop after Phase 1. Await the user's next instruction; do not begin Phase 2.

The remaining sections below preserve the original planning baseline; their pre-implementation statuses are historical and are superseded by the Phase 1 delivery record above.

## Completed tasks

- Read the complete `docs/MASTER_SPEC.md`, including all 19 sections and the required monorepo tree.
- Inspected the workspace, including hidden root entries and Git status. The only pre-existing file found was `docs/MASTER_SPEC.md`; no application, dependency manifests, tests or `.git` directory existed.
- Created `AGENTS.md` with mandatory stack, scope, architecture, coding, grounding, streaming and verification rules.
- Created `docs/architecture.md` with proposed layers, module structure, domain models/ports, dependencies, data flows and the seven-event streaming contract.
- Created `docs/implementation-plan.md` with four phases, work breakdowns, acceptance criteria, demo coverage and specification traceability.
- Created this progress record. No application scaffolding, packages, databases or external services were changed.

## Pending tasks

| Phase | Status | Main remaining work |
| --- | --- | --- |
| 1 - End-to-end UI and streaming | Implemented; automated checks pass | Manual browser walkthrough remains unverified |
| 2 - Supabase and data | Implemented; live verification blocked | Configure resolvable Supabase URI; verify extension, migrations, imports, ingestion, retrieval and duplicate counts |
| 3 - AI integration | Not started | Hosted HF provider, query planning, verified analytics, grounded responses, real streaming/fallback and ten demo questions |
| 4 - Architecture and testing | Not started | Architecture audit, expanded tests/reliability, setup documentation and complete acceptance verification |

Detailed gates and criteria are in [implementation-plan.md](implementation-plan.md). Do not advance all phases in one execution.

## Architectural decisions

| Decision | Reason/status |
| --- | --- |
| Modular monolith in one frontend/backend monorepo | Required by specification; no implementation yet |
| API -> Application -> Domain Interfaces <- Infrastructure | Separates HTTP, orchestration, business values and external implementations |
| Composition through core/container.py | Keeps clients/connections out of use cases and enables mocked ports |
| React/Vite JavaScript/JSX, Tailwind, Recharts; FastAPI/Pydantic v2 | Required stack; exact compatible versions pending implementation |
| Existing Supabase PostgreSQL with psycopg 3/SQLAlchemy 2.x and pgvector | Required provider; actual connection mode/extension schema remain unverified |
| Local CPU MiniLM embeddings; hosted HF language inference | Explicit specification distinction; no local language-model hosting |
| Separate semantic CSV ingestion and structured metric imports | Retrieved text supports explanation; verified SQL/Pandas calculations own exact KPIs |
| Fixed May-October 2026 fictional data from shared canonical facts | Ensures deterministic CSV/PDF/numerical consistency |
| Backend-owned datasets; model proposes only validated chart specifications | Avoids invented chart values and executable generated code |
| Pydantic at transport/provider boundaries; framework-free domain values | Preserves Clean Architecture while validating external output |
| POST fetch SSE with ordered block IDs and source metadata | Required inline progressive text/chart experience with history and cancellation |
| Explicit mock/incremental/validated_blocks modes | Prevents misrepresenting fixtures or buffered output as token streaming |
| No placeholders or application code in this task | Explicit user instruction; Phase 1 requires a new instruction |

## Verification evidence

- Repository inspection: `rg --files` and `Get-ChildItem -Force` found only the original specification before documentation creation.
- Specification review: read the complete file with explicit UTF-8 decoding after the shell's default display produced garbled punctuation. No specification content was modified.
- Git inspection: `git status --short` and `git ls-files` reported that the directory is not a Git repository. Git initialization is pending Phase 1.
- Documentation review: checked the proposed phases, stack, layer boundaries, domain contracts, streaming events, demo matrix and acceptance criteria against the master specification. These are design checks, not runtime tests.
- Application tests/builds: not run; there is no application or test suite yet.
- Supabase connectivity/migrations/vector integration: not attempted or verified.
- Hosted HF availability/inference/streaming: not attempted or verified.

## Known issues and unresolved decisions

- Git is not initialized; there is no pre-existing implementation to preserve or validate beyond the specification.
- The IDE lists `docs/ExecBrief_AI_Master_Prompt.md`, but that file was not present in the inspected workspace. The complete on-disk `MASTER_SPEC.md` is the planning source; no missing-file contents were inferred.
- Exact package versions, lockfile strategy, hosted HF model availability/capabilities and langchain_postgres schema behavior require implementation-time verification. No compatibility success is claimed.
- Supabase connection configuration, extension state, access permissions and pooling mode are unknown. External verification will need the user's existing project configuration through backend environment settings.
- Metric schemas/formulas, currency/units, denominator policies and changed-document replacement details must be finalized in Phase 2/3 before claiming numerical correctness or ingestion reliability.
- Incremental structured generation and grounding reliability must be evaluated with the chosen provider. A documented validated-block fallback is permitted by the specification.
- No application defects are established because no application exists. All final acceptance criteria remain pending.

## Next authorized action

Correct local database/model configuration and rerun the pending live acceptance checks documented above. Phase 4 code work is delivered; final acceptance is pending, not claimed complete.
