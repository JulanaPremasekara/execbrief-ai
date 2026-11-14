from typing import Protocol
class AnalyticsProvider(Protocol):
    def calculate(self, operation: str, start: str, end: str) -> dict: ...

