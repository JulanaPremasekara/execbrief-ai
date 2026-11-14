from execbrief.application.use_cases.ask_executive import AskExecutiveUseCase
from execbrief.infrastructure.mock.response_provider import MockResponseProvider

def build_chat() -> AskExecutiveUseCase:
    import os
    from execbrief.core import data_config
    if os.getenv("EXECBRIEF_MODE","mock")=="live":
        from execbrief.application.use_cases.ask_grounded import AskGroundedUseCase
        from execbrief.infrastructure.llm.huggingface_provider import HuggingFaceProvider
        from execbrief.infrastructure.analytics.pandas_engine import PandasAnalytics
        from execbrief.infrastructure.database.repositories.metrics_repository import MetricsRepository
        llm=HuggingFaceProvider(os.getenv("HF_MODEL"),os.getenv("HF_TOKEN"),os.getenv("HF_PROVIDER","auto"))
        class LiveChat:
            stream_mode="validated_blocks"
            async def execute(self,question,history):
                import asyncio
                engine=None
                try:
                    yield "status",dict(stage="connecting",message="Connecting to evidence sources",stream_mode=self.stream_mode)
                    engine,store,_=await asyncio.to_thread(build_ingestion)
                    use_case=AskGroundedUseCase(llm,PandasAnalytics(MetricsRepository(engine)),store)
                    async for event in use_case.execute(question,history):
                        yield event
                finally:
                    if engine is not None:
                        engine.dispose()
        return LiveChat()
    return AskExecutiveUseCase(MockResponseProvider())

def build_ingestion():
    from execbrief.core.data_container import build_ingestion as compose
    return compose()

