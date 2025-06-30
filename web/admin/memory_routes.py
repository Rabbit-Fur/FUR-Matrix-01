# web/admin/memory_routes.py

"""Admin blueprint for inspecting stored GPT memory dumps."""

import bleach
from bson import ObjectId
from flask import Blueprint, abort, flash, redirect, render_template, session, url_for
from markdown import markdown
from markupsafe import Markup

from mongo_service import get_collection
from web.auth.decorators import admin_required


def get_memory_entries() -> list[dict]:
    """Collect memory entries from various sources."""
    entries: list[dict] = []

    # MongoDB stored contexts
    collection = get_collection("memory_contexts")
    try:
        for doc in collection.find().sort("exported_at", -1):
            entries.append(
                {
                    "key": str(doc.get("_id")),
                    "value": doc.get("content") or doc.get("description"),
                    "created_at": doc.get("exported_at") or doc.get("created_at"),
                    "source": "mongo",
                }
            )
    except Exception:
        pass

    # Example: in-memory session values (for current admin only)
    for k, v in session.items():
        if k == "_flashes":
            continue
        entries.append(
            {
                "key": k,
                "value": v,
                "created_at": None,
                "source": "session",
            }
        )

    return entries


admin_memory = Blueprint("admin_memory", __name__, url_prefix="/admin/memory")


@admin_memory.route("/")
@admin_required
def index():
    entries = get_memory_entries()
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


@admin_memory.route("/clear", methods=["POST"])
@admin_required
def clear_memory():
    """Delete all stored memory contexts."""
    collection = get_collection("memory_contexts")
    collection.delete_many({})
    flash("Cache wurde geleert.", "success")
    return redirect(url_for("admin_memory.index"))
