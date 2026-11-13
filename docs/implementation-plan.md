# Four-phase implementation plan

Status: proposed; all application phases are pending. Follow [MASTER_SPEC.md](MASTER_SPEC.md), [architecture.md](architecture.md) and [AGENTS.md](../AGENTS.md). The user has authorized documentation only. Stop after these documents and wait for an explicit instruction to begin Phase 1.

## Execution and evidence rules

- Implement one phase incrementally, with useful modules rather than placeholder scaffolding. Clean Architecture, SOLID and required patterns apply from the first implementation; Phase 4 audits/refines them.
- Resolve current library APIs and compatible versions using official documentation when implementing, and record exact install/run/test commands and results. No versions, hosted model or integration behavior have been verified yet.
- Each phase ends with a progress update listing files changed, acceptance checks, actual results, limitations and remaining issues. Do not mark a phase verified when required checks were skipped. Mock-only success does not establish live integration success.
- Automated tests use mocked LLM responses and require no paid inference. Keep external integration checks explicit. Wait for the next phase instruction after reporting the current phase.

## Phase 1 - End-to-end UI and streaming

Objective: a working React-to-FastAPI streaming slice using clearly labeled synthetic mock responses, with the final architectural boundaries in place.

### Work

1. Initialize the single Git monorepo if still absent, add appropriate ignores, and establish React/Vite JavaScript/JSX and Python 3.11+ FastAPI applications. Add only used modules, reproducible dependency manifests/locks and blank-secret configuration examples.
2. Define domain blocks, datasets, sources and narrow interfaces; keep Pydantic request/response schemas and ORM-free domain values distinct. Set up configuration, dependency composition and health/chat routes.
3. Formalize request limits, chart schema, source references and all seven SSE events in `docs/api-contracts.md`. Add validation of block IDs, types, dataset IDs and columns, plus a transport-neutral application event stream.
4. Implement `POST /api/chat/stream` through a mock provider/use case and StreamingResponse. Emit an ordered text/line-chart/text/bar-chart/recommendation fixture without artificial timing; label this mode mock. Include representative references and error paths.
5. Build ChatWindow, ChatMessage, MessageInput, StreamingStatus, SourceReferences and the visualization blocks. Use Tailwind for a responsive executive UI; use Recharts strategies and a registry for bar/line charts, multiple series, titles, axes, legends and tooltips.
6. Implement `chatApi.js` and `useExecutiveStream.js`: fetch, incremental decoding/SSE buffering, ordered block state, history, completion, errors and AbortController cancellation. Keep App.jsx focused on composition.
7. Add backend Pytest contract tests and frontend parser/rendering tests. Document exact local frontend/backend setup and the mock-only scope in README.

### Acceptance criteria

- A browser-submitted question reaches FastAPI and receives the seven-event contract as applicable; text and inline charts render in order without losing earlier blocks/messages.
- Tests verify fragmented UTF-8/SSE frames, multiple frames per chunk, append behavior, stable IDs, sequential rendering, text-only responses, both chart strategies, invalid charts/dataset columns, errors, early EOF, cancellation and completion.
- Backend tests and frontend tests/build pass with recorded commands. Health and the browser mock flow are checked and their results recorded separately.
- No Supabase or HF credentials are needed for the mock slice; no live RAG, analytics or LLM functionality is claimed. Mock chart rows stay isolated from future integrated data paths.
- API/use-case/domain/infrastructure responsibilities are separate; no endpoint contains analytics or provider logic. The next phase remains pending until instructed.

## Phase 2 - Supabase and data

Prerequisite: verified Phase 1 and instruction to proceed. Access to the existing Supabase project/connection configuration is needed for live verification; never put supplied credentials in documentation or frontend files.

### Work

1. Define canonical schemas, natural keys, units, validation and fictional facts for May-October 2026. Use a deterministic seed for Nexora Solutions (Pvt) Ltd and its five departments, approximately 150 employees. Ensure an October revenue decline has consistent financial facts and narrative support.
2. Implement `generate_synthetic_data.py` to produce all six required CSVs and PDFs. Generate narratives from the same canonical facts, label all artifacts fictional and verify totals across them.
3. Configure SQLAlchemy 2.x/psycopg 3, SSL, appropriate pool settings and Alembic. Check existing database state; enable pgvector in `extensions` if absent, and validate the actual extension schema with langchain_postgres. Do not install local PostgreSQL.
4. Create relational schemas for revenue, departmental expenses, sales, turnover, projects and operational KPIs, with constraints and provenance. Implement repository adapters and `seed_database.py` with validated, repeatable imports.
5. Implement modular PyPDFLoader and CSVLoader adapters preserving all required metadata. Add RecursiveCharacterTextSplitter with 1000/200 defaults for long PDFs; preserve short CSV records.
6. Implement local CPU all-MiniLM-L6-v2 embeddings through HuggingFaceEmbeddings, vector storage, deduplication and safe retry/replacement behavior. Build IngestDocumentsUseCase and `ingest_documents.py`; add document routes only for a concrete ingestion workflow.
7. Implement the retriever adapter using `.as_retriever()` with configurable similarity top-k 5. Write `docs/rag-pipeline.md` and database/data-generation/ingestion setup instructions.

### Acceptance criteria

- All six CSVs and six named reports exist, are readable, labeled fictional and cover the correct six months. A fixed seed reproduces facts; reconciliation checks confirm shared figures including October revenue and cross-dataset relationships.
- Loader, splitting and metadata tests pass; source page/row conventions are documented. Repeated structured import and document ingestion do not duplicate records/chunks; changed content and interrupted-ingestion retries are covered.
- Alembic setup and relational persistence are verified on the existing hosted Supabase with SSL. The chosen vector integration stores and retrieves embeddings with the installed extension schema.
- Real retrieval returns relevant chunks with correct provenance; mocked adapter tests are identified separately. Lack of external access leaves live verification explicitly pending.
- No language model runs locally. Embeddings are local CPU inference; generation integration remains Phase 3 work.

## Phase 3 - AI integration

Prerequisite: verified Phase 2 and instruction to proceed. Hosted HF token/model configuration and a capability check are required for live generation validation.

### Work

1. Verify an available hosted `HF_MODEL` supports required generation and, where available, incremental streaming. Implement LLMProvider with the hosted Hugging Face client, bounded timeout/retry policy, rate-limit handling and safe errors.
2. Implement QueryPlanner with allowlisted operations and validated parameters. Route questions to RAG, structured analytics or both; do not execute model-generated code/SQL.
3. Implement SQLAlchemy repository operations and Pandas calculations for revenue trends/growth, actual versus target, department expenses/budget variances, sales, turnover, delays and operational trends. Specify formulas, units, period boundaries, missing data and zero denominators; use known-value fixtures.
4. Implement RagService, AnalyticsService and response planning behind domain interfaces. Compose AskExecutiveUseCase and GenerateBriefingUseCase with retrieved evidence and verified datasets.
5. Validate ordered Pydantic response blocks, approved dataset/column references and backend-resolved chart rows. Add evidence attribution, numerical consistency checks, unsupported-request handling and explicit missing-evidence responses. Treat reports as evidence, not executable instructions.
6. Connect real output to SSE and source rendering. Prefer genuine incremental text when reliable; otherwise document and visibly identify validated-block mode. Preserve the same ordering/error/cancellation contract.
7. Remove mock data from the integrated execution path while retaining fixtures for tests. Exercise all ten required demo questions and record outcomes, provider/model details and streaming mode.

### Acceptance criteria

- Verified calculations match independent expected values for every required analytical capability, including missing/zero-denominator cases and actual/target comparisons.
- The live path retrieves from Supabase and calls hosted HF; explanations use evidence and verified numerical results. Unsupported claims are rejected or clearly qualified; unknown causes are not invented.
- Invalid chart types, unknown datasets/columns and executable output are rejected. Recharts displays backend-owned verified datasets; relevant questions may yield text only.
- Automated mocked tests cover provider failures/timeouts/rate limits, malformed output, missing evidence, grounding and stream behavior without paid inference.
- Live smoke checks and all demo outcomes are recorded separately from unit tests. Actual token streaming is demonstrated if claimed; validated-block mode is documented if used. Browser sources and cancellation are verified.

### Demo verification matrix

| Required question | Expected evidence/analytics and presentation |
| --- | --- |
| How is our company performing? | Broad briefing, verified KPIs and narrative evidence, sequential summary/line/analysis/bar/recommendations/sources |
| Show revenue trends over the last six months. | May-October revenue dataset, trend explanation and line chart |
| Compare departmental expenses. | Department expense totals/variances and bar chart |
| Which departments are underperforming? | Defined target comparisons, evidence-backed interpretation and relevant chart |
| Why did revenue decline in October? | September/October calculation plus cited explanatory reports; distinguish evidence from hypotheses |
| What are our biggest operational risks? | Risk register and operational evidence, supported prioritization and actions |
| How has employee turnover changed? | Defined turnover calculation and trend, supported HR context |
| Which projects are delayed? | Verified planned/actual/status data and cited project/operations context |
| What management decisions require attention? | Management minutes, risks and verified metrics supporting recommendations |
| Compare actual performance against targets. | Approved actual/target datasets and appropriate multi-series charts |

## Phase 4 - Architecture and testing

Prerequisite: verified Phase 3 and instruction to proceed. This phase expands assurance and documentation rather than postponing architectural correctness until the end.

### Work

1. Audit dependency direction, small modules, interface substitutability, repository isolation, dependency injection, chart Strategy/Registry and SOLID compliance. Refactor violations without changing public contracts unnecessarily.
2. Complete unit/integration/contract coverage for PDF/CSV loading, recursive splitting, metadata, vector retrieval, KPI calculations, chart validation/unsupported types, stream order, missing evidence and duplicate ingestion.
3. Complete frontend sequential rendering, text streaming, bar/line charts and error tests; cover concurrent/stale stream isolation, cancellation and incomplete frames.
4. Improve resource cleanup, provider failure handling, safe logging, input limits, CORS/configuration, ingestion retry safety and responsive/accessibility behavior. Validate that sensitive settings never enter frontend builds.
5. Add a functional backend Dockerfile when packaging is exercised, without a local database container. Complete README, API contracts, RAG pipeline and architecture with actual commands/configuration and deployment/runtime limitations.
6. Run the automated suite and frontend build, then perform the integrated demo walkthrough. Record exact results and any unavailable external checks in progress.md.

### Acceptance criteria

- Every master-spec acceptance criterion is evidenced: question submission, FastAPI processing, LangChain/Supabase retrieval, correct KPIs, grounded hosted generation, validated blocks, sequential rendering, verified bar/line charts and visible sources.
- No business logic resides in endpoints; database operations remain in repositories; ingestion is modular; interfaces and patterns satisfy the documented boundaries.
- Required backend/frontend tests and build pass; live retrieval and hosted inference have separate recorded evidence. No skipped integration check is reported as passed.
- Setup instructions cover React, FastAPI, existing Supabase, pgvector schema, HF inference, synthetic generation, relational seed, RAG ingestion, tests and running the complete application. Commands are verified or explicitly marked unverified.
- No final hardcoded chart data, committed secrets, prohibited technologies or misleading streaming claims remain. Open limitations are explicit; application completion is claimed only after all required acceptance checks pass.

## Specification traceability

| Master specification sections | Delivery |
| --- | --- |
| 1-4: product, stack, monorepo, layers | Planning and Phase 1; enforced throughout |
| 5-7: synthetic data, Supabase, ingestion | Phase 2 |
| 8-9: analytics and hosted generation | Phase 3 |
| 10-13: blocks, charts, streaming, frontend | Phase 1 contracts/mock slice; Phase 3 real integration |
| 14-15: SOLID/patterns and tests | Every phase; expanded audit in Phase 4 |
| 16: ten demo questions | Phase 3 walkthrough and Phase 4 regression |
| 17-19: phase gates, acceptance, setup | This plan; verified incrementally and finalized in Phase 4 |
