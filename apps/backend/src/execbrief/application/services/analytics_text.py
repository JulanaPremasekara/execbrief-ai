"""Deterministic prose from verified analytical rows."""
from datetime import datetime


def describe_row(operation: str, row: dict, units: str) -> str:
    def value(key):
        number = row.get(key)
        if number is None:
            return "not available"
        if isinstance(number, (int, float)):
            formatted = f"{number:,.2f}".rstrip("0").rstrip(".") if isinstance(number, float) else f"{number:,}"
            if "percent" in key:
                return formatted + "%"
            return ("LKR " if units == "LKR" else "") + formatted
        return str(number)

    month = row.get("month")
    label = datetime.strptime(month, "%Y-%m").strftime("%B %Y") if month else str(row.get("department", row.get("project", operation.title())))
    if operation == "revenue":
        growth = "Month-over-month growth is not available." if row.get("growth_percent") is None else f"Month-over-month growth was {value('growth_percent')}."
        return f"{label}: revenue was {value('actual_revenue')} against a target of {value('target_revenue')}. Revenue minus target was {value('variance')}. {growth}"
    fields = [f"{key.replace('_', ' ')}: {value(key)}" for key in row if key not in ("month", "department", "project")]
    return f"{label}: " + "; ".join(fields) + "."
