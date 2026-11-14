import os
from execbrief.application.use_cases.ask_executive import AskExecutiveUseCase
from execbrief.infrastructure.mock.response_provider import MockResponseProvider
from execbrief.core.runtime import execution_mode

def build_live():
    from execbrief.application.use_cases.ask_grounded import AskGroundedUseCase
    from execbrief.infrastructure.llm.huggingface_provider import HuggingFaceProvider
    from execbrief.infrastructure.analytics.pandas_engine import PandasAnalytics
    from execbrief.infrastructure.database.repositories.metrics_repository import MetricsRepository
    llm=HuggingFaceProvider(os.getenv("HF_MODEL"),os.getenv("HF_TOKEN"),os.getenv("HF_PROVIDER","auto"))
    engine,store,_=build_ingestion()
    return engine,AskGroundedUseCase(llm,PandasAnalytics(MetricsRepository(engine)),store)

def build_chat():
    if execution_mode()=="live":
        from execbrief.core.live_chat import LiveChat
        return LiveChat(build_live)
    return AskExecutiveUseCase(MockResponseProvider())

def build_ingestion():
    from execbrief.core.data_container import build_ingestion as compose
    return compose()

