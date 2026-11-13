# EXECBRIEF AI — COMPLETE FULL-STACK IMPLEMENTATION PROMPT

## 1. Your Role

Act as a senior AI engineer, full-stack software engineer, software architect, and RAG specialist.

Build a working, portfolio-quality application called:

**ExecBrief AI — Generative Executive Analytics & Decision Support Assistant**

The application enables executives to ask natural-language questions about company performance and receive evidence-grounded explanations, interactive charts, business insights, and actionable recommendations.

This is not a basic PDF chatbot or a static analytics dashboard. It is a conversational AI application combining:

- Retrieval-Augmented Generation (RAG)
- Structured business analytics
- Generative AI
- Dynamic chart generation
- Real-time streaming
- Clean Architecture
- SOLID principles
- Design patterns
- Modular monorepo organization

Implement a functional MVP first, but maintain proper architectural boundaries from the beginning.

---

# 2. Mandatory Technology Stack

### Frontend
- React.js with Vite
- JavaScript / JSX
- Tailwind CSS
- Recharts
- React Hooks
- Fetch API with ReadableStream
- Server-Sent Events (SSE) parsing

### Backend
- Python 3.11+
- FastAPI
- Pydantic v2
- SQLAlchemy 2.x
- Pandas
- psycopg 3
- Alembic
- Pytest

### RAG and AI
- LangChain
- `PyPDFLoader`
- `CSVLoader`
- `RecursiveCharacterTextSplitter`
- `HuggingFaceEmbeddings`
- `sentence-transformers/all-MiniLM-L6-v2`
- `langchain_postgres` vector store integration
- Hosted Hugging Face Inference API
- LangChain retriever interface

### Database
- Existing Supabase project
- Hosted Supabase PostgreSQL
- PostgreSQL `vector` extension (pgvector)
- Relational tables for structured KPIs
- Vector storage for document embeddings

Do not use:
- Streamlit
- ChromaDB
- Ollama
- Locally hosted LLMs
- Local PostgreSQL Docker containers as the primary database
- Arbitrary LLM-generated SQL or executable code

The user already has Supabase. Do not require a new database provider.

---

# 3. Mandatory Monorepo Architecture

Create a single Git repository containing separate frontend and backend applications.

Use a modular monolith with Clean Architecture.

Follow this folder structure:

```text
execbrief-ai/
│
├── apps/
│   ├── frontend/
│   │   ├── public/
│   │   ├── src/
│   │   │   ├── app/
│   │   │   │   └── App.jsx
│   │   │   │
│   │   │   ├── features/
│   │   │   │   ├── chat/
│   │   │   │   │   ├── components/
│   │   │   │   │   │   ├── ChatWindow.jsx
│   │   │   │   │   │   ├── ChatMessage.jsx
│   │   │   │   │   │   ├── MessageInput.jsx
│   │   │   │   │   │   └── StreamingStatus.jsx
│   │   │   │   │   ├── hooks/
│   │   │   │   │   │   └── useExecutiveStream.js
│   │   │   │   │   └── services/
│   │   │   │   │       └── chatApi.js
│   │   │   │   │
│   │   │   │   └── visualizations/
│   │   │   │       ├── components/
│   │   │   │       │   ├── BlockRenderer.jsx
│   │   │   │       │   ├── TextBlock.jsx
│   │   │   │       │   ├── BarChartBlock.jsx
│   │   │   │       │   └── LineChartBlock.jsx
│   │   │   │       └── registry/
│   │   │   │           └── chartRegistry.js
│   │   │   │
│   │   │   ├── shared/
│   │   │   │   ├── components/
│   │   │   │   ├── hooks/
│   │   │   │   └── utils/
│   │   │   │
│   │   │   └── main.jsx
│   │   │
│   │   ├── package.json
│   │   └── vite.config.js
│   │
│   └── backend/
│       ├── src/
│       │   └── execbrief/
│       │       ├── main.py
│       │       │
│       │       ├── api/
│       │       │   ├── routes/
│       │       │   │   ├── chat.py
│       │       │   │   ├── documents.py
│       │       │   │   └── health.py
│       │       │   ├── schemas/
│       │       │   │   ├── requests.py
│       │       │   │   └── responses.py
│       │       │   └── dependencies.py
│       │       │
│       │       ├── domain/
│       │       │   ├── entities/
│       │       │   │   ├── document.py
│       │       │   │   ├── metric.py
│       │       │   │   └── response_block.py
│       │       │   ├── interfaces/
│       │       │   │   ├── llm_provider.py
│       │       │   │   ├── document_retriever.py
│       │       │   │   ├── metrics_repository.py
│       │       │   │   └── analytics_provider.py
│       │       │   └── exceptions.py
│       │       │
│       │       ├── application/
│       │       │   ├── use_cases/
│       │       │   │   ├── ask_executive.py
│       │       │   │   ├── ingest_documents.py
│       │       │   │   └── generate_briefing.py
│       │       │   └── services/
│       │       │       ├── rag_service.py
│       │       │       ├── analytics_service.py
│       │       │       ├── query_planner.py
│       │       │       ├── response_planner.py
│       │       │       └── streaming_service.py
│       │       │
│       │       ├── infrastructure/
│       │       │   ├── database/
│       │       │   │   ├── session.py
│       │       │   │   ├── models/
│       │       │   │   └── repositories/
│       │       │   ├── rag/
│       │       │   │   ├── loaders/
│       │       │   │   │   ├── pdf_loader.py
│       │       │   │   │   └── csv_loader.py
│       │       │   │   ├── text_splitter.py
│       │       │   │   ├── embeddings.py
│       │       │   │   └── pgvector_store.py
│       │       │   ├── llm/
│       │       │   │   └── huggingface_provider.py
│       │       │   └── analytics/
│       │       │       └── pandas_engine.py
│       │       │
│       │       └── core/
│       │           ├── config.py
│       │           └── container.py
│       │
│       ├── migrations/
│       ├── tests/
│       │   ├── unit/
│       │   ├── integration/
│       │   └── contract/
│       ├── pyproject.toml
│       └── Dockerfile
│
├── data/
│   └── synthetic/
│       ├── csv/
│       └── pdf/
│
├── scripts/
│   ├── generate_synthetic_data.py
│   ├── seed_database.py
│   └── ingest_documents.py
│
├── docs/
│   ├── architecture.md
│   ├── api-contracts.md
│   └── rag-pipeline.md
│
├── .env.example
├── .gitignore
└── README.md
```

Do not create empty placeholder files unnecessarily. Every implemented module must have a clear responsibility.

---

# 4. Clean Architecture Rules

Follow this dependency direction:

**API → Application → Domain Interfaces ← Infrastructure**

### API Layer
Responsible for HTTP requests, response validation, dependency injection, and SSE serialization.

Do not put RAG, SQL, KPI calculations, or LLM logic inside API endpoints.

### Domain Layer
Contains business entities, domain rules, exceptions, and abstract contracts.

The domain must not depend on FastAPI, LangChain, SQLAlchemy, Hugging Face, or React.

### Application Layer
Contains use cases and workflow orchestration.

Examples:
- AskExecutiveUseCase
- IngestDocumentsUseCase
- GenerateBriefingUseCase

Coordinate retrieval, analytics, and generation through interfaces.

### Infrastructure Layer
Contains concrete implementations of external technologies.

Examples:
- LangChain PDF loader
- LangChain CSV loader
- Text splitter
- Embedding provider
- pgvector retriever
- SQLAlchemy repositories
- Hosted Hugging Face LLM client
- Pandas analytics engine

### Dependency Composition
Use `core/container.py` to construct infrastructure dependencies and inject them into application services.

Do not construct database connections or LLM clients directly inside use cases.

---

# 5. Synthetic Company and Data Generation

Create a fictional company named:

**Nexora Solutions (Pvt) Ltd**

Industry: Business services

Employees: Approximately 150

Departments:
- Finance
- Sales
- Human Resources
- Operations
- IT

Generate six months of synthetic company performance data ending in October 2026.

### CSV Files
- `monthly_revenue.csv`
- `department_expenses.csv`
- `sales_performance.csv`
- `employee_turnover.csv`
- `project_performance.csv`
- `operational_kpis.csv`

### PDF Reports
- Financial Performance Report
- Sales Performance Report
- HR Performance Report
- Operations Report
- Management Meeting Minutes
- Business Risk Register

Generate consistent data with realistic relationships.

For example, October revenue should be identical across CSV files, PDF reports, and generated executive explanations.

Use a deterministic random seed.

Create scripts to generate data and import it into Supabase.

All generated company data must be labeled fictional.

---

# 6. Supabase PostgreSQL Configuration

Use the existing Supabase project.

Do not install PostgreSQL or pgvector locally.

### Database Setup

Enable the PostgreSQL vector extension:

```sql
CREATE EXTENSION IF NOT EXISTS vector
WITH SCHEMA extensions;
```

Use the Supabase PostgreSQL connection string supplied by the dashboard.

Use psycopg 3 and SQLAlchemy 2.x.

Configure SSL and appropriate connection pooling.

Use Alembic migrations for relational database tables.

Ensure the LangChain PostgreSQL vector store works with the extension's installed schema.

Do not assume that pgvector is installed in the `public` schema.

### Environment Variables

Use:

```env
DATABASE_URL=
HF_TOKEN=
HF_MODEL=
FRONTEND_ORIGIN=http://localhost:5173
```

Use additional environment variables if needed.

Never expose database credentials or Hugging Face tokens to React.

Do not commit real secrets to GitHub.

Use Supabase as the database provider, not as a replacement for the FastAPI backend.

---

# 7. LangChain RAG Ingestion Pipeline

Implement a complete document ingestion pipeline.

### PDF Loading

Use:

`PyPDFLoader` from `langchain_community.document_loaders`.

Preserve:
- Filename
- Page number
- Source path
- Document ID

### CSV Loading

Use:

`CSVLoader` from `langchain_community.document_loaders`.

Convert CSV rows into LangChain documents.

Preserve:
- Source filename
- Row number
- Dataset identifier

### Text Splitting

Use:

`RecursiveCharacterTextSplitter` from `langchain_text_splitters`.

Initial configuration:
- Chunk size: 1000
- Chunk overlap: 200

Apply to long PDF content.

Avoid splitting short CSV records unnecessarily.

Preserve metadata.

### Embeddings

Use:

`HuggingFaceEmbeddings` from `langchain_huggingface`.

Embedding model:

`sentence-transformers/all-MiniLM-L6-v2`

Run embeddings locally on CPU.

### Vector Storage

Use the current supported integration from:

`langchain_postgres`

Store embeddings in Supabase PostgreSQL with pgvector.

Implement document deduplication.

### Retrieval

Use:

`.as_retriever()`

Initial retrieval:
- Similarity search
- Top-k = 5

Make retrieval parameters configurable.

Return relevant document chunks and source metadata.

### Important

CSVLoader is for semantic retrieval.

Use PostgreSQL SQL queries and Pandas for accurate financial and operational calculations.

Never calculate exact business KPIs solely from retrieved text.

---

# 8. Structured Analytics Engine

Implement an analytics service that calculates verified business metrics.

Required capabilities:

- Monthly revenue trends
- Revenue growth percentages
- Actual versus target comparisons
- Department expenses
- Budget variances
- Sales performance
- Employee turnover
- Project delays
- Operational KPI trends

Use SQLAlchemy repositories and Pandas.

Use predefined analytical operations with validated parameters.

Do not execute unrestricted LLM-generated SQL.

Return validated datasets that the chart service can use.

---

# 9. Hosted Hugging Face LLM

Use a hosted Hugging Face Inference API model.

Do not require Ollama or locally downloaded language models.

Create a model-provider interface and a Hugging Face implementation.

The LLM must:

- Interpret executive questions
- Use retrieved RAG evidence
- Use verified analytical results
- Generate executive explanations
- Identify business risks
- Recommend appropriate actions
- Select relevant charts
- Provide supporting sources

The model must not invent unsupported facts or numerical values.

Check that the selected hosted model supports the required inference capabilities.

Handle API failures, rate limits, and timeouts.

---

# 10. Structured Response Blocks

Use Pydantic v2 to validate ordered response blocks.

Support:

### Text Block
- ID
- Type: `text`
- Content

### Chart Block
- ID
- Type: `chart`
- Chart type: `bar` or `line`
- Title
- Dataset ID
- X-axis column
- Y-axis columns

Example:

```json
{
  "blocks": [
    {
      "id": "b1",
      "type": "text",
      "content": "Revenue increased over the reporting period."
    },
    {
      "id": "b2",
      "type": "chart",
      "chart_type": "line",
      "title": "Monthly Revenue",
      "dataset_id": "monthly_revenue",
      "x": "month",
      "y": ["actual_revenue", "target_revenue"]
    },
    {
      "id": "b3",
      "type": "text",
      "content": "October performance declined compared with September."
    }
  ]
}
```

The LLM generates chart specifications, not executable chart code.

The backend must resolve chart data from approved datasets.

Validate all dataset IDs and columns.

Do not allow arbitrary LLM-generated Python, JavaScript, or SQL execution.

---

# 11. Dynamic Chart Rendering

Use Recharts.

Implement:
- Bar charts
- Line charts

Use a Strategy Pattern and chart registry.

Charts must support:
- Multiple data series
- Titles
- Axis labels
- Tooltips
- Legends
- Responsive sizing

The LLM selects the chart type based on the question and available data.

Charts must appear inline within the assistant's response.

Do not force charts when they are not relevant.

---

# 12. Real-Time Streaming

Implement a POST endpoint:

`POST /api/chat/stream`

Use FastAPI StreamingResponse with SSE.

React must consume the response using fetch and ReadableStream.

### SSE Event Types

- status
- block_start
- text_delta
- block_end
- chart
- error
- done

### Expected Behavior

When the user asks:

"How is our company performing?"

The interface should:

1. Display the user question.
2. Show retrieval status.
3. Stream executive summary text.
4. Render a line chart.
5. Stream additional analysis.
6. Render a bar chart.
7. Stream management recommendations.
8. Display source references.
9. Complete the response.

Maintain exact event order.

Do not overwrite previous response blocks.

Use stable block IDs.

Handle stream cancellation and errors.

### True Streaming Requirement

Implement genuine incremental LLM text streaming when supported.

Do not simulate streaming with artificial delays.

If structured incremental generation is unreliable, use a documented validated-block fallback.

Do not misrepresent replayed blocks as token-level model streaming.

---

# 13. React Frontend

Create a professional executive chat interface.

Required components:
- ChatWindow
- ChatMessage
- MessageInput
- StreamingStatus
- BlockRenderer
- TextBlock
- BarChartBlock
- LineChartBlock
- SourceReferences

Create:

`useExecutiveStream.js`

Responsibilities:
- Manage fetch streaming
- Parse SSE events
- Maintain response blocks
- Preserve conversation history
- Track loading and errors
- Support cancellation
- Handle completion

Keep network logic in a dedicated API service.

Keep chart rendering in separate components.

Do not place the entire application in `App.jsx`.

Use a clean, responsive business-oriented design.

---

# 14. SOLID Principles and Design Patterns

Follow:
- Single Responsibility Principle
- Open/Closed Principle
- Liskov Substitution Principle
- Interface Segregation Principle
- Dependency Inversion Principle

Use:
- Strategy Pattern for chart implementations
- Factory/Registry Pattern for chart selection
- Repository Pattern for database access
- Dependency Injection for service dependencies

Avoid unnecessary abstractions.

Ensure each module has one clear responsibility.

---

# 15. Testing

Use Pytest for backend testing.

Test:
- PDF loading
- CSV loading
- Recursive splitting
- Metadata preservation
- Vector retrieval
- KPI calculations
- Chart specification validation
- Unsupported chart types
- Streaming event order
- Missing evidence
- Duplicate ingestion

Use mocked LLM responses for unit tests.

Include frontend tests for:
- Sequential block rendering
- Text streaming
- Bar charts
- Line charts
- Error handling

Do not require paid API calls for automated tests.

---

# 16. Required Demo Questions

The application must support:

1. How is our company performing?
2. Show revenue trends over the last six months.
3. Compare departmental expenses.
4. Which departments are underperforming?
5. Why did revenue decline in October?
6. What are our biggest operational risks?
7. How has employee turnover changed?
8. Which projects are delayed?
9. What management decisions require attention?
10. Compare actual performance against targets.

The assistant must select the appropriate combination of RAG, structured analytics, charts, and explanations.

---

# 17. Implementation Phases

### Phase 1 — End-to-End UI and Streaming

- Create monorepo structure.
- Set up React and FastAPI.
- Define interfaces and response contracts.
- Implement SSE streaming.
- Implement text and chart rendering.
- Test using synthetic mock responses.

### Phase 2 — Supabase and Data

- Generate synthetic CSV/PDF data.
- Configure Supabase PostgreSQL.
- Enable pgvector.
- Create relational tables.
- Implement PyPDFLoader and CSVLoader.
- Implement RecursiveCharacterTextSplitter.
- Generate embeddings.
- Store and retrieve vectors.
- Import structured metrics.

### Phase 3 — AI Integration

- Integrate hosted Hugging Face inference.
- Implement query planning.
- Implement RAG retrieval.
- Implement structured analytics.
- Generate validated response blocks.
- Connect AI output to SSE streaming.

### Phase 4 — Architecture and Testing

- Refine Clean Architecture boundaries.
- Apply SOLID principles.
- Implement design patterns.
- Add tests.
- Improve reliability.
- Complete documentation.

Build incrementally and verify each phase before proceeding.

---

# 18. Acceptance Criteria

The application is complete when:

- React can submit executive questions.
- FastAPI receives and processes them.
- LangChain retrieves relevant documents from Supabase pgvector.
- Structured KPI calculations return correct results.
- Hosted Hugging Face inference generates grounded executive explanations.
- The system produces validated text and chart blocks.
- React renders streamed content sequentially.
- Bar and line charts show verified data.
- Sources are displayed.
- The architecture follows Clean Architecture and SOLID.
- API endpoints do not contain business logic.
- Database access is isolated in repositories.
- RAG ingestion components are modular.
- Tests pass.
- Setup instructions are complete.

---

# 19. Final Instructions

Before writing code:

1. Inspect the existing project.
2. Propose the monorepo architecture.
3. Define domain models and interfaces.
4. Define the streaming event contract.
5. Identify required dependencies.
6. Create an implementation plan.

Then begin implementation.

Do not put everything into one folder.

Do not create a single massive backend file.

Do not combine database access, retrieval, analytics, and HTTP handling in one module.

Do not use hardcoded chart data in the final integrated application.

Do not claim a feature works unless it has been implemented and tested.

Provide exact setup instructions for:
- React
- FastAPI
- Supabase PostgreSQL
- pgvector
- Hugging Face inference
- Synthetic data generation
- RAG ingestion
- Running the complete application

**Start with Phase 1 and implement the project incrementally. Preserve the required monorepo structure and architecture throughout development.**