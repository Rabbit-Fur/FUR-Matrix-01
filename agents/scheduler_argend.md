# Scheduler Agent

## Purpose
Manages scheduled tasks like champion autopilot and Google Calendar sync.

## Environment Variables
- `GOOGLE_SYNC_INTERVAL_MINUTES` – interval for calendar sync (optional)

## External Dependencies
- `schedule` library
- Google Calendar API
- MongoDB collections used by tasks
