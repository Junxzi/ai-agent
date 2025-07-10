# ai-agent
A **personal AI‑powered Discord bot** that lives in Jun’s DM and acts as a full‑time assistant.  
Powered by OpenAI ChatGPT (GPT‑4 or GPT‑3.5), it can:

- 💬 **Answer questions** in natural language  
- 📝 **Manage To‑Dos** (add, list, complete, delete)  
- ⏰ **Set reminders** (DM notification at a given time)  
- 📅 **Handle a personal schedule** (add events, list them, fire start‑time alerts)

Everything is designed to run 24 / 7 on a self‑hosted Linux box.  
The repo ships **source, configs and a ready‑to‑use `systemd` service file**.

---

## Features

| Area | What you get |
|------|--------------|
| ChatGPT integration | OpenAI ChatCompletion API with Function Calling |
| Modular codebase | `todo_service`, `reminder_service`, `schedule_service`, etc. |
| Durable storage | Lightweight SQLite (`jun_assistant.db`) |
| Structured logging | Python `logging` to file **and** console |
| Auto‑restart | Supplied `systemd` unit keeps the bot alive |

---

## Directory Layout

```text
jun-discord-ai-agent/
├─ bot/                 # Python packages
│   ├─ discord_client.py
│   ├─ llm_client.py
│   ├─ todo_service.py
│   ├─ reminder_service.py
│   ├─ schedule_service.py
│   └─ data_store.py
├─ main.py              # Entry point
├─ config.yaml          # Non‑secret settings
├─ .env.example         # Template for secrets
├─ requirements.txt
├─ systemd/
│   └─ junbot.service
└─ README.md

```
---

## Quick Start

1. Install dependencies

```code
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Add secrets

Copy .env.example → .env and fill in your keys.

```
DISCORD_TOKEN=xxxxxxxxxxxxxxxx
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx
```
3. Tune config.yaml

```
openai:
  model: gpt-4o-mini    # use gpt-3.5-turbo if you wish
reminder:
  check_interval: 60    # seconds
timezone: "Asia/Tokyo"
```

4. Run the bot

```
python main.py
```

Send the bot a DM on Discord and verify it responds.

5. Keep it running with systemd (Ubuntu example)


```
sudo cp systemd/junbot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now junbot
```

⸻

## Usage Examples

Example DM	What the bot does
“Remind me tomorrow at 9 am to submit the report.”	Stores a reminder → DM at 09:00 tomorrow
“Add ‘buy milk’ to my To‑Do.”	Inserts a new To‑Do item
“Show my To‑Do list.”	Replies with all pending tasks
“Schedule a team meeting next Monday at 15:00.”	Inserts an event & notifies at start


⸻

## Configuration Cheat‑Sheet

File	Purpose
.env	Secrets: Discord token, OpenAI key, etc.
config.yaml	Model name, timezone, tweakable parameters
requirements.txt	Python package list
systemd/*.service	Auto‑start service definition


⸻

## Roadmap
•	Swap custom loop for APScheduler for sub‑second accuracy
•	Plug in a vector DB (Chroma) for long‑term memory
•	Add a lightweight Web dashboard
•	Optional multi‑user mode (if ever needed)

⸻

## License

MIT License – © 2025 Jun
Use at your own risk. Enjoy hacking!

## How to use

1. Create the repository **`jun-discord-ai-agent`** on GitHub or your favourite host.  
2. Copy the README above into `README.md`.  
3. Rename `.env.example` → `.env`, paste your Discord token & OpenAI key.  
4. Follow **Quick Start** to test locally, then enable the `systemd` service for 24 / 7 operation.
