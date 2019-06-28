import os
import sys
import re
import discord

from importlib import import_module
from redis import Redis


class HackWeek(discord.AutoShardedClient):
    """
    Subclass of Discord Client, with a collection of commands
    and a connection to a Redis instance.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.commands = {}

    async def on_ready(self):
        if self.debug:
            print("Debug mode enabled.")
        for file in os.listdir('./bot/commands'):
            if file.endswith('.py') and not file.startswith("__init__"):
                module = import_module(
                    f"bot.commands.{file[:-3]}")
                for key, value in module.commands.items():
                    if type(value) == list:
                        try:
                            self.commands[key].extend(value)
                        except KeyError:
                            self.commands[key] = value
                    elif type(value) == dict:
                        try:
                            self.commands[key] = {
                                **self.commands[key], **value}
                        except KeyError:
                            self.commands[key] = value
        print("Logged in.")

    async def on_message(self, message):
        """
        Called when a new message is sent.

        Example plugin usage.

        commands = {
            "on_message": {
                "<COMMAND_PREFIX>": <TASK>,
            },
        }

        <COMMAND_PREFIX> represents what the users message must begin with in
        order to be recognized as a command.

        <TASK> represents a function that is called when the command is
        recognized. <TASK> must have two positional arguments:

            bot: An instance of the bot class.
            message: The Message object that triggered the command.
        """

        items = self.commands.get("on_message")

        if items and type(items) == dict:
            for prefix, callback in items.items():
                if message.content.startswith(prefix):
                    await callback(self, message)

    async def on_guild_role_delete(self, role):
        """
        Called when a role is deleted from a guild.

        Example plugin usage.

        commands = {
            "on_guild_role_delete": [
                <TASK>,
            ],
        }

        <TASK> represents a function that is called the event is triggered.
        <TASK> must have two positional arguments:

            bot: An instance of the bot class.
            role: The Role object that was deleted.
        """

        callbacks = self.commands.get("on_guild_role_delete")

        if callbacks:
            for callback in callbacks:
                await callback(self, role)

    async def on_member_update(self, before, after):
        """
        Called when any of the following properties of a member are changed.
            - nickname
            - status
            - activity
            - roles

        Example plugin usage.

        commands = {
            "on_member_update": {
                "<PROP>": [
                    <TASK>,
                ],
            }
        }

        <PROP> represents the property that must be changed in order for the
        list of tasks to be run. It must be one of the properties listed above.
        <TASK> represents a function that is called when the specified property
        has been changed. <TASK> must have three positional arguments:

            bot: An instance of the bot class.
            member: The changed member.
            prop: The property before it was changed.
        """

        items = self.commands.get("on_member_update")

        if items and type(items) == dict:
            if before.nick != after.nick:
                callbacks = items.get("nickname")
                if callbacks:
                    for callback in callbacks:
                        callback(self, after, before.nick)
            if before.status != after.status:
                callbacks = items.get("status")
                if callbacks:
                    for callback in callbacks:
                        callback(self, after, before.status)
            if before.activity != after.activity:
                callbacks = items.get("activity")
                if callbacks:
                    for callback in callbacks:
                        callback(self, after, before.activity)
            if before.roles != after.roles:
                callbacks = items.get("roles")
                if callbacks:
                    changed_roles = list(set(before.roles).difference(
                        set(after.roles)))
                    for callback in callbacks:
                        callback(self, after, changed_roles)


def create_bot() -> discord.Client:
    """
    Robot factory. 🤖

    No but seriously, this is a factory to create instances of our bot.
    """

    activity = discord.Game("gk help")
    bot = HackWeek(activity=activity)
    return bot
