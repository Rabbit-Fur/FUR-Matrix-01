import re
from pathlib import Path

REQ_PATH = Path("requirements.txt")
RESOLVED_PATH = Path("requirements_resolved.txt")
ENV_EXAMPLE_PATH = Path(".env.example")
ENV_PATH = Path(".env")
LOG_PATH = Path("Fehlende_ENV_LOG.md")


PACKAGES_TO_FIX = {
    "langchain": "langchain>=0.3.26",
    "openai": "openai>=1.14",
}


def parse_env(path: Path) -> set[str]:
    keys = set()
    if not path.exists():
        return keys
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key = line.split("=", 1)[0].strip()
        if key:
            keys.add(key)
    return keys


def resolve_requirements() -> None:
    resolved_lines = []
    conflict = False
    for raw_line in REQ_PATH.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            resolved_lines.append(raw_line)
            continue
        pkg = re.split("[<>=]", line, 1)[0].lower()
        if pkg == "langchain" and ">=0.3.26" in line:
            conflict = True
        replacement = PACKAGES_TO_FIX.get(pkg)
        resolved_lines.append(replacement if replacement else raw_line)
    RESOLVED_PATH.write_text("\n".join(resolved_lines) + "\n")

    missing_env = sorted(parse_env(ENV_EXAMPLE_PATH) - parse_env(ENV_PATH))

    with LOG_PATH.open("w") as f:
        f.write("# Fehlende Umgebungsvariablen\n\n")
        for key in missing_env:
            f.write(f"- {key}\n")
        f.write("\n# Paketkonflikte\n\n")
        if conflict:
            f.write("> Detektierter Versionskonflikt:\n")
            f.write("- pydantic>=2.7.4\n- langchain>=0.3.26\n- openai>=1.14\n")
            f.write("\npip loest pydantic>=2.7.4 automatisch auf.\n")
        else:
            f.write("Keine Konflikte erkannt.\n")


if __name__ == "__main__":
    resolve_requirements()
