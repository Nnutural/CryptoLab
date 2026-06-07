"""Architecture boundary regression tests."""

from __future__ import annotations

import ast
from pathlib import Path


def test_routers_do_not_import_models() -> None:
    routers_dir = Path(__file__).resolve().parents[1] / "app" / "routers"
    offenders: list[str] = []
    for path in routers_dir.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                if node.module == "app.models" or node.module.startswith("app.models."):
                    offenders.append(f"{path.name}:{node.lineno}")
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == "app.models" or alias.name.startswith("app.models."):
                        offenders.append(f"{path.name}:{node.lineno}")
    assert offenders == []
