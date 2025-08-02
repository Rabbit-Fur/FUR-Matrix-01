from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from mongo_service import get_collection  # noqa: E402


def enable_codex_autopilot() -> None:
    """Enable daily log write monitoring in the codex settings."""
    collection = get_collection("codex_settings")
    collection.update_one(
        {"module": "codex_autopilot"},
        {
            "$set": {
                "enabled": True,
                "last_activated": datetime.utcnow().isoformat(),
                "mode": "daily_log_write",
                "target": "write_log_to_mongo",
                "trigger": "daily",
            }
        },
        upsert=True,
    )
    print("✅ Codex Autopilot-Modus aktiviert – tägliche Write Logs werden überwacht.")


if __name__ == "__main__":
    enable_codex_autopilot()
