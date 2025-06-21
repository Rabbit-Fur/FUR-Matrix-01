.DEFAULT_GOAL := check
.PHONY: lint test check

lint:
	black .
	isort .
	flake8 .

test:
	pytest --disable-warnings

check: lint test
