import asyncio
from execbrief.application.use_cases.ask_grounded import AskGroundedUseCase
from execbrief.application.services.analytics_text import describe_row


def test_readable_revenue_missing_growth():
    text = describe_row("revenue", {"month": "2026-05", "actual_revenue": 12000000, "target_revenue": 13000000, "variance": -1000000, "growth_percent": None}, "LKR")
    assert "May 2026" in text and "LKR 12,000,000" in text
    assert "not available" in text and "None" not in text


def test_trend_chart_and_relevant_sources():
    class Llm:
        async def generate(self, task, context):
            if task == "plan":
                return {"operations": ["revenue"], "start": "2026-05", "end": "2026-10", "retrieve": False}
            return {"blocks": [{"type": "text", "content": context["evidence"]["revenue:0"]["content"], "sources": ["revenue:0"]}]}
    class Analytics:
        def calculate(self, *args):
            return {"id": "revenue", "units": "LKR", "columns": ["month", "actual_revenue", "target_revenue"], "rows": [{"month": "2026-05", "actual_revenue": 12, "target_revenue": 13}, {"month": "2026-06", "actual_revenue": 14, "target_revenue": 15}]}
    async def run():
        return [event async for event in AskGroundedUseCase(Llm(), Analytics(), None).execute("Show revenue trends", [])]
    events = asyncio.run(run())
    ends = [payload for kind, payload in events if kind == "block_end"]
    assert [s["id"] for s in ends[0]["sources"]] == ["revenue-summary:0"]
    charts = [payload for kind, payload in events if kind == "chart"]
    assert charts[0]["spec"]["chart_type"] == "bar"
    assert len(charts[0]["dataset"]["rows"]) == 2
