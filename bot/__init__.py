import discord
import os

from importlib import import_module
from redis import Redis


class HackWeek(discord.Client):
    """
    Subclass of Discord Client, with a collection of commands
    and a connection to a Redis instance.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.commands = {}
        self.db = Redis(
            host=os.environ.get("REDIS_HOST", "localhost"),
            port=os.environ.get("REDIS_PORT", 6379),
            db=os.environ.get("REDIS_DB", 0),
            password=os.environ.get("REDIS_PASSWORD", None))

    async def on_ready(self):
        for file in os.listdir('./bot/commands'):
            if file.endswith('.py') and not file.startswith("__init__"):
                module = import_module(
                    f"bot.commands.{file[:-3]}")
                self.commands = {**self.commands, **module.commands}

    async def on_message(self, message):
        for prefix, callback in self.commands.items():
            if message.content.startswith(prefix):
                await callback(self, message)


def create_bot() -> discord.Client:
    """
    Robot factory. 🤖

    No but seriously, this is a factory to create instances of our bot.
    """

    bot = HackWeek()
    return bot
