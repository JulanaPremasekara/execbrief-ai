from execbrief.application.use_cases.ask_executive import AskExecutiveUseCase
from execbrief.infrastructure.mock.response_provider import MockResponseProvider

def build_chat() -> AskExecutiveUseCase:
    return AskExecutiveUseCase(MockResponseProvider())

def build_ingestion():
    from execbrief.core.data_container import build_ingestion as compose
    return compose()

