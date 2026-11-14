"""Real orchestration/analytics/SSE; external model and storage ports are fakes."""
import asyncio
import json
import threading
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient
from execbrief.main import app
from execbrief.api.dependencies import get_chat
from execbrief.core.live_chat import LiveChat
from execbrief.application.use_cases.ask_grounded import AskGroundedUseCase
from execbrief.infrastructure.analytics.pandas_engine import PandasAnalytics
from execbrief.infrastructure.data.synthetic import facts
from execbrief.domain.entities.document import Document

QUESTION = "How is our company performing over the last six months?"

class Repository:
    def fetch(self, dataset):
        return facts()[dataset]

class Retriever:
    def retrieve(self, question):
        assert question == QUESTION
        return [Document("Atlas acceptance was deferred.", {"filename": "Minutes.pdf", "page": 1})]

class Model:
    async def generate(self, task, context):
        if task == "plan":
            assert context["question"] == QUESTION
            return dict(operations=["revenue", "expenses"], start="2026-05", end="2026-10", retrieve=True)
        return {"blocks": [
            dict(type="text", content=context["evidence"]["revenue:0"]["content"], sources=["revenue:0"]),
            dict(type="chart", chart_type="line", dataset_id="revenue", x="month", y=["actual_revenue"]),
            dict(type="text", content="Atlas acceptance was deferred.", sources=["evidence:0"]),
            dict(type="chart", chart_type="bar", dataset_id="expenses", x="department", y=["actual_expenses"]),
            dict(type="text", content="Recommendation: Review delivery milestones.", sources=["evidence:0"]),
        ]}

def test_executive_question_through_sse():
    engine = Mock()
    case = AskGroundedUseCase(Model(), PandasAnalytics(Repository()), Retriever())
    app.dependency_overrides[get_chat] = lambda: LiveChat(lambda: (engine, case))
    try:
        response = TestClient(app).post("/api/chat/stream", json={"question": QUESTION})
    finally:
        app.dependency_overrides.clear()
    events = [(f.splitlines()[0][7:], json.loads(f.splitlines()[1][6:])) for f in response.text.strip().split("\n\n")]
    assert [p["sequence"] for _, p in events] == list(range(1, len(events)+1))
    assert [p["block_type"] for e,p in events if e == "block_start"] == ["text","chart","text","chart","text"]
    charts = [p for e,p in events if e == "chart"]
    assert [p["spec"]["chart_type"] for p in charts] == ["line","bar"]
    assert charts[0]["dataset"]["rows"][-1]["actual_revenue"] == 14000000
    assert events[-1][1]["outcome"] == "completed"
    assert events[-1][1]["stream_mode"] == "validated_blocks"
    assert any(s.get("page") == 1 for s in events[-1][1]["sources"])
    engine.dispose.assert_called_once()

def test_cancel_during_initialization_disposes_late_resource():
    async def run():
        started, release = threading.Event(), threading.Event()
        engine = Mock()
        def factory():
            started.set()
            release.wait(5)
            return engine, None
        iterator = LiveChat(factory).execute(QUESTION, [])
        await anext(iterator)
        pending = asyncio.create_task(anext(iterator))
        await asyncio.to_thread(started.wait, 5)
        pending.cancel()
        with pytest.raises(asyncio.CancelledError):
            await pending
        release.set()
        for _ in range(100):
            if engine.dispose.called:
                break
            await asyncio.sleep(.01)
        engine.dispose.assert_called_once()
    asyncio.run(run())

def test_cancel_during_generation_closes_iterator_and_engine():
    async def run():
        closed = asyncio.Event()
        entered = asyncio.Event()
        class Waiting:
            async def execute(self, *args):
                try:
                    entered.set()
                    await asyncio.Event().wait()
                    yield "done", {}
                finally:
                    closed.set()
        engine = Mock()
        iterator = LiveChat(lambda: (engine, Waiting())).execute(QUESTION, [])
        await anext(iterator)
        pending = asyncio.create_task(anext(iterator))
        await entered.wait()
        pending.cancel()
        with pytest.raises(asyncio.CancelledError):
            await pending
        assert closed.is_set()
        engine.dispose.assert_called_once()
    asyncio.run(run())
