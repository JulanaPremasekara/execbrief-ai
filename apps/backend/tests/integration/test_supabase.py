import os
import pytest
from sqlalchemy import text
pytestmark=pytest.mark.skipif(os.getenv("RUN_SUPABASE_TESTS")!="1",reason="Explicit live Supabase test opt-in required")

def test_live_database_and_seed():
    from execbrief.infrastructure.database.session import create_database_engine,ensure_vector
    from execbrief.infrastructure.database.repositories.metrics_repository import MetricsRepository
    from execbrief.core.data_config import DATA_ROOT
    engine=create_database_engine()
    try:
        assert ensure_vector(engine)
        repository=MetricsRepository(engine)
        first=repository.import_directory(DATA_ROOT/"csv")
        assert repository.import_directory(DATA_ROOT/"csv")==first
        assert len(repository.fetch("monthly_revenue"))==6
        assert next(r for r in repository.fetch("monthly_revenue") if r["month"]=="2026-10")["actual_revenue"]==14000000
    finally:
        engine.dispose()

def test_live_vectors_and_deduplication():
    from execbrief.core.data_container import build_ingestion
    from execbrief.core.data_config import DATA_ROOT
    engine,store,use_case=build_ingestion()
    try:
        first=use_case.execute(DATA_ROOT)
        assert use_case.execute(DATA_ROOT)==first
        with engine.connect() as connection:
            count=connection.execute(text("SELECT count(*) FROM langchain_pg_embedding WHERE collection_id=(SELECT uuid FROM langchain_pg_collection WHERE name='execbrief_phase2')")).scalar_one()
        assert count==sum(first.values())
        documents=store.retrieve("Why did October revenue decline?")
        assert len(documents)==5
        assert all("filename" in d.metadata for d in documents)
        assert any("October" in d.content for d in documents)
    finally:
        engine.dispose()
