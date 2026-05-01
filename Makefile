.PHONY: help install dev test test-cov lint format typecheck build docker-up docker-down clean pre-commit

help:
	@echo "Available targets:"
	@echo "  install     Install pre-commit hooks + dev dependencies"
	@echo "  dev         Start development server / watch mode"
	@echo "  test        Run unit tests"
	@echo "  test-cov    Run tests with coverage report (generates coverage.xml)"
	@echo "  lint        Run linter (ruff)"
	@echo "  format      Auto-format code (ruff format)"
	@echo "  typecheck   Run static type checker (mypy)"
	@echo "  build       Build production artefact"
	@echo "  docker-up   Start docker-compose services"
	@echo "  docker-down Stop docker-compose services"
	@echo "  clean       Remove generated artefacts and caches"
	@echo "  pre-commit  Run all pre-commit checks"

install:
	pre-commit install

dev:
	@echo "No dev server — project-init is a CLI tool"

test:
	@echo "No tests yet — see issues for the test plan"

test-cov:
	@echo "No tests yet — see issues for the test plan"

lint:
	pre-commit run --all-files

format:
	pre-commit run ruff-format --all-files || true

typecheck:
	@echo "No typecheck yet — see issues for the test plan"

build:
	@echo "No build artefact yet — see issues"

docker-up:
	@echo "No docker-compose yet"

docker-down:
	@echo "No docker-compose yet"

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .pytest_cache .mypy_cache .ruff_cache coverage.xml htmlcov 2>/dev/null || true

pre-commit:
	pre-commit run --all-files

# ── Quality Gates ──────────────────────────────────────────────────────────────

quality-gate-baseline: ## Record baseline metrics for regression detection
	@python3 scripts/quality_gate.py baseline

quality-gate-verify: ## Verify no regression since baseline
	@python3 scripts/quality_gate.py verify
