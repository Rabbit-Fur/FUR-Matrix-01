# gpt_test_context.py
"""
Testet den Core-Memory-Kontext für GPT-Aufgaben auf Basis definierter Tags.
Wird verwendet, um dynamisch kontextbasierte Prompts zu generieren.
"""

from core.memory.memory_loader import load_gpt_contexts


def test_gpt_memory():
    tags = ["reminder", "champion", "i18n"]
    context = load_gpt_contexts(tags=tags)

    prompt = f"""You are the FUR GPT System.
Use the following Core-Memory:

{context}

User: Wie funktioniert das Reminder-System?
GPT:"""

    print(prompt.strip())


if __name__ == "__main__":
    test_gpt_memory()
