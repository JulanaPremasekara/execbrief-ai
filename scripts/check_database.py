"""Safe diagnostics: never print connection strings or driver exception messages."""
import socket
from sqlalchemy.engine import make_url
from sqlalchemy import text
from execbrief.core.data_config import database_url
from execbrief.infrastructure.database.session import create_database_engine

if __name__ == "__main__":
    try:
        url=make_url(database_url())
        socket.getaddrinfo(url.host,url.port or 5432)
    except socket.gaierror:
        print("Database hostname cannot be resolved. Configure the dashboard session-pooler URI locally.")
        raise SystemExit(1)
    except Exception:
        print("Configure a valid DATABASE_URL locally.")
        raise SystemExit(1)
    engine=create_database_engine()
    try:
        with engine.connect() as connection:
            assert connection.execute(text("SELECT 1")).scalar_one()==1
        print("Database connection verified.")
    except Exception:
        print("Database connection failed. Check credentials, SSL, project status and network access locally.")
        raise SystemExit(1)
    finally:
        engine.dispose()
