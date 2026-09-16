.PHONY: setup teardown quality test

setup:
	uv sync

teardown:
	rm -rf .venv

# The single quality entry point: exits non-zero on any violation.
# Each check below maps to a row of iso5055.weaknesses in .sota/quality-gates.yaml.
quality:
	uv run ruff check .
	uv run mypy --strict src
	uv run radon cc -n C -s src
	uv run python tools/complexity_gate.py src
	uv run bandit -q -r src
	uv run pylint --disable=all --enable=duplicate-code src
	uv run vulture src
	uv run lint-imports
	gitleaks detect --no-banner --source .

test:
	uv run pytest
