# web/admin/memory_routes.py

"""Admin blueprint for inspecting stored GPT memory dumps."""

import bleach
from bson import ObjectId
from flask import Blueprint, abort, render_template
from markdown import markdown
from markupsafe import Markup

from mongo_service import get_collection
from web.auth.decorators import admin_required

admin_memory = Blueprint("admin_memory", __name__, url_prefix="/admin/memory")


@admin_memory.route("/")
@admin_required
def index():
    collection = get_collection("memory_contexts")
    collection.create_index("exported_at")
    entries = list(collection.find().sort("exported_at", -1))
    return render_template("admin/memory/index.html", memory_entries=entries)


@admin_memory.route("/<entry_id>")
@admin_required
def view_entry(entry_id: str):
    collection = get_collection("memory_contexts")
    entry = collection.find_one({"_id": ObjectId(entry_id)})
    if not entry:
        abort(404)

    content_md = entry.get("content_md")
    content_html = None
    if content_md:
        content_html = Markup(bleach.clean(markdown(content_md)))

    return render_template("admin/memory/detail.html", entry=entry, content_html=content_html)
