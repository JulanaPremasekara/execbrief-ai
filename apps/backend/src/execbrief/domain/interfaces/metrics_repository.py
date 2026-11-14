from typing import Protocol
class MetricsRepository(Protocol):
    def fetch(self, dataset: str) -> list[dict]: ...

