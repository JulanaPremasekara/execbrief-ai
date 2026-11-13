# Proposed architecture

Status: design only; no application implementation exists. This document follows all sections of [MASTER_SPEC.md](MASTER_SPEC.md). The current workspace contains the master specification and the requested planning documents; it is not yet initialized as a Git repository.

## Layers and dependency direction

```text
React UI -> FastAPI API -> Application -> Domain interfaces
                                           ^
                                      Infrastructure
core/container.py composes adapters and injects them into use cases.
```

| Boundary | Responsibilities | Dependencies |
| --- | --- | --- |
| API | Routes, Pydantic requests/responses, HTTP errors, SSE encoding, dependency resolution | Application and domain types; FastAPI/Pydantic |
| Application | AskExecutive, IngestDocuments, GenerateBriefing; retrieval, analytical and response planning; ordered semantic events | Domain entities and interfaces only; no concrete SDK, ORM or HTTP types |
| Domain | Documents, metrics, datasets, blocks, source references, business rules and exceptions | Standard Python; no external framework dependencies |
| Infrastructure | SQLAlchemy repositories, Pandas engine, LangChain loading/splitting/embedding/retrieval, hosted inference and generated-output validation adapters | Domain contracts plus external libraries |
| Composition | Configuration, lifecycle, connection pools and provider construction | All required concrete implementations; `api/dependencies.py` exposes constructed use cases |

Pydantic transport schemas live in `api/schemas`; model-output Pydantic validation belongs at the inference adapter boundary and converts to domain blocks. Application services additionally validate business constraints such as dataset membership. ORM models stay in infrastructure. The application streaming service produces transport-neutral events; only the API encodes SSE bytes.

## Target monorepo

This is a target structure, not an instruction to create empty files. The master specification's full tree is authoritative; modules are introduced when used.

```text
apps/
  frontend/
    public/
    src/
      app/App.jsx
      features/
        chat/
          components/{ChatWindow,ChatMessage,MessageInput,StreamingStatus,SourceReferences}.jsx
          hooks/useExecutiveStream.js
          services/chatApi.js
        visualizations/
          components/{BlockRenderer,TextBlock,BarChartBlock,LineChartBlock}.jsx
          registry/chartRegistry.js
      shared/{components,hooks,utils}/
      main.jsx
    package.json
    vite.config.js
  backend/
    src/execbrief/
      main.py
      api/
        routes/{chat,documents,health}.py
        schemas/{requests,responses}.py
        dependencies.py
      domain/
        entities/{document,metric,response_block}.py
        interfaces/{llm_provider,document_retriever,metrics_repository,analytics_provider}.py
        exceptions.py
      application/
        use_cases/{ask_executive,ingest_documents,generate_briefing}.py
        services/{rag_service,analytics_service,query_planner,response_planner,streaming_service}.py
      infrastructure/
        database/{session.py,models/,repositories/}
        rag/
          loaders/{pdf_loader,csv_loader}.py
          {text_splitter,embeddings,pgvector_store}.py
        llm/huggingface_provider.py
        analytics/pandas_engine.py
      core/{config,container}.py
    migrations/
    tests/{unit,integration,contract}/
    pyproject.toml
    Dockerfile
data/synthetic/{csv,pdf}/
scripts/{generate_synthetic_data,seed_database,ingest_documents}.py
docs/{MASTER_SPEC,architecture,implementation-plan,progress,api-contracts,rag-pipeline}.md
AGENTS.md
.env.example
.gitignore
README.md
```

Frontend tests will be colocated with the relevant features. Additional ingestion ports may be introduced under domain interfaces when needed; external loader, splitter and vector-store types must not leak into application code.

## Proposed domain models and ports

| Model | Core values and invariants |
| --- | --- |
| Document / DocumentChunk | Stable ID, content, content hash, source metadata, chunk index; provenance survives transformations |
| SourceReference | Source ID, filename, document/dataset ID and page or row locator; internal filesystem paths are not automatically exposed to the browser |
| Metric / AnalyticalDataset | Operation/dataset ID, period, units, dimensions, typed columns, rows and provenance; explicit missing values and denominator policy |
| QueryPlan | Allowlisted analytical operations, validated filters and retrieval query; never executable code or SQL |
| TextBlock | Unique stable `id`, `type: text`, `content` |
| ChartBlock | Unique stable `id`, `type: chart`, `chart_type: bar|line`, `title`, `dataset_id`, `x`, nonempty `y` column list |
| ExecutiveResponse | Ordered blocks, approved datasets and supporting source references |

| Port | Proposed behavior |
| --- | --- |
| LLMProvider | Plan/generate through typed inputs and output; yield incremental text when supported; expose capability/failure semantics |
| DocumentRetriever | Retrieve domain chunks and sources for a query and configurable top-k |
| MetricsRepository | Fetch typed metric records through predefined operations and validated filters |
| AnalyticsProvider | Transform records into verified metrics/datasets using predefined calculations |
| Ingestion ports, as required | Load domain documents, split chunks, embed and upsert deduplicated chunks; isolate LangChain representations in adapters |

Use narrow protocols/ABCs, standard Python domain values, and shared contract tests for adapter substitutability. Do not add generic repository frameworks or unused abstractions.

## Dependencies and configuration

| Area | Planned dependencies |
| --- | --- |
| Frontend runtime/build | react, react-dom, vite and React plugin, tailwindcss and its compatible Vite integration, recharts |
| Frontend testing | Proposed Vitest, React Testing Library, jsdom and DOM assertions |
| Backend runtime | Python 3.11+, fastapi, uvicorn, pydantic v2, proposed pydantic-settings |
| Relational/analytics | sqlalchemy 2.x, psycopg 3, alembic, pandas |
| RAG | langchain, langchain-community, langchain-text-splitters, langchain-huggingface, langchain-postgres, sentence-transformers, pypdf; compatible pgvector client dependency |
| Hosted inference | huggingface-hub hosted inference client behind LLMProvider |
| Data generation/testing | Proposed reportlab for PDFs; pytest, HTTP test client and async test support as required |

Versions and exact supported integration APIs must be checked against official documentation when each phase is implemented, then locked reproducibly. No packages have been installed or compatibility-tested in this planning task.

Backend settings include `DATABASE_URL`, `HF_TOKEN`, `HF_MODEL`, `FRONTEND_ORIGIN=http://localhost:5173`; optional settings cover timeouts, retrieval top-k and pool sizing. Secrets stay server-side. The selected hosted model is intentionally undecided until availability and required inference/streaming capabilities can be verified. Local CPU embedding inference is explicitly required and separate from hosted language generation.

Use the supplied Supabase dashboard connection string with SSL and psycopg 3. Select pooling settings compatible with the actual connection mode; use an appropriate migration connection. Enable `CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA extensions;` after checking existing extension state. Configure the vector integration to resolve the actual installed schema rather than assuming `public`. Alembic owns relational schema changes; vector schema initialization must be controlled and documented for the chosen integration.

## Data and ingestion flow

1. Generate deterministic fictional facts for Nexora Solutions (Pvt) Ltd, approximately 150 business-services employees in Finance, Sales, Human Resources, Operations and IT, for May-October 2026.
2. Derive `monthly_revenue.csv`, `department_expenses.csv`, `sales_performance.csv`, `employee_turnover.csv`, `project_performance.csv` and `operational_kpis.csv` from those facts.
3. Derive Financial Performance, Sales Performance, HR Performance, Operations, Management Meeting Minutes and Business Risk Register PDFs from the same facts. Label all outputs fictional and check cross-artifact totals, especially October revenue. Include supported narrative reasons for the October decline.
4. Validate CSV schemas and import typed records through repositories into corresponding relational metric tables. Use deterministic natural keys/constraints so repeated seeding does not duplicate facts. Define monetary units, dates, target semantics and metric formulas before importing.
5. Separately ingest PDFs using PyPDFLoader and CSV rows using CSVLoader. Preserve PDF filename/page/source path/document ID and CSV filename/row/dataset ID.
6. Split long PDF content using RecursiveCharacterTextSplitter (1000/200); avoid needless splitting of short CSV records. Embed locally using HuggingFaceEmbeddings and all-MiniLM-L6-v2.
7. Store vectors in Supabase through langchain_postgres. Use stable document/chunk identifiers and content hashes for deduplication. Track completed ingestion and make retries safe; define replacement of changed-source chunks to avoid stale evidence.
8. Retrieve through `.as_retriever()` with similarity search and configurable top-k, initially 5. Return domain evidence and provenance.

## Question-to-response flow

1. Chat components submit a question and bounded conversation context through `chatApi.js`; `useExecutiveStream.js` manages ordered state and cancellation.
2. FastAPI validates the request and invokes AskExecutiveUseCase with injected services.
3. Query planning selects RAG, approved analytics, or both. Model-suggested operations/filters are validated before execution.
4. RAG supplies supporting evidence; repositories and the Pandas adapter calculate exact revenue trends/growth, actual versus target, departmental expenses/budget variances, sales, turnover, project delays and operational trends.
5. Response planning combines evidence and verified datasets. Hosted inference explains performance, risks and recommended actions and proposes charts. Missing evidence yields an explicit limitation, not an invented cause or number. Retrieved text is evidence, never authority to run code.
6. Validate model output and grounding before publishing finalized blocks. Only approved dataset IDs, columns and chart types resolve to backend-owned rows. Keep source attribution linked to evidence and analytical provenance.
7. Emit ordered semantic events; the API serializes SSE. The frontend appends text to the matching block, dispatches charts through the registry and renders references. Chart strategies support multiple series, titles, axis labels, tooltips, legends and responsive sizing. Questions needing only text receive no forced chart.

GenerateBriefingUseCase will reuse the same pipeline for the broad executive overview, without duplicating business logic. Document routes, when introduced, will invoke IngestDocumentsUseCase; their precise API is deferred to Phase 2.

## Proposed streaming contract

Phase 1 will formalize and test this design in `docs/api-contracts.md`. Endpoint: `POST /api/chat/stream`; JSON request contains `question` and optional bounded `history` entries with `role` and `content`. Backend-generated request/message IDs isolate streams. Response content type is `text/event-stream`; each frame has `event: <type>` and a JSON `data:` payload followed by a blank line. Common payload fields are `request_id`, `message_id`, and strictly increasing `sequence`.

| Event | Additional payload and meaning |
| --- | --- |
| status | `stage`, `message`, `stream_mode` (`mock`, `incremental`, or `validated_blocks`); progress only |
| block_start | `block_id`, `block_type`, zero-based `position`; opens the next block |
| text_delta | `block_id`, `delta`; append only to the current text block |
| chart | `block_id`, validated `spec`, backend-resolved `dataset` including ID/columns/rows/units; emitted once within a chart block |
| block_end | `block_id`, block-specific `sources`; closes and finalizes the block |
| error | Safe `code`, `message`, `retryable`; does not erase previously completed blocks |
| done | `outcome: completed|error`, aggregate `sources`, `stream_mode`; terminal event |

Success ordering is `status* -> (block_start -> text_delta* OR chart -> block_end)* -> done`, with optional progress statuses between blocks. Only one block is open at a time. IDs are stable and unique within each message; positions increase. In the intended overview, text, line chart, text, bar chart and recommendations appear sequentially, followed by aggregate sources/completion. No events follow `done`.

Request validation failures before streaming use ordinary HTTP errors. After streaming begins, an unrecoverable failure emits `error` then `done(outcome=error)` if the connection permits; an open partial block remains visibly incomplete. A disconnected/cancelled client cannot be guaranteed a terminal event. AbortController cancels the browser request and backend cancellation closes provider iterators/resources. Unexpected EOF without `done` is an interrupted response. Do not automatically replay a partially rendered answer.

The parser must buffer incomplete UTF-8 and SSE frames across ReadableStream chunks, support LF/CRLF and multiline data, and process multiple frames per chunk. Reject malformed payloads and invalid ordering safely. Updates address the active message/block so older conversation entries remain intact.

Incremental mode forwards actual hosted model text deltas under a validated response plan. Grounding checks and numeric constraints must not be bypassed for speed. If structured/grounded incremental generation cannot be made reliable, validate complete blocks before emitting them, label `validated_blocks`, and document the tradeoff. Never claim buffered blocks or mock fixture chunks are model-token streaming; never add artificial delays.

## Verification boundaries

Unit tests exercise domain/application behavior using fake ports and mocked LLM output. Adapter tests cover loaders, splitter and metadata; contract tests cover block validation and stream order. Integration tests separately verify real Supabase migrations, deduplication and vector retrieval. Optional live hosted-inference smoke tests verify capability/grounding and are distinct from the automated no-paid-call suite. Frontend tests exercise real parser/state behavior and block/chart rendering. All work remains unimplemented until the relevant phase is authorized and verified.
