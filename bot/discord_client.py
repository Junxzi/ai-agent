from __future__ import annotations

import asyncio
import datetime
import logging
import re
from zoneinfo import ZoneInfo
from typing import Any, Dict, List, Tuple

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
        self.tz = ZoneInfo(config.get("timezone", "UTC"))
        self.bg_task = self.loop.create_task(self._reminder_loop())
        # Patterns to detect natural language "add to todo" commands
        self.todo_add_patterns: List[re.Pattern[str]] = [
            re.compile(r"add (.+?) to(?: my)? todo", re.IGNORECASE),
            re.compile(r"(.+?)を?ToDoに追加"),
            re.compile(r"ToDoに(.+?)を追加"),
        ]
        # Patterns for natural language "show todo list" requests
        self.todo_list_patterns: List[re.Pattern[str]] = [
            re.compile(r"show (?:my )?(?:todo|task) list", re.IGNORECASE),
            re.compile(r"ToDoリスト.*(見せて|表示)"),
            re.compile(r"ToDo一覧"),
        ]
        # Simple patterns for reminder requests (e.g. "明日9時に○○をリマインド")
        self.reminder_add_patterns: List[re.Pattern[str]] = [
            re.compile(r"明日(\d{1,2})時(?:([0-9]{1,2})分?)?に(.+?)を?リマインド"),
            re.compile(
                r"remind me (?:(tomorrow) )?at (\d{1,2})(?::(\d{2}))?\s*(am|pm)? to (.+)",
                re.IGNORECASE,
            ),
        ]

    def _parse_todo_add(self, text: str) -> str | None:
        for pat in self.todo_add_patterns:
            m = pat.search(text)
            if m:
                return m.group(1).strip()
        return None

    def _is_todo_list_request(self, text: str) -> bool:
        return any(p.search(text) for p in self.todo_list_patterns)

    def _parse_reminder_add(self, text: str) -> Tuple[str, str] | None:
        now = datetime.datetime.now(self.tz)
        for pat in self.reminder_add_patterns:
            m = pat.search(text)
            if not m:
                continue
            if pat.pattern.startswith("明日"):
                hour = int(m.group(1))
                minute = int(m.group(2) or 0)
                message = m.group(3).strip()
                remind_date = now.date() + datetime.timedelta(days=1)
            else:
                tomorrow = m.group(1)
                hour = int(m.group(2))
                minute = int(m.group(3) or 0)
                ampm = m.group(4)
                if ampm:
                    if ampm.lower() == "pm" and hour < 12:
                        hour += 12
                    if ampm.lower() == "am" and hour == 12:
                        hour = 0
                message = m.group(5).strip()
                remind_date = now.date() + datetime.timedelta(days=1) if tomorrow else now.date()
            remind_at = datetime.datetime.combine(
                remind_date,
                datetime.time(hour, minute, tzinfo=self.tz),
            )
            return message, remind_at.isoformat()
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
            if self._is_todo_list_request(message.content):
                await self._send_todo_list(message.channel)
                return
            todo_desc = self._parse_todo_add(message.content)
            if todo_desc:
                task_id = self.todos.add_task(todo_desc)
                await message.channel.send(f"Added task #{task_id}")
                return
            reminder = self._parse_reminder_add(message.content)
            if reminder:
                msg_text, remind_at = reminder
                rid = self.reminders.add_reminder(msg_text, remind_at)
                await message.channel.send(
                    f"Reminder #{rid} set for {remind_at}"
                )
                return
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

    async def _send_todo_list(self, channel: discord.abc.Messageable):
        tasks = self.todos.list_pending_tasks()
        if not tasks:
            await channel.send("(no pending tasks)")
            return
        lines = []
        for tid, desc, due in tasks:
            due_str = f" (due {due})" if due else ""
            lines.append(f"{tid}: {desc}{due_str}")
        await channel.send("\n".join(lines))

    async def _reminder_loop(self):
        await self.wait_until_ready()
        interval = int(self.config["reminder"]["check_interval"])
        while not self.is_closed():
            now = datetime.datetime.now(self.tz).replace(microsecond=0)
            due = self.reminders.due_reminders(now)
            for rid, msg in due:
                user = await self.fetch_user(self.allowed_user_id)
                await user.send(msg)
                self.reminders.mark_sent(rid)
            await asyncio.sleep(interval)
