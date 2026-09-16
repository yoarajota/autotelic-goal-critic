"""Enforces the structural thresholds declared in .sota/quality-gates.yaml.

`radon cc -n C -s src` is the readable report and stays in the quality runner for humans, but it
exits 0 even when it prints a rank-C block, so it cannot be the gate. This script measures the
same source and exits non-zero on a violation: a threshold that cannot fail is decoration.

Complexity comes from radon (the declared tool); function length, file length and nesting depth
come from the standard library AST, because radon does not report them. Nesting depth stands in
for the declared `max_call_depth`: call graph depth needs a resolver, while block nesting is what
actually makes a function unreadable, and the substitution is recorded here rather than silently
applied. Thresholds are duplicated from .sota/quality-gates.yaml deliberately: `pytest` fails if
the two ever disagree, so the coupling is checked instead of trusted.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

from radon.complexity import cc_visit

CYCLOMATIC_COMPLEXITY_MAX = 15
FUNCTION_LENGTH_MAX = 60
FILE_LENGTH_MAX = 500
NESTING_DEPTH_MAX = 8

NESTING_NODES = (
    ast.For,
    ast.AsyncFor,
    ast.While,
    ast.If,
    ast.Try,
    ast.With,
    ast.AsyncWith,
    ast.Match,
)


def _max_nesting(node: ast.AST, depth: int = 0) -> int:
    """Deepest control-flow nesting under `node`, not descending into nested functions."""
    deepest = depth
    for child in ast.iter_child_nodes(node):
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
            continue
        nested = depth + 1 if isinstance(child, NESTING_NODES) else depth
        deepest = max(deepest, _max_nesting(child, nested))
    return deepest


def _violations(path: Path) -> list[str]:
    source = path.read_text(encoding="utf-8")
    lines = source.splitlines()
    found: list[str] = []

    if len(lines) > FILE_LENGTH_MAX:
        found.append(f"{path}: {len(lines)} lines (max {FILE_LENGTH_MAX})")

    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as exc:
        return [*found, f"{path}: unparseable — {exc}"]

    for block in cc_visit(source):
        if block.complexity > CYCLOMATIC_COMPLEXITY_MAX:
            found.append(
                f"{path}:{block.lineno}: {block.name} cyclomatic complexity "
                f"{block.complexity} (max {CYCLOMATIC_COMPLEXITY_MAX})"
            )

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if node.end_lineno is not None:
            length = node.end_lineno - node.lineno + 1
            if length > FUNCTION_LENGTH_MAX:
                found.append(
                    f"{path}:{node.lineno}: {node.name} is {length} lines "
                    f"(max {FUNCTION_LENGTH_MAX})"
                )
        depth = _max_nesting(node)
        if depth > NESTING_DEPTH_MAX:
            found.append(
                f"{path}:{node.lineno}: {node.name} nests {depth} blocks "
                f"(max {NESTING_DEPTH_MAX})"
            )
    return found


def main() -> int:
    roots = [Path(arg) for arg in sys.argv[1:]] or [Path("src")]
    files = sorted(p for root in roots if root.exists() for p in root.rglob("*.py"))
    violations = [v for path in files for v in _violations(path)]
    if violations:
        print("structural thresholds violated:", file=sys.stderr)
        for violation in violations:
            print(f"  {violation}", file=sys.stderr)
        return 1
    print(f"structural thresholds ok ({len(files)} file(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
