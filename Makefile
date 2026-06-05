PYTHON := .venv/bin/python
PIP := .venv/bin/pip
PYTEST := .venv/bin/pytest
RUFF := .venv/bin/ruff
MYPY := .venv/bin/mypy
PRE_COMMIT := .venv/bin/pre-commit

PACKAGE := package_snowball

.PHONY: help setup install-dev format lint typecheck test check clean pre-commit-install

help:
	@echo "setup              Create venv and install dev dependencies"
	@echo "install-dev        Install project in editable mode with dev extras"
	@echo "format             Run ruff formatter"
	@echo "lint               Run ruff linter"
	@echo "typecheck          Run mypy"
	@echo "test               Run pytest"
	@echo "check              format + lint + typecheck + test"
	@echo "pre-commit-install Install git hooks"
	@echo "clean              Remove caches"

# Команда для первичной настройки проекта на компьютере
setup:
	python3.13 -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install pre-commit ruff mypy
	.venv/bin/pre-commit install

# Ручной запуск линтеров и форматирования через pre-commit на всех файлах
lint:
	.venv/bin/pre-commit run --all-files

# Отдельный быстрый запуск ruff, если хочется проверить код без pre-commit
ruff:
	.venv/bin/ruff check . --fix
	.venv/bin/ruff format .

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete



install-dev:
	$(PIP) install -e ".[dev]"

format:
	$(RUFF) format src tests

typecheck:
	$(MYPY) src tests

test:
	$(PYTEST)

check: format lint typecheck test

pre-commit-install:
	$(PRE_COMMIT) install
