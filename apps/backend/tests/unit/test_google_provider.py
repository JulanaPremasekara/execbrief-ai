import asyncio
from unittest.mock import AsyncMock, patch
import httpx
import pytest
from execbrief.infrastructure.llm.google_provider import GoogleProvider

@pytest.mark.parametrize("content,valid", [('{"operations":["revenue"],"start":"2026-05","end":"2026-10","retrieve":true}', True), ('secret invalid output', False)])
def test_google_validation(content, valid):
    response = httpx.Response(200, json={"choices": [{"message": {"content": content}}]}, request=httpx.Request("POST", "https://example.test"))
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=response):
        if valid:
            assert asyncio.run(GoogleProvider("model", "secret").generate("plan", {}))["operations"] == ["revenue"]
        else:
            with pytest.raises(RuntimeError, match="invalid structured response") as error:
                asyncio.run(GoogleProvider("model", "secret").generate("plan", {}))
            assert "secret" not in str(error.value)

def test_select_google(monkeypatch):
    from execbrief.core.container import build_llm
    monkeypatch.setenv("LLM_PROVIDER", "google")
    monkeypatch.setenv("GOOGLE_MODEL", "model")
    monkeypatch.setenv("GOOGLE_API_KEY", "test-key")
    assert isinstance(build_llm(), GoogleProvider)
