# codex/context_manager.py

from core.memory.memory_loader import load_gpt_contexts
import logging
from typing import List

log = logging.getLogger(__name__)

def build_codex_prompt(task_tags: List[str]) -> str:
    """
    Baut einen Codex-kompatiblen Prompt auf Basis gespeicherter GPT-Kontexte.

    Args:
        task_tags (List[str]): Eine Liste von Tags zur Filterung des Kontextes.

    Returns:
        str: Finaler Prompt-Text im FUR-Format.
    """
    try:
        context = load_gpt_contexts(tags=task_tags)
        if not context.strip():
            log.warning(f"[CodexContext] ⚠️ Kein Kontext für Tags: {task_tags}")
            context = "– Kein Kontext gefunden –"
        return f"### FUR CONTEXT:\n{context}\n\n### TASK:\n"
    except Exception as e:
        log.error(f"[CodexContext] ❌ Fehler beim Laden des Kontextes: {e}")
        return "### FUR CONTEXT:\n– Fehler beim Laden des Kontexts –\n\n### TASK:\n"
