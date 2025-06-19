# core/memory/memory_loader.py

from typing import List, Optional

from mongo_service import db

memory_collection = db["memory_contexts"]


def load_gpt_contexts(tags: Optional[List[str]] = None) -> str:
    """
    Lädt Memory-Kontexte aus MongoDB und formatiert sie als GPT-Systemprompt.
    Nur Kontexte mit passenden Tags werden berücksichtigt (wenn angegeben).
    """
    query = {"tags": {"$in": tags}} if tags else {}
    entries = memory_collection.find(query).sort("updated_at", -1)

    context_blocks = []

    for entry in entries:
        _id = entry.get("_id", "Unbekannt")
        description = entry.get("description", "Keine Beschreibung verfügbar.")
        tags_list = entry.get("tags", [])
        code_refs = entry.get("code_refs", [])

        block = f"### {_id}\n{description}"
        if code_refs:
            block += f"\n📁 Code: {', '.join(code_refs)}"
        if tags_list:
            block += f"\n🏷️ Tags: {', '.join(tags_list)}"

        context_blocks.append(block.strip())

    return "\n\n".join(context_blocks)
