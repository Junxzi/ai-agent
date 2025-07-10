from __future__ import annotations

import asyncio
import datetime
import logging
from typing import Any, Dict

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
