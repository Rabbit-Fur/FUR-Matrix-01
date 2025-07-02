# Access Agent

## Purpose
Manages role-based access control using Discord roles stored in environment variables.

## Environment Variables
- `ADMIN_ROLE_IDS` – comma-separated Discord role IDs for admins
- `R4_ROLE_IDS` – comma-separated role IDs for high-level members
- `R3_ROLE_IDS` – comma-separated role IDs for mid-level members

## External Dependencies
- MongoDB collection `access_logs`
