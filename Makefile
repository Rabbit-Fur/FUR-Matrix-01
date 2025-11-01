.PHONY: setup lint fmt unit cov serve-bot serve-web ingest export test codex codex-fix docker-shell

PYTHON ?= python
PIP ?= pip

setup:
	$(PIP) install -r requirements.txt

lint:
	black --check .
	ruff check .
	flake8

fmt:
	black .
	ruff check . --fix
	isort .

unit:
	pytest -m "not slow"

cov:
	pytest --cov=. --cov-report=term-missing

serve-bot:
	$(PYTHON) -m bot.bot_main

serve-web:
	$(PYTHON) main_app.py

ingest:
	$(PYTHON) scripts/parse_knowledge.py --input Wissen --output build/knowledge

export:
	$(PYTHON) scripts/parse_knowledge.py --input Wissen --output build/export

test: unit

codex:
	codex

codex-fix:
	codex exec --full-auto "fix linting, run tests, and update documentation"

docker-shell:
	docker compose -f docker-compose.codex.yml exec codex-dev bash
