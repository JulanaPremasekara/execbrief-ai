import json
import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from execbrief.main import app
from execbrief.api.dependencies import get_chat
from execbrief.api.schemas.responses import ChartPayload
from execbrief.infrastructure.mock.response_provider import MockResponseProvider

client = TestClient(app)

def events(question="How are we performing?"):
    response = client.post("/api/chat/stream", json={"question": question})
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    return [(frame.splitlines()[0][7:], json.loads(frame.splitlines()[1][6:]))
            for frame in response.text.strip().split("\n\n")]

def test_sequence_and_data():
    stream = events()
    assert [p["sequence"] for _, p in stream] == list(range(1, len(stream)+1))
    assert len({p["message_id"] for _,p in stream}) == 1
    order = []
    active = None
    for event,p in stream:
        if event == "block_start":
            assert active is None
            active = p["block_id"]
            if p["block_type"] == "text": order.append("text")
        elif event == "chart":
            assert active == p["block_id"]
            order.append(p["spec"]["chart_type"])
            ChartPayload.model_validate({k:p[k] for k in ["block_id","spec","dataset"]})
        elif event == "block_end":
            assert active == p["block_id"]
            active = None
    assert order == ["text","line","text","bar","text"]
    assert stream[-1][0] == "done"
    assert stream[-1][1]["sources"]

def test_text_only_and_health():
    assert not any(e == "chart" for e,_ in events("text only"))
    assert client.get("/api/health").json() == {"status":"ok","mode":"mock"}

@pytest.mark.parametrize("question", ["", "   ", "x"*2001])
def test_invalid_request(question):
    assert client.post("/api/chat/stream",json={"question":question}).status_code == 422

@pytest.mark.parametrize("field,value", [("chart_type","pie"),("dataset_id","unknown"),("x","unknown"),("y",["unknown"])])
def test_invalid_chart(field,value):
    block = MockResponseProvider().respond("demo",[])[1]
    with pytest.raises(ValidationError):
        ChartPayload(block_id=block.id,spec={**block.spec,field:value},dataset=block.dataset)

def test_failure_is_terminal():
    class Broken:
        async def execute(self,*args):
            yield "status", {"stage":"preparing","message":"Preparing","stream_mode":"mock"}
            raise RuntimeError("private detail")
    app.dependency_overrides[get_chat] = lambda: Broken()
    try:
        stream=events()
        assert [e for e,_ in stream] == ["status","error","done"]
        assert "private detail" not in str(stream)
    finally:
        app.dependency_overrides.clear()
