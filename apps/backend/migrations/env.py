from alembic import context
from execbrief.infrastructure.database.session import create_database_engine, ensure_vector
from execbrief.infrastructure.database.models.metrics import metadata
engine=create_database_engine()
ensure_vector(engine)
with engine.connect() as connection:
    context.configure(connection=connection,target_metadata=metadata,version_table_schema="execbrief")
    with context.begin_transaction():
        context.run_migrations()
engine.dispose()

