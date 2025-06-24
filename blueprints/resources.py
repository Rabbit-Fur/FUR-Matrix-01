from __future__ import annotations

import os

from flask import Blueprint, abort, current_app, render_template, send_from_directory

from web.auth.decorators import login_required

resources = Blueprint("resources", __name__)

# Example resource files with translation keys for their descriptions
RESOURCE_FILES = [
    {"filename": "example.txt", "desc_key": "example_desc"},
]


@resources.route("/resources")
@login_required
def list_resources():
    folder = current_app.config.get("RESOURCES_FOLDER")
    os.makedirs(folder, exist_ok=True)
    files = []
    for res in RESOURCE_FILES:
        if os.path.exists(os.path.join(folder, res["filename"])):
            files.append(res)
    return render_template("resources/index.html", resources=files)


@resources.route("/resources/download/<path:filename>")
@login_required
def download_resource(filename: str):
    folder = current_app.config.get("RESOURCES_FOLDER")
    allowed = {r["filename"] for r in RESOURCE_FILES}
    safe_name = os.path.basename(filename)
    if safe_name not in allowed:
        abort(404)
    return send_from_directory(folder, safe_name, as_attachment=True)
