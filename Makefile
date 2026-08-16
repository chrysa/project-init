# makefile-tier: lib
.PHONY: help install install-dev dev test test-cov docker-test lint format format-check typecheck build docker-up docker-down clean pre-commit ci sync-standards-domains check-standards-domains

help:
	@echo "Available targets:"
	@echo "  install      Install pre-commit hooks"
	@echo "  install-dev  Install pre-commit hooks + dev dependencies"
	@echo "  dev          Start development server / watch mode"
	@echo "  test         Run unit tests"
	@echo "  test-cov     Run tests with coverage report (generates coverage.xml)"
	@echo "  lint         Run linter (ruff)"
	@echo "  format       Auto-format code (ruff format)"
	@echo "  format-check Check formatting without writing (CI)"
	@echo "  typecheck    Run static type checker (mypy)"
	@echo "  build        Build production artefact"
	@echo "  docker-up    Start docker-compose services"
	@echo "  docker-down  Stop docker-compose services"
	@echo "  clean        Remove generated artefacts and caches"
	@echo "  pre-commit   Run all pre-commit checks"
	@echo "  ci           Run the full local gate (lint + pre-commit + docker-test)"
	@echo "  sync-standards-domains   Regenerate profiles/domains.yaml from shared-standards"
	@echo "  check-standards-domains  Fail if profiles/domains.yaml has drifted (CI)"

install:
	pre-commit install

install-dev:
	pre-commit install
	@echo "Dev deps are provisioned in the container (Dockerfile.test) — see docker-test"

dev:
	@echo "No dev server — project-init is a CLI tool"

test:
	@echo "No tests yet — run docker-test for CI-compatible tests"

docker-test: ## Run tests inside Docker (CI-compatible)
	docker build -f Dockerfile.test -t project-init-test .
	docker run --rm project-init-test

test-cov:
	@echo "No tests yet — run docker-test for CI-compatible tests"

lint:
	pre-commit run --all-files

format:
	pre-commit run ruff-format --all-files || true

format-check:
	pre-commit run ruff-format --all-files

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

ci: lint check-standards-domains docker-test ## Run the full local gate (lint + drift + pre-commit + docker-test)

# ── Standards domain registry (generated from shared-standards) ─────────────────

sync-standards-domains: ## Regenerate profiles/domains.yaml from the shared-standards registry
	@python scripts/sync_standards_domains.py

check-standards-domains: ## Fail if profiles/domains.yaml has drifted from the source (CI)
	@python scripts/sync_standards_domains.py --check

# ── Quality Gates ──────────────────────────────────────────────────────────────

quality-gate-baseline: ## Record baseline metrics for regression detection
	@quality-gate-baseline

quality-gate-verify: ## Verify no regression since baseline
	@quality-gate-verify
