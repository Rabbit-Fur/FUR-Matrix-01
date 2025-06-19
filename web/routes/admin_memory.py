from datetime import datetime

from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for

from core.memory.memory_loader import load_gpt_contexts
from database.mongo_client import db

admin_memory = Blueprint("admin_memory", __name__)


@admin_memory.route("/admin/memory")
def show_memory():
    memory = db["memory_contexts"].find()
    return render_template("admin/memory.html", memory=memory)


@admin_memory.route("/admin/memory/<string:memory_id>/edit", methods=["GET", "POST"])
def edit_memory(memory_id):
    memory = db["memory_contexts"].find_one({"_id": memory_id})
    if not memory:
        flash("❌ Memory-Kontext nicht gefunden.", "error")
        return redirect(url_for("admin_memory.show_memory"))

    if request.method == "POST":
        description = request.form.get("description", "").strip()
        tags_raw = request.form.get("tags", "").strip()

        if not description or not tags_raw:
            flash("⚠️ Beschreibung und Tags dürfen nicht leer sein.", "error")
            return render_template("admin/memory_edit.html", memory=memory)

        memory["description"] = description
        memory["tags"] = [tag.strip() for tag in tags_raw.split(",") if tag.strip()]
        memory["updated_at"] = datetime.utcnow()

        db["memory_contexts"].replace_one({"_id": memory_id}, memory)
        flash("✅ Kontext erfolgreich aktualisiert.", "success")
        return redirect(url_for("admin_memory.show_memory"))

    return render_template("admin/memory_edit.html", memory=memory)


@admin_memory.route("/admin/memory/gpt_test")
def gpt_test():
    tags = request.args.get("tags", "reminder,champion").split(",")
    context = load_gpt_contexts(tags=tags)
    return render_template("admin/memory_gpt_test.html", context=context, tags=tags)


@admin_memory.route("/admin/memory/export.json")
def export_memory():
    tags = request.args.get("tags", "reminder").split(",")
    memory = list(db["memory_contexts"].find({"tags": {"$in": tags}}))
    for m in memory:
        m["_id"] = str(m["_id"])
    return jsonify(memory=memory)
