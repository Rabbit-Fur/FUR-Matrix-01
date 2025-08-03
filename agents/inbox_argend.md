# Inbox Agent

## Purpose
Stores incoming system messages such as Discord DMs or webhook notifications and routes them for further processing.

## Environment Variables
*(none)*

## External Dependencies
- MongoDB collection `inbox`

## Registration
Add `InboxAgent(db)` to `agenten_loader.init_agents()` so the agent is available under the key `"inbox"`.
