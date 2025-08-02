# /app/utils/env_helpers.py

import os


def get_env_str(var_name: str, required: bool = True, default: str | None = None) -> str | None:
    """Liest eine Umgebungsvariable als String aus.

    Wirft `RuntimeError`, wenn der Wert fehlt und `required=True` ist.
    """
    value = os.environ.get(var_name, default)
    if required and not value:
        raise RuntimeError(f"{var_name} muss in .env definiert sein!")
    return value


def get_env_int(var_name: str, required: bool = True, default: int | None = None) -> int | None:
    """Liest eine Umgebungsvariable als Integer aus.

    Gibt `default` zurück oder wirft `RuntimeError` bei ungültiger Ganzzahl.
    """
    value = os.environ.get(var_name)
    if value is None:
        if required:
            raise RuntimeError(f"{var_name} muss in .env definiert sein!")
        return default
    try:
        return int(value)
    except ValueError:
        raise RuntimeError(f"{var_name} muss eine gültige Ganzzahl sein!")


def get_env_bool(var_name: str, required: bool = True, default: bool | None = None) -> bool | None:
    """Liest eine Umgebungsvariable als Boolean aus.

    Akzeptiert "true", "1", "yes" und "on" als wahr.
    """
    value = os.environ.get(var_name)
    if value is None:
        if required:
            raise RuntimeError(f"{var_name} muss in .env definiert sein!")
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def get_env_float(
    var_name: str, required: bool = True, default: float | None = None
) -> float | None:
    """Liest eine Umgebungsvariable als Float aus.

    Gibt `default` zurück oder wirft `RuntimeError` bei ungültiger Zahl.
    """
    value = os.environ.get(var_name)
    if value is None:
        if required:
            raise RuntimeError(f"{var_name} muss in .env definiert sein!")
        return default
    try:
        return float(value)
    except ValueError:
        raise RuntimeError(f"{var_name} muss eine gültige Zahl sein!")
