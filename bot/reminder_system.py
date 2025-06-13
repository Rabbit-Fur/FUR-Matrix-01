import asyncio

from bot.bot_main import bot
from web.database import get_db


async def _send_reminder(reminder_id: int) -> None:
    db = get_db()
    reminder = db.execute(
        "SELECT message FROM reminders WHERE id = ?",
        (reminder_id,),
    ).fetchone()
    if not reminder:
        print(f"[Reminder] Reminder-ID {reminder_id} not found.")
        db.close()
        return

    participants = db.execute(
        "SELECT u.discord_id FROM reminder_participants rp "
        "JOIN users u ON u.id = rp.user_id WHERE rp.reminder_id = ?",
        (reminder_id,),
    ).fetchall()
    db.close()

    for row in participants:
        try:
            user = await bot.fetch_user(int(row["discord_id"]))
            if user:
                await user.send(reminder["message"])
                print(f"[Reminder] Sent to {user}.")
        except Exception as exc:
            print(f"[Reminder] Failed to send to {row['discord_id']}: {exc}")


def send_reminder_by_id(reminder_id: int) -> None:
    loop = asyncio.get_event_loop()
    if loop.is_running():
        asyncio.ensure_future(_send_reminder(reminder_id))
    else:
        loop.run_until_complete(_send_reminder(reminder_id))
