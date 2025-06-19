# web/admin/memory_routes.py

from flask import Blueprint, render_template, current_app, abort
from bson import ObjectId

admin_memory = Blueprint('admin_memory', __name__, url_prefix='/admin/memory')

@admin_memory.route('/')
def index():
    collection = current_app.mongo.db.memory_contexts
    entries = list(collection.find().sort("exported_at", -1))
    return render_template('admin/memory/index.html', memory_entries=entries)

@admin_memory.route('/<entry_id>')
def view_entry(entry_id):
    collection = current_app.mongo.db.memory_contexts
    entry = collection.find_one({"_id": ObjectId(entry_id)})
    if not entry:
        abort(404)
    return render_template('admin/memory/detail.html', entry=entry)
