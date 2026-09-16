.PHONY: setup teardown quality test poc

setup:
	uv sync

teardown:
	rm -rf .venv

# The single quality entry point: exits non-zero on any violation.
# Each check below maps to a row of iso5055.weaknesses in .sota/quality-gates.yaml.
quality:
	uv run ruff check .
	uv run mypy --strict src poc
	uv run radon cc -n C -s src
	uv run python tools/complexity_gate.py src poc
	uv run bandit -q -r src
	uv run pylint --disable=all --enable=duplicate-code src
	uv run vulture src
	uv run lint-imports
	gitleaks detect --no-banner --source .

test:
	uv run pytest

# The proof of concept. Writes the raw curve data behind E-002.
poc:
	uv run python poc/run_poc.py --budget 60000 --eval-every 5000 --seeds 0 1 2 3 4 --saturation-budget 200000 --out evidence-data/E-002-poc-runs.json
