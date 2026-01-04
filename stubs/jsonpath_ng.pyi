"""Custom types for jsonpath_ng for use with external code."""
from typing import Any

class DatumInContext:
    value: dict[str, Any]

class JSONPath:
    def find(self, doc: dict[str, Any]) -> list[DatumInContext]: ...

def parse(path: str) -> JSONPath: ...
