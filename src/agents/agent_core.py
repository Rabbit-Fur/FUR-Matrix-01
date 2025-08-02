"""AgentCore orchestrates GPT queries and system agents."""

from __future__ import annotations

import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import openai

from ..mongo_service import get_collection
from blueprints.monitoring import GPT_ERROR_COUNT, GPT_RESPONSE_TIME

PROMPT_PATH = (
    Path(__file__).resolve().parent.parent / "templates" / "prompts" / "gpt_agent_core_prompt.md"
)
SYSTEM_PROMPT = PROMPT_PATH.read_text(encoding="utf-8") if PROMPT_PATH.exists() else ""


class AgentCore:
    """High level interface to interact with GPT-4 and helper agents."""

    def __init__(self, api_key: str, webhook_agent: Any | None = None) -> None:
        openai.api_key = api_key
        self.webhook_agent = webhook_agent
        self.logs = get_collection("agent_logs")

    def run(self, prompt: str, role: str = "User", lang: str = "de") -> Dict[str, Any]:
        """Execute a prompt via GPT-4 and return parsed JSON if possible."""

        system = (
            SYSTEM_PROMPT + f"\n\nRolle: {role}\nSprache: {lang}\nDatum: {datetime.utcnow().date()}"
        )
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ]
        start = time.perf_counter()
        try:
            resp = openai.ChatCompletion.create(model="gpt-4", messages=messages)
            duration = time.perf_counter() - start
            GPT_RESPONSE_TIME.observe(duration)
            logging.info("GPT response time: %.3fs", duration)
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
            GPT_ERROR_COUNT.inc()
            logging.error("GPT request failed: %s", exc)
            return {"error": str(exc)}
