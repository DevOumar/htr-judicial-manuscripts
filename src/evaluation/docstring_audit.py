"""Audit Google-style docstring coverage for Python functions."""

from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
from typing import Any, Dict, List


def audit_src(src_dir: str = "src") -> Dict[str, Any]:
    """Count functions and docstrings under ``src``.

    Args:
        src_dir: Source directory to scan.

    Returns:
        Coverage summary with per-file missing function names.
    """
    files: List[Dict[str, Any]] = []
    total_functions = 0
    total_docstrings = 0
    for path in sorted(Path(src_dir).rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        functions = [node for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]
        if not functions:
            continue
        documented = [node for node in functions if ast.get_docstring(node)]
        missing = [node.name for node in functions if not ast.get_docstring(node)]
        total_functions += len(functions)
        total_docstrings += len(documented)
        files.append(
            {
                "file": str(path),
                "functions": len(functions),
                "docstrings": len(documented),
                "coverage": len(documented) / len(functions) if functions else 1.0,
                "missing": missing,
            }
        )
    return {
        "total_functions": total_functions,
        "total_docstrings": total_docstrings,
        "coverage": total_docstrings / total_functions if total_functions else 1.0,
        "files": files,
    }


def main() -> None:
    """Write a docstring coverage report."""
    parser = argparse.ArgumentParser(description="Audit Python function docstring coverage.")
    parser.add_argument("--src-dir", default="src")
    parser.add_argument("--output", default="outputs/docstring_audit/docstring_audit_report.json")
    args = parser.parse_args()
    report = audit_src(args.src_dir)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, ensure_ascii=False)
    print(json.dumps({k: v for k, v in report.items() if k != "files"}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
