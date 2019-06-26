import re

from bot.db import create_permset
from bot.utils import request_answer
from bot.utils import Permission


async def create_permset_for(bot, message):
    """
    Create a permset for one or more role.
    """

    permissions = []

    match = re.search(r"named (\S+)", message.content)
    if not match:
        await message.channel.send(
            "Please provide a name.\n\n`gk create permset for <role> named <name>`")
        return

    name = match.group(1)
    name = re.sub(r"\ ", "-", re.sub(r"[^a-zA-Z0-9_\ ]", "", name))

    await request_answer(
        bot,
        message.author,
        f"When creating the permset named `{name}`\nWhat permissions would you like me to give?",
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
        create_permset(bot.db, role, name, permissions)

    await message.channel.send("Created permsets! 🎉")


commands = {
    "gk create permset for": create_permset_for,
}
