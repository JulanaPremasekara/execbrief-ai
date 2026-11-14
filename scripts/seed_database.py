from alembic.config import Config
from alembic import command
from execbrief.core.data_config import ROOT,DATA_ROOT
from execbrief.infrastructure.database.session import create_database_engine,ensure_vector
from execbrief.infrastructure.database.repositories.metrics_repository import MetricsRepository
if __name__=="__main__":
    try:
        command.upgrade(Config(str(ROOT/"apps/backend/alembic.ini")),"head")
        engine=create_database_engine()
        schema=ensure_vector(engine)
        counts=MetricsRepository(engine).import_directory(DATA_ROOT/"csv")
        print("pgvector verified; relational import counts:",counts)
        engine.dispose()
    except Exception as error:
        print("Database setup failed:",type(error).__name__,"Check local credentials, network and database permissions. Details suppressed to protect credentials.")
        raise SystemExit(1)

