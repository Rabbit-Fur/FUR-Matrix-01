# 🧠 CODEX PLAN – Repository: Rabbit-Fur/try

Dieser Plan enthält alle aktuellen Codex-kompatiblen Aufgaben, die für GitHub Copilot, Copilot Chat und ChatGPT Codex verwendet werden können.

---

## 🔧 Reminder API Verbesserungen
**Datei:** `web/routes/reminder_api.py`

- [ ] Wrap all messages with `t()`
- [ ] Add try/except error handling
- [ ] Add logging for reminder sends

---

## 🏆 Leaderboard Cog Refactoring
**Datei:** `bot/cogs/leaderboard_cog.py`

- [ ] Replace static strings with `t()`
- [ ] Return translated error messages
- [ ] Separate DB logic from command handlers

---

## 🛡️ Admin Dashboard Validierung
**Dateien:** `templates/admin/dashboard.html`, `templates/admin/admin_base.html`

- [ ] Fix infinite template recursion
- [ ] Check `bg_image` logic with fallback
- [ ] Ensure titles and headings use `t()`

---

## 🌐 Übersetzungen prüfen
**Dateien:** `translations/*.json`

- [ ] Find missing keys in all languages
- [ ] (Optional) Auto-fill from English as fallback

---

## 🎨 CSS & Style Cleanup
**Datei:** `static/css/style.css`

- [ ] Unify all button styles
- [ ] Optimize media queries
- [ ] Create reusable FUR Hero layout

---

🔁 Bereit für PR-Erstellung, Review mit GPT oder Integration in Copilot Chat.
