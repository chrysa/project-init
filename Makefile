.PHONY: help install test lint pre-commit

help:
	@echo "Available targets:"
	@echo "  install     Install pre-commit hooks + dev dependencies"
	@echo "  test        Run tests"
	@echo "  lint        Run all linters"
	@echo "  pre-commit  Run all pre-commit checks"

install:
	pre-commit install

test:
	@echo "No tests yet — see issues for the test plan"

lint:
	pre-commit run --all-files

pre-commit:
	pre-commit run --all-files
