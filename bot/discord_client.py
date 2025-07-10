from __future__ import annotations

import asyncio
import datetime
import logging
import re
from typing import Any, Dict, List
from zoneinfo import ZoneInfo

import discord

from .llm_client import LLMClient
from openai_client import ask_chatgpt
from .todo_service import TodoService
from .reminder_service import ReminderService
from .schedule_service import ScheduleService


class JunBot(discord.Client):
    def __init__(self, config: Dict[str, Any], store, **kwargs):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents, **kwargs)
        self.config = config
        self.allowed_user_id = int(config["discord"]["allowed_user_id"])
        self.llm = LLMClient(config)
        self.todos = TodoService(store)
        self.reminders = ReminderService(store)
        self.schedule = ScheduleService(store)
        self.bg_task = self.loop.create_task(self._reminder_loop())
        # Patterns to detect natural language "add to todo" commands
        self.todo_add_patterns: List[re.Pattern[str]] = [
            re.compile(r"add (.+?) to(?: my)? todo", re.IGNORECASE),
            re.compile(r"(.+?)を?ToDoに追加"),
            re.compile(r"ToDoに(.+?)を追加"),
        ]
        # Pattern to detect simple schedule entry like "10/5 15:00に会議"
        self.event_add_pattern = re.compile(
            r"(?P<month>\d{1,2})/(?P<day>\d{1,2})\s+"
            r"(?P<hour>\d{1,2}):(?P<minute>\d{2})(?:に)?\s*(?P<title>.+)"
        )

    def _parse_todo_add(self, text: str) -> str | None:
        for pat in self.todo_add_patterns:
            m = pat.search(text)
            if m:
                return m.group(1).strip()
        return None

    def _parse_event_add(self, text: str) -> tuple[str, str] | None:
        m = self.event_add_pattern.search(text)
        if not m:
            return None
        try:
            month = int(m.group("month"))
            day = int(m.group("day"))
            hour = int(m.group("hour"))
            minute = int(m.group("minute"))
            title = m.group("title").strip()
            year = datetime.datetime.now().year
            tzname = self.config.get("timezone", "UTC")
            tz = ZoneInfo(tzname)
            dt = datetime.datetime(year, month, day, hour, minute, tzinfo=tz)
            return title, dt.isoformat()
        except Exception:
            return None

    async def on_ready(self):
        logging.getLogger(__name__).info("Logged in as %s", self.user)

    async def on_message(self, message: discord.Message):
        # Only handle direct messages from the allowed user
        if message.author.id != self.allowed_user_id:
            return
        if message.author == self.user:
            return
        # Ignore messages that are not DMs (e.g. guild channels)
        if message.guild is not None:
            return

        if message.content.startswith("/todo"):
            await self.handle_todo_command(message)
        else:
            todo_desc = self._parse_todo_add(message.content)
            if todo_desc:
                task_id = self.todos.add_task(todo_desc)
                await message.channel.send(f"Added task #{task_id}")
                return
            event = self._parse_event_add(message.content)
            if event:
                title, start_time = event
                event_id = self.schedule.add_event(title, start_time)
                await message.channel.send(
                    f"Added event #{event_id}: {title} at {start_time}"
                )
            else:
                await self.handle_chat(message)

    async def handle_chat(self, message: discord.Message):
        """Generate a reply using ChatGPT and send it back to the user."""
        answer = ask_chatgpt(message.content)
        await message.channel.send(answer)

    async def handle_todo_command(self, message: discord.Message):
        parts = message.content.split(maxsplit=2)
        if len(parts) < 2:
            await message.channel.send("Usage: /todo <add|list|complete|delete>")
            return
        cmd = parts[1]
        if cmd == "add" and len(parts) == 3:
            task_id = self.todos.add_task(parts[2])
            await message.channel.send(f"Added task #{task_id}")
        elif cmd == "list":
            tasks = self.todos.list_tasks()
            lines = [f"{t[0]}: {t[1]}{' ✅' if t[3] else ''}" for t in tasks]
            await message.channel.send("\n".join(lines) or "(no tasks)")
        elif cmd == "complete" and len(parts) == 3:
            self.todos.complete_task(int(parts[2]))
            await message.channel.send("Completed")
        elif cmd == "delete" and len(parts) == 3:
            self.todos.delete_task(int(parts[2]))
            await message.channel.send("Deleted")
        else:
            await message.channel.send("Invalid /todo command")

    async def _reminder_loop(self):
        await self.wait_until_ready()
        interval = int(self.config["reminder"]["check_interval"])
        while not self.is_closed():
            now = datetime.datetime.now().replace(microsecond=0).isoformat()
            due = self.reminders.due_reminders(datetime.datetime.now())
            for rid, msg in due:
                user = await self.fetch_user(self.allowed_user_id)
                await user.send(msg)
                self.reminders.mark_sent(rid)
            await asyncio.sleep(interval)
