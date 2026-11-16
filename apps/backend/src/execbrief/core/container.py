import os
from execbrief.application.use_cases.ask_executive import AskExecutiveUseCase
from execbrief.infrastructure.mock.response_provider import MockResponseProvider
from execbrief.core.runtime import execution_mode

def build_llm():
    from execbrief.core import data_config
    provider = os.getenv("LLM_PROVIDER", "huggingface").strip().lower()
    if provider in ("local", "ollama"):
        from execbrief.infrastructure.llm.local_provider import LocalProvider
        return LocalProvider(os.getenv("OLLAMA_MODEL", ""), os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434"), float(os.getenv("OLLAMA_TIMEOUT", "120")))
    if provider == "google":
        from execbrief.infrastructure.llm.google_provider import GoogleProvider
        return GoogleProvider(os.getenv("GOOGLE_MODEL"), os.getenv("GOOGLE_API_KEY"))
    if provider == "huggingface":
        from execbrief.infrastructure.llm.huggingface_provider import HuggingFaceProvider
        return HuggingFaceProvider(os.getenv("HF_MODEL"), os.getenv("HF_TOKEN"), os.getenv("HF_PROVIDER", "auto"))
    raise ValueError("LLM_PROVIDER must be huggingface, google, local or ollama")


def build_live():
    from execbrief.application.use_cases.ask_grounded import AskGroundedUseCase
    from execbrief.infrastructure.analytics.pandas_engine import PandasAnalytics
    from execbrief.infrastructure.database.repositories.metrics_repository import MetricsRepository
    llm=build_llm()
    engine,store,_=build_ingestion()
    return engine,AskGroundedUseCase(llm,PandasAnalytics(MetricsRepository(engine)),store)

def build_chat():
    if execution_mode()=="live":
        from execbrief.core.live_chat import LiveChat
        return LiveChat(build_live)
    return AskExecutiveUseCase(MockResponseProvider(), diagnostic_delay=0.4 if os.getenv("MOCK_STREAM_DIAGNOSTIC") == "1" else 0)

def build_ingestion():
    from execbrief.core.data_container import build_ingestion as compose
    return compose()

