"""
env_helpers.py – Hilfsfunktionen für sichere und typsichere Umgebungsvariablen

Stellt Funktionen bereit, um Umgebungsvariablen sicher als str, int, float oder bool auszulesen.
Fehler werden klar kommuniziert und Defaultwerte unterstützt.
"""

import os

def get_env_str(var_name: str, required: bool = True, default: str | None = None) -> str | None:
    """
    Liest eine Umgebungsvariable als String aus.

    Args:
        var_name (str): Name der Umgebungsvariable.
        required (bool, optional): Muss die Variable gesetzt sein? (Default: True)
        default (str | None, optional): Fallback, falls nicht gesetzt.

    Returns:
        str | None: Der Wert als String, oder Default/Fallback.

    Raises:
        RuntimeError: Falls Variable benötigt wird, aber fehlt.
    """
    value = os.environ.get(var_name, default)
    if required and (value is None or value == ""):
        raise RuntimeError(f"Die Umgebungsvariable '{var_name}' muss in .env definiert sein!")
    return value

def get_env_int(var_name: str, required: bool = True, default: int | None = None) -> int | None:
    """
    Liest eine Umgebungsvariable als Integer aus.

    Args:
        var_name (str): Name der Umgebungsvariable.
        required (bool, optional): Muss die Variable gesetzt sein? (Default: True)
        default (int | None, optional): Fallback, falls nicht gesetzt.

    Returns:
        int | None: Der Wert als Integer, oder Default/Fallback.

    Raises:
        RuntimeError: Falls Variable benötigt wird, aber fehlt oder kein Integer ist.
    """
    value = os.environ.get(var_name)
    if value is None or value == "":
        if required:
            raise RuntimeError(f"Die Umgebungsvariable '{var_name}' muss in .env definiert sein!")
        return default
    try:
        return int(value)
    except ValueError:
        raise RuntimeError(f"Die Umgebungsvariable '{var_name}' muss eine gültige Ganzzahl sein!")

def get_env_bool(var_name: str, required: bool = True, default: bool | None = None) -> bool | None:
    """
    Liest eine Umgebungsvariable als Boolean aus.

    Akzeptiert: '1', 'true', 'yes', 'on' (Groß-/Kleinschreibung egal).

    Args:
        var_name (str): Name der Umgebungsvariable.
        required (bool, optional): Muss die Variable gesetzt sein? (Default: True)
        default (bool | None, optional): Fallback, falls nicht gesetzt.

    Returns:
        bool | None: Der Wert als Boolean, oder Default/Fallback.

    Raises:
        RuntimeError: Falls Variable benötigt wird, aber fehlt.
    """
    value = os.environ.get(var_name)
    if value is None or value == "":
        if required:
            raise RuntimeError(f"Die Umgebungsvariable '{var_name}' muss in .env definiert sein!")
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}

def get_env_float(var_name: str, required: bool = True, default: float | None = None) -> float | None:
    """
    Liest eine Umgebungsvariable als Float aus.

    Args:
        var_name (str): Name der Umgebungsvariable.
        required (bool, optional): Muss die Variable gesetzt sein? (Default: True)
        default (float | None, optional): Fallback, falls nicht gesetzt.

    Returns:
        float | None: Der Wert als Float, oder Default/Fallback.

    Raises:
        RuntimeError
