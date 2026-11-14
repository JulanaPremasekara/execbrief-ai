import asyncio
from types import SimpleNamespace
import pytest
from execbrief.infrastructure.llm import huggingface_provider as module

@pytest.mark.parametrize("failure",[TimeoutError(),ValueError("invalid")])
def test_provider_failure_is_sanitized(monkeypatch,failure):
    class Client:
        def __init__(self,**kwargs): pass
        async def __aenter__(self): return self
        async def __aexit__(self,*args): pass
        async def chat_completion(self,**kwargs): raise failure
    monkeypatch.setattr(module,"AsyncInferenceClient",Client)
    with pytest.raises(module.ProviderError,match="Hosted inference failed"):
        asyncio.run(module.HuggingFaceProvider("org/model","test").generate("plan",{}))

def test_rate_limit_retry_and_validation(monkeypatch):
    calls=[]
    class Client:
        def __init__(self,**kwargs): pass
        async def __aenter__(self): return self
        async def __aexit__(self,*args): pass
        async def chat_completion(self,**kwargs):
            calls.append(kwargs)
            if len(calls)==1:
                error=RuntimeError()
                error.response=SimpleNamespace(status_code=429)
                raise error
            return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content='{"operations":["revenue"],"retrieve":true,"start":"2026-05","end":"2026-10"}'))])
    async def no_wait(*args): pass
    monkeypatch.setattr(module,"AsyncInferenceClient",Client)
    monkeypatch.setattr(module.asyncio,"sleep",no_wait)
    result=asyncio.run(module.HuggingFaceProvider("org/model","test").generate("plan",{}))
    assert result["operations"]==["revenue"]
    assert len(calls)==2

def test_malformed_response_rejected(monkeypatch):
    class Client:
        def __init__(self,**kwargs): pass
        async def __aenter__(self): return self
        async def __aexit__(self,*args): pass
        async def chat_completion(self,**kwargs):
            return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content='{"sql":"DROP TABLE metrics"}'))])
    monkeypatch.setattr(module,"AsyncInferenceClient",Client)
    with pytest.raises(module.ProviderError):
        asyncio.run(module.HuggingFaceProvider("org/model","test").generate("plan",{}))
