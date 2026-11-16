import asyncio
import json
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from execbrief.infrastructure.llm.local_provider import LocalProvider, LocalProviderError


@pytest.mark.parametrize("content,valid", [('{"operations":["revenue"]}', True), ('secret invalid', False)])
def test_validation(content, valid):
    response = httpx.Response(200, json={"done": True, "message": {"content": content}}, request=httpx.Request("POST", "http://localhost"))
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=response) as post:
        if valid:
            assert asyncio.run(LocalProvider("test").generate("plan", {}))["operations"] == ["revenue"]
            assert post.call_args.kwargs["json"]["stream"] is False
            assert "properties" in post.call_args.kwargs["json"]["format"]
        else:
            with pytest.raises(LocalProviderError, match="invalid structured response"):
                asyncio.run(LocalProvider("test").generate("plan", {}))


@pytest.mark.parametrize("failure", [httpx.ConnectError("secret"), httpx.ReadTimeout("secret")])
def test_network_errors(failure):
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock, side_effect=failure):
        with pytest.raises(LocalProviderError) as error:
            asyncio.run(LocalProvider("test").generate("plan", {}))
        assert "secret" not in str(error.value)


def test_cancellation():
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock, side_effect=asyncio.CancelledError):
        with pytest.raises(asyncio.CancelledError):
            asyncio.run(LocalProvider("test").generate("plan", {}))


def test_paraphrased_fact_rejected():
    content = json.dumps({"blocks": [{"type": "text", "content": "Invented fact.", "sources": ["e1"]}]})
    response = httpx.Response(200, json={"done": True, "message": {"content": content}}, request=httpx.Request("POST", "http://localhost"))
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=response):
        with pytest.raises(LocalProviderError):
            asyncio.run(LocalProvider("test").generate("response", {"evidence": {"e1": {"content": "Verified fact."}}}))


def test_selected_source_expands_verified_text():
    content = json.dumps({"blocks": [{"type": "text", "content": "", "sources": ["e1"]}]})
    response = httpx.Response(200, json={"done": True, "message": {"content": content}}, request=httpx.Request("POST", "http://localhost"))
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=response):
        result = asyncio.run(LocalProvider("test").generate("response", {"evidence": {"e1": {"content": "Verified fact."}}}))
        assert result["blocks"][0]["content"] == "Verified fact."
        from execbrief.application.services.response_planner import ResponsePlanner
        assert ResponsePlanner().resolve(result, {}, {"e1": {"content": "Verified fact."}})[0].content == "Verified fact."


def test_selection(monkeypatch):
    from execbrief.core.container import build_llm
    monkeypatch.setenv("LLM_PROVIDER", "local")
    monkeypatch.setenv("OLLAMA_MODEL", "test")
    assert isinstance(build_llm(), LocalProvider)


def test_docker_host_configuration():
    assert LocalProvider("test", "http://host.docker.internal:11434").base_url == "http://host.docker.internal:11434"
    with pytest.raises(ValueError):
        LocalProvider("test", "http://untrusted.example:11434")


@pytest.mark.parametrize("source,valid", [("evidence:0", True), ("report.pdf", False)])
def test_response_citations(source, valid):
    content = json.dumps({"blocks": [{"type": "text", "content": "Verified fact.", "sources": [source]}]})
    response = httpx.Response(200, json={"done": True, "message": {"content": content}}, request=httpx.Request("POST", "http://localhost"))
    context = {"evidence": {"evidence:0": {"content": "Verified fact."}}}
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=response) as post:
        if valid:
            result = asyncio.run(LocalProvider("test").generate("response", context))
            assert result["blocks"][0]["sources"] == [source]
        else:
            with pytest.raises(LocalProviderError):
                asyncio.run(LocalProvider("test").generate("response", context))
        items = post.call_args.kwargs["json"]["format"]["$defs"]["GeneratedBlock"]["properties"]["sources"]["items"]
        assert items["enum"] == ["evidence:0"]
