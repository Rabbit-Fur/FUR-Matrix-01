"""Handle sending reminders and user opt-outs via MongoDB."""


class ReminderAgent:
    def __init__(self, db):
        self.db = db

    def send_reminders(self):
        # Reminder-Versand-Logik hier einbinden (z. B. aus reminder_cog)
        pass

    def opt_out_user(self, discord_id):
        # Reminder-Opt-Out-Logik einfügen
        pass
