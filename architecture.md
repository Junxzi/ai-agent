# Architecture Overview

This document outlines the system architecture and module structure of Jun's personal AI assistant Discord bot. The design is based on the requirements described in **基本仕様.md**.

## High-Level Architecture

The bot runs on a self-hosted server and communicates with Discord via the Discord API. Incoming direct messages from the user are processed with OpenAI's ChatGPT API, and the bot also persists data in a local SQLite database. Responses and notifications are sent back over Discord.

```
Discord DM <=> Bot server (Python) <=> OpenAI API / SQLite
```

The main components and their interactions are:

- **Discord front end** – Receives messages from Jun and displays bot replies.
- **Python bot application** – Handles events, calls the LLM and local services.
- **OpenAI API** – Provides natural language understanding and function calling.
- **SQLite database** – Stores ToDo tasks, reminders and schedule events locally.

The communication flow is asynchronous: Discord forwards a DM to the bot, the bot queries ChatGPT if needed, updates or reads from the database, and finally returns the generated response to the user.

## Directory Layout

The specification proposes a modular directory structure:

```
jun_personal_ai_bot/
├── config.yaml              # Static settings
├── .env                     # Secret environment variables
├── main.py                  # Entry point
├── bot/
│   ├── discord_client.py    # Discord event handling
│   ├── llm_client.py        # OpenAI API interface
│   ├── todo_service.py      # ToDo management
│   ├── reminder_service.py  # Reminder logic
│   ├── schedule_service.py  # Schedule management
│   └── data_store.py        # SQLite access
└── systemd/junbot.service   # Optional service unit
```

Main script `main.py` loads configuration and environment variables, then starts the Discord client. Each feature is separated into a module under `bot/` for maintainability.

## Core Modules

### discord_client.py
Handles connection to Discord and acts as the controller. It receives DM events, forwards the content to `llm_client`, and sends responses back to the user.

### llm_client.py
Wraps the OpenAI ChatCompletion API. It builds prompts, defines available functions, and parses responses. When ChatGPT triggers a function call, this module invokes the corresponding service (e.g., ToDo or reminder) and returns results.

### todo_service.py
Implements business logic for managing ToDo items: add, list, complete and delete tasks. It accesses the `tasks` table via `data_store.py` and returns data to `llm_client` or Discord commands.

### reminder_service.py
Provides reminder registration, listing and cancellation, plus a scheduler that periodically checks for due reminders and sends DM notifications. It updates the `reminders` table in the database.

### schedule_service.py
Stores and retrieves personal events. It allows creating new events and listing them within a specified time range. Future extensions can integrate external calendars.

### data_store.py
Centralizes SQLite operations such as creating tables and executing queries. All services use this module to ensure database access is separated from business logic.

## Configuration and Secrets

- **.env** – Holds sensitive values like `DISCORD_TOKEN` and `OPENAI_API_KEY`. It is loaded via `python-dotenv` and kept out of version control.
- **config.yaml** – Contains non‑secret settings such as model name, Discord user ID, reminder intervals and timezone. It is read at startup with `PyYAML`.

This separation allows changing behavior or rotating keys without modifying the code.

## Deployment

A sample `systemd` service file is provided so the bot can run continuously on a server. The service starts `main.py`, restarts automatically on failure and loads environment variables if needed.

## Summary

The bot is composed of a Discord-facing client, an LLM interface and a set of service modules for ToDo, reminders and schedule management. Data persistence is handled through a single SQLite database accessed via `data_store.py`. Configuration and secrets are externalized in `config.yaml` and `.env`. This modular architecture keeps responsibilities clear and makes future extensions—such as additional services or improved scheduling—straightforward.

## Conversation Flow and Command Routing

User messages arrive as plain text via Discord. They are first inspected for a
leading slash command such as `/todo list`. If present, the bot directly calls
the corresponding service without involving the LLM.

For normal sentences, the text is sent to ChatGPT along with a list of
available functions. The model either returns an answer (for general Q&A) or
invokes one of the functions below:

1. **ToDo operations** – phrases containing verbs like "add", "complete" or
   "delete" together with "todo"/"task" route to `todo_service`.
2. **Reminders** – expressions such as "remind me" or "set a reminder" cause a
   call to `reminder_service` after ChatGPT extracts the time and message.
3. **Schedule management** – mentions of "schedule", "meeting" or "appointment"
   use `schedule_service` to store or list events.

If ChatGPT returns plain text with no function call, the bot replies directly
with that answer. This hybrid strategy allows free‑form conversation while
still supporting explicit commands when needed.

