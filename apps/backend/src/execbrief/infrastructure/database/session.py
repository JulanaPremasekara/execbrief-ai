from sqlalchemy import create_engine, text, event
from sqlalchemy.engine import make_url
from execbrief.core.data_config import database_url

def create_database_engine():
    url = make_url(database_url()).set(drivername="postgresql+psycopg")
    if not url.host or not (url.host.endswith(".supabase.co") or url.host.endswith(".supabase.com")):
        raise ValueError("Use the existing hosted Supabase PostgreSQL connection")
    if url.port == 6543:
        raise ValueError("Use direct or session-pooler port 5432 for ingestion")
    engine = create_engine(url, pool_size=3, max_overflow=2, pool_pre_ping=True,
        hide_parameters=True, connect_args={"sslmode":"require", "connect_timeout":15, "prepare_threshold":None})
    return engine

def ensure_vector(engine):
    with engine.begin() as connection:
        schema = connection.execute(text("SELECT n.nspname FROM pg_extension e JOIN pg_namespace n ON n.oid=e.extnamespace WHERE e.extname='vector'")).scalar()
        if schema is None:
            connection.execute(text("CREATE SCHEMA IF NOT EXISTS extensions"))
            connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA extensions"))
            schema = "extensions"
        connection.execute(text("CREATE SCHEMA IF NOT EXISTS execbrief"))
    quoted = engine.dialect.identifier_preparer.quote(schema)
    @event.listens_for(engine, "connect")
    def search_path(dbapi_connection, record):
        previous = dbapi_connection.autocommit
        dbapi_connection.autocommit = True
        with dbapi_connection.cursor() as cursor:
            cursor.execute(f"SET search_path TO execbrief, {quoted}, public")
        dbapi_connection.autocommit = previous
    engine.dispose()
    return schema

