# ExecBrief AI project rules

## Authority and workflow

- Read the complete [master specification](docs/MASTER_SPEC.md) before changing the project. It defines the product and mandatory architecture. Follow explicit user instructions when they constrain execution.
- Current authorization covers planning documents only. Do not implement application code until the user instructs you to begin Phase 1.
- Follow [architecture](docs/architecture.md) and the [four-phase plan](docs/implementation-plan.md). Implement incrementally, verify each phase, report results, and obtain the next phase instruction rather than implementing the entire application in one execution.
- Update [progress](docs/progress.md) with completed work, pending work, decisions, commands/checks and their actual results, and known issues. Distinguish mocked verification from live integration verification. Never claim untested functionality works.
- Preserve existing work. Create modules only when they have a concrete responsibility; do not precreate empty folders or placeholder files from the target tree.

## Mandatory stack

- Frontend: React, Vite, JavaScript/JSX, Tailwind CSS, Recharts, React Hooks, Fetch API and ReadableStream with SSE parsing.
- Backend: Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2.x, psycopg 3, Pandas, Alembic, Pytest.
- RAG: LangChain; `PyPDFLoader` and `CSVLoader` from `langchain_community.document_loaders`; `RecursiveCharacterTextSplitter` from `langchain_text_splitters`; `HuggingFaceEmbeddings` from `langchain_huggingface`; supported `langchain_postgres` integration and `.as_retriever()`.
- Embeddings: `sentence-transformers/all-MiniLM-L6-v2`, locally on CPU. Long PDF chunks initially use size 1000 and overlap 200; preserve short CSV rows and all source metadata. Similarity retrieval initially uses configurable top-k 5.
- Language generation: hosted Hugging Face Inference API behind a provider interface. Verify selected `HF_MODEL` capabilities during integration; handle timeouts, rate limits and provider errors.
- Storage: the user's existing hosted Supabase PostgreSQL, relational KPI tables and pgvector. SSL, appropriate pooling and Alembic relational migrations are required. Verify the vector extension schema; never assume `public`.
- Forbidden: Streamlit, ChromaDB, Ollama, local LLM hosting, local PostgreSQL/pgvector installation, local PostgreSQL Docker as the primary database, replacing FastAPI with Supabase, and execution of arbitrary model-generated SQL, Python or JavaScript.

## Architecture and coding conventions

- Use a single monorepo with `apps/frontend` and `apps/backend/src/execbrief`, as specified in the master specification. Use a modular monolith and SOLID principles from Phase 1 onward.
- Dependencies flow `API -> Application -> Domain Interfaces <- Infrastructure`. Domain entities and contracts must not import FastAPI, LangChain, SQLAlchemy, Hugging Face or frontend libraries. Prefer standard Python dataclasses, enums and narrow protocols/ABCs for domain types.
- API routes handle transport, request/response validation, dependency injection and SSE serialization only. Keep SQL, RAG, calculations and LLM calls out of endpoints.
- Application use cases orchestrate domain interfaces; they must not import infrastructure implementations or construct clients/connections. Infrastructure adapts external types into domain values.
- Construct concrete dependencies in `core/container.py`; expose them through `api/dependencies.py`. Keep ORM models separate from domain entities and Pydantic transport schemas.
- Apply Repository for storage, dependency injection for services, and Strategy plus Factory/Registry for charts. Keep interfaces small, implementations substitutable, and abstractions tied to actual needs.
- Python modules/functions use snake_case, classes PascalCase and public contracts type hints. JSX components use PascalCase, JavaScript functions camelCase and hooks a `use` prefix. Keep network operations in feature services, stream state in hooks and chart rendering in dedicated components. `App.jsx` composes the UI.
- Validate untrusted inputs and generated output at boundaries. Use predefined analytical operations with validated parameters and parameterized repository queries. Define units, periods, denominator rules and missing/zero behavior for metrics; never silently turn missing data into zero.
- Use Pydantic v2 to validate ordered response blocks. Permit only text and bar/line chart specifications with approved dataset IDs and columns. Resolve chart rows on the backend from verified analytical datasets; final integrated charts cannot use hardcoded demonstration data.

## Data, grounding and security

- Generate fictional Nexora Solutions (Pvt) Ltd, business services, approximately 150 employees across Finance, Sales, Human Resources, Operations and IT. Use May through October 2026, a deterministic seed and one consistent source of facts for all six CSVs and six reports named in the specification. Label generated company data fictional.
- Keep semantic CSV ingestion separate from structured KPI import. Compute exact financial and operational metrics through SQLAlchemy repositories and Pandas, never solely from retrieved text.
- Preserve PDF filename/page/source path/document ID and CSV filename/row/dataset identifier. Implement deduplication and source provenance. Explanations and numerical claims must be supported by retrieved evidence and verified analytics; clearly state missing evidence.
- Keep `DATABASE_URL`, `HF_TOKEN`, `HF_MODEL` and `FRONTEND_ORIGIN` in backend configuration; the default frontend origin is `http://localhost:5173`. Never expose secrets through React/Vite variables, logs, responses or Git. Future `.env.example` contains blank secrets only.

## Streaming and verification

- Use `POST /api/chat/stream`, FastAPI `StreamingResponse`, and the seven event types `status`, `block_start`, `text_delta`, `block_end`, `chart`, `error`, `done`. Follow the contract in architecture.md until the dedicated API contract is implemented/documented.
- Preserve event order, stable block IDs, previous blocks and conversation history. Support cancellation, partial network frames, failures and completion. Display source references.
- Stream genuine incremental model output where supported. Never add artificial delays to imply generation. Clearly label Phase 1 mock streams and any documented validated-block fallback; replay is not token-level streaming.
- Test backend behavior with Pytest and mocked LLM responses. Automated tests must not require paid inference. Separately report any live Supabase/model checks and any skipped checks.
- Cover loaders, splitting, metadata, retrieval, KPI calculations, chart validation and unsupported types, event order, missing evidence and duplicate ingestion. Frontend tests cover ordered blocks, text deltas, both chart types and errors; include cancellation and fragmented SSE parsing.
- Finish with reproducible instructions for frontend/backend setup, Supabase/pgvector, hosted inference, generation, ingestion and running the complete application. Do not invent successful commands or test outcomes.
