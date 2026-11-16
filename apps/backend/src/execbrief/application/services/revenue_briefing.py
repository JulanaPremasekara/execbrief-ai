"""Build an executive revenue briefing from verified rows, without invented causes."""
from datetime import datetime


def revenue_briefing(dataset: dict, sources: dict, chart_type: str = "bar") -> dict:
    rows = sorted(dataset["rows"], key=lambda row: row["month"])
    latest = rows[-1]
    month = datetime.strptime(latest["month"], "%Y-%m").strftime("%B %Y")
    actual, target = latest.get("actual_revenue"), latest.get("target_revenue")
    money = lambda value: "not available" if value is None else f"LKR {value:,.0f}"
    summary = f"{month} revenue was {money(actual)} against a target of {money(target)}."
    insights = []
    if len(rows) > 1 and actual is not None and rows[-2].get("actual_revenue") is not None:
        prior = rows[-2]["actual_revenue"]
        difference = actual - prior
        direction = "increased" if difference > 0 else "decreased" if difference < 0 else "was unchanged"
        change = f"Revenue {direction}"
        if difference:
            change += f" by {money(abs(difference))}"
            if prior != 0:
                change += f" ({abs(difference / prior * 100):.1f}%)"
        change += " compared with the previous reporting month."
        summary += " " + change
        insights.append(change)
    if actual is not None and target is not None:
        gap = actual - target
        insights.append(f"Revenue was {money(abs(gap))} {'below' if gap < 0 else 'above'} target." if gap else "Revenue matched the target.")
        if target > 0:
            insights.append(f"Target attainment was {actual / target * 100:.1f}%.")
    insights.append("These figures establish performance, but do not establish the cause of any change.")
    texts = ["Revenue Performance Overview\n" + summary,
             "Key business insights\n" + "\n".join("• " + item for item in insights),
             "Recommended actions\n• Review the revenue variance with the sales and finance teams.\n• Check contract and billing records before attributing a cause.\n• Monitor revenue recovery against the approved target.\nThese are suggested follow-up actions, not findings from company reports."]
    blocks = []
    for index, content in enumerate(texts):
        key = f"revenue-summary:{index}"
        sources[key] = {"id": key, "filename": "Verified revenue analysis · " + month, "content": content}
        blocks.append({"type": "text", "content": content, "sources": [key]})
        if index == 0:
            blocks.append({"type": "chart", "dataset_id": "revenue", "chart_type": chart_type, "x": "month", "y": ["actual_revenue", "target_revenue"]})
    return {"blocks": blocks}
