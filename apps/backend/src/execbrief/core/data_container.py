from execbrief.infrastructure.database.session import create_database_engine, ensure_vector
from execbrief.infrastructure.rag.embeddings import build_embeddings
from execbrief.infrastructure.rag.pgvector_store import VectorStore
from execbrief.infrastructure.rag.loaders.pdf_loader import PDFLoader
from execbrief.infrastructure.rag.loaders.csv_loader import CSVLoader
from execbrief.infrastructure.rag.text_splitter import TextSplitter
from execbrief.application.use_cases.ingest_documents import IngestDocumentsUseCase
def build_ingestion():
    engine=create_database_engine()
    ensure_vector(engine)
    store=VectorStore(engine,build_embeddings())
    return engine,store,IngestDocumentsUseCase({".pdf":PDFLoader(),".csv":CSVLoader()},TextSplitter(),store)

