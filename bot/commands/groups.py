import re

from bot.db import create_group
from bot.utils import request_answer
from bot.utils import Permission


async def create_group_for(bot, message):
    """
    Create a permissions group for one or more roles.
    """

    permissions = []

    match = re.search(r"named (\S+)", message.content)
    if not match:
        await message.channel.send(
            "Please provide a name.\n\n`gk create group for <role> named <name>`")
        return

    name = match.group(1)
    name = re.sub(r"\ ", "-", re.sub(r"[^a-zA-Z0-9_\ ]", "", name))

    await request_answer(
        bot,
        message.author,
        f"When creating the group named `{name}`\nWhat permissions would you like me to give?",
        {
            "📻": (
                "Create and delete channels",
                lambda: permissions.append(Permission.CREATE_AND_DELETE)),
            "📝": (
                "Modify existing channels",
                lambda: permissions.append(Permission.MODIFY_CHANNELS)),
            "🖌": (
                "Modify properties of the role",
                lambda: permissions.append(Permission.MODIFY_ROLES)),
            "📯": (
                "Invite new members",
                lambda: permissions.append(Permission.INVITE_USERS)),
            "👞": (
                "Remove users",
                lambda: permissions.append(Permission.REMOVE_USERS)), },
        destination=message.channel)

    for role in message.role_mentions:
        create_group(bot.db, role, name, permissions)

    await message.channel.send("Created groups! 🎉")


commands = {
    "gk create group for": create_group_for,
}
