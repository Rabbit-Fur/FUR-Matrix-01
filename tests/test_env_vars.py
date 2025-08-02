"""Ensure required environment variables are documented."""

from pathlib import Path


def test_env_vars_documented():
    root = Path(__file__).resolve().parents[1]
    log_lines = (root / "Fehlende_ENV_LOG.md").read_text().splitlines()
    variables = []
    for line in log_lines:
        if line.startswith("# Paketkonflikte"):
            break
        if line.startswith("- "):
            variables.append(line[2:].strip())

    env_text = (root / ".env.example").read_text()
    docs_text = (root / "docs/env_vars.md").read_text()

    missing_env = [v for v in variables if v not in env_text]
    missing_docs = [v for v in variables if v not in docs_text]

    assert not missing_env, f"Missing in .env.example: {missing_env}"
    assert not missing_docs, f"Missing in docs/env_vars.md: {missing_docs}"
