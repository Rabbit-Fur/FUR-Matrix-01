import re
import subprocess
from pathlib import Path
from typing import List, Set

PROJECT_DIR: Path = Path(__file__).resolve().parent
IGNORED_DIRS: Set[str] = {"venv", ".venv", "__pycache__", "migrations"}

def fix_file(filepath: Path) -> None:
    """
    Wendet Basis-Fixes für Leerzeilen und Kommentare an einer Python-Datei an.

    Args:
        filepath (Path): Pfad zur Python-Datei.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except OSError as e:
        print(f"❌ Fehler beim Lesen von {filepath}: {e}")
        return

    new_lines: List[str] = []
    for i, line in enumerate(lines):
        # E302/E305: Leerzeile vor Funktionen/Klassen, außer am Anfang
        if re.match(r"^(def |class )", line) and (i == 0 or lines[i - 1].strip() != ""):
            new_lines.append("\n")

        # E261: 2 Leerzeichen vor Inline-Kommentar
        line = re.sub(r"([^#])#(?! )", r"\1# ", line)

        # E265: Kommentar sollte mit "# " beginnen
        if re.match(r"^\s*#\S", line):
            line = re.sub(r"^\s*#(\S)", r"# \1", line)

        new_lines.append(line)

    if new_lines and not new_lines[-1].endswith("\n"):
        new_lines[-1] += "\n"  # W292: newline am Ende

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        print(f"✅ Formatiert: {filepath}")
    except OSError as e:
        print(f"❌ Fehler beim Schreiben in {filepath}: {e}")

def run_flake8_and_fix() -> None:
    """
    Sucht alle Python-Dateien im Projekt und wendet Basis-Fixes an,
    danach werden black und isort ausgeführt.
    """
    py_files = [
        file
        for file in PROJECT_DIR.rglob("*.py")
        if not any(part in IGNORED_DIRS for part in file.parts)
    ]

    print(f"🔧 Fixe {len(py_files)} Python-Dateien...")

    for file in py_files:
        fix_file(file)

    print("✅ Basis-Fixes abgeschlossen. Führe black & isort aus...")

    try:
        subprocess.run(["black", "."], cwd=PROJECT_DIR, check=True)
        subprocess.run(["isort", "."], cwd=PROJECT_DIR, check=True)
    except FileNotFoundError as e:
        print(f"❌ Werkzeug nicht gefunden: {e}")

def fix_unused_imports() -> None:
    """
    Entfernt ungenutzte Importe & Variablen mit autoflake.
    """
    print("🧹 Entferne ungenutzte Importe mit autoflake...")
    try:
        subprocess.run(
            [
                "autoflake",
                "--in-place",
                "--remove-all-unused-imports",
                "--remove-unused-variables",
                "-r",
                ".",
            ],
            cwd=PROJECT_DIR,
            check=True,
        )
    except FileNotFoundError:
        print(
            "❌ 'autoflake' ist nicht installiert. Bitte via pip installieren: pip install autoflake"
        )

if __name__ == "__main__":
    try:
        run_flake8_and_fix()
        fix_unused_imports()
        print("🎉 Code-Cleanup abgeschlossen.")
    except Exception as e:
        print(f"❌ Fehler beim automatischen Fix: {e}")