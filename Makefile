.PHONY: codex codex-fix lint test format docker-shell

codex:
	codex

codex-fix:
	codex exec --full-auto "fix linting, run tests, and update documentation"

lint:
	ruff check . || true
	eslint . || true

format:
	ruff check . --fix || true
	black . || true
	prettier -w .

test:
	pytest -q

docker-shell:
	docker compose -f docker-compose.codex.yml exec codex-dev bash
