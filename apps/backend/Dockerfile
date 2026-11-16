FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY apps/backend/pyproject.toml apps/backend/pyproject.toml
COPY apps/backend/src apps/backend/src
RUN pip install --no-cache-dir -e ./apps/backend
COPY apps/backend/alembic.ini apps/backend/alembic.ini
COPY apps/backend/migrations apps/backend/migrations
COPY scripts scripts
RUN useradd --create-home appuser && mkdir -p /app/.cache/embeddings && chown -R appuser:appuser /app
USER appuser
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "execbrief.main:app", "--host", "0.0.0.0", "--port", "8000"]
