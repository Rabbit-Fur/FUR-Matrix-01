"""AgentCore orchestrates GPT queries and system agents."""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import openai

from mongo_service import db

PROMPT_PATH = (
    Path(__file__).resolve().parent.parent / "templates" / "prompts" / "gpt_agent_core_prompt.md"
)
SYSTEM_PROMPT = PROMPT_PATH.read_text(encoding="utf-8") if PROMPT_PATH.exists() else ""


class AgentCore:
    """High level interface to interact with GPT-4 and helper agents."""

    def __init__(self, api_key: str, webhook_agent: Any | None = None) -> None:
        openai.api_key = api_key
        self.webhook_agent = webhook_agent
        self.logs = db["agent_logs"]

    def run(self, prompt: str, role: str = "User", lang: str = "de") -> Dict[str, Any]:
        """Execute a prompt via GPT-4 and return parsed JSON if possible."""

        system = (
            SYSTEM_PROMPT + f"\n\nRolle: {role}\nSprache: {lang}\nDatum: {datetime.utcnow().date()}"
        )
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ]
        try:
            resp = openai.ChatCompletion.create(model="gpt-4", messages=messages)
            content = resp.choices[0].message.content.strip()
            self.logs.insert_one({"prompt": prompt, "response": content, "ts": datetime.utcnow()})
            if self.webhook_agent:
                self.webhook_agent.send_log_notification(content)
            try:
                import json

                return json.loads(content)
            except Exception:
                return {"response": content}
        except Exception as exc:  # pragma: no cover - network issues
            logging.error("GPT request failed: %s", exc)
            return {"error": str(exc)}
