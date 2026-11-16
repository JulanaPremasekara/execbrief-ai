from execbrief.application.services.revenue_briefing import revenue_briefing
from execbrief.application.services.response_planner import ResponsePlanner


def test_verified_summary_and_order():
    data = {"id": "revenue", "columns": ["month", "actual_revenue", "target_revenue"], "rows": [
        {"month": "2026-09", "actual_revenue": 15000000, "target_revenue": 16000000},
        {"month": "2026-10", "actual_revenue": 14000000, "target_revenue": 16000000}]}
    sources = {}
    response = revenue_briefing(data, sources)
    blocks = ResponsePlanner().resolve(response, {"revenue": data}, sources)
    assert [block.type for block in blocks] == ["text", "chart", "text", "text"]
    assert "6.7%" in blocks[0].content
    assert "87.5%" in blocks[2].content
    assert blocks[1].dataset is data


def test_missing_and_zero_values():
    data = {"rows": [{"month": "2026-09", "actual_revenue": 0}, {"month": "2026-10", "actual_revenue": None, "target_revenue": 0}]}
    response = revenue_briefing(data, {})
    assert "not available" in response["blocks"][0]["content"]
    assert "%" not in response["blocks"][0]["content"]
