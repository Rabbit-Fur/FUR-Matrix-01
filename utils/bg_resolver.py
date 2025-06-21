import os

from flask import request


def resolve_background_template() -> str:
    """
    Automatisch den passenden Hintergrund aus /static/bg/ wählen
    basierend auf der aktuellen Route (endpoint-Name).
    """
    endpoint = (request.endpoint or "").split(".")[-1]  # z.B. "dashboard"
    filename = f"{endpoint}.png"
    static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static", "bg"))
    file_path = os.path.join(static_dir, filename)

    if os.path.isfile(file_path):
        return f"/static/bg/{filename}"
    return "/static/img/background.jpg"  # Fallback
