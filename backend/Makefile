.PHONY: help install install-dev venv dev test lint format clean db-upgrade db-downgrade db-migrate db-revision changelog

PYTHON := python3
VENV := venv
VENV_BIN := $(VENV)/bin
FLASK_APP := src.app:create_app

help:
	@echo "Aether AI Backend - Make Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make venv           Create virtual environment"
	@echo "  make install        Install production dependencies"
	@echo "  make install-dev    Install development dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make dev            Run Flask development server"
	@echo "  make test           Run tests with pytest"
	@echo "  make lint           Run pylint"
	@echo "  make format         Format code with black"
	@echo ""
	@echo "Database:"
	@echo "  make db-upgrade     Upgrade database to latest migration"
	@echo "  make db-downgrade   Downgrade database by one revision"
	@echo "  make db-migrate     Generate new migration (msg='description')"
	@echo "  make db-revision    Create empty migration (msg='description')"
	@echo ""
	@echo "Utilities:"
	@echo "  make changelog      Generate CHANGELOG.md"
	@echo "  make clean          Remove cache and temporary files"

venv:
	$(PYTHON) -m venv $(VENV)
	@echo "Virtual environment created. Activate with: source $(VENV_BIN)/activate"

install:
	$(VENV_BIN)/pip install --upgrade pip
	$(VENV_BIN)/pip install -r requirements.txt

install-dev: install
	$(VENV_BIN)/pip install -r requirements-dev.txt

dev:
	FLASK_APP=$(FLASK_APP) FLASK_ENV=development $(VENV_BIN)/flask run --host=0.0.0.0 --port=5001 --reload

test:
	$(VENV_BIN)/pytest tests/ -v --cov=src --cov-report=html --cov-report=term

lint:
	$(VENV_BIN)/pylint src/ --rcfile=.pylintrc

format:
	$(VENV_BIN)/black src/ tests/
	$(VENV_BIN)/isort src/ tests/

db-upgrade:
	$(VENV_BIN)/alembic upgrade head

db-downgrade:
	$(VENV_BIN)/alembic downgrade -1

db-migrate:
	@if [ -z "$(msg)" ]; then \
		echo "Error: Please provide a migration message using msg='your message'"; \
		exit 1; \
	fi
	$(VENV_BIN)/alembic revision --autogenerate -m "$(msg)"

db-revision:
	@if [ -z "$(msg)" ]; then \
		echo "Error: Please provide a revision message using msg='your message'"; \
		exit 1; \
	fi
	$(VENV_BIN)/alembic revision -m "$(msg)"

changelog:
	$(VENV_BIN)/git-changelog -o CHANGELOG.md

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.log" -delete
	rm -rf .pytest_cache .coverage htmlcov/ .mypy_cache/ build/ dist/ *.egg-info
	@echo "Cleaned cache and temporary files"

