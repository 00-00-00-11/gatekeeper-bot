import re

from discord.utils import find

from bot.db import create_permset, edit_permset
from bot.utils import request_answer
from bot.utils import Permission


async def create_permset_named(bot, message):
    """
    Create a permset for one or more role.
    """

    match = re.search(r"named (\S+) for (.+$)", message.content)
    if not match:
        await message.channel.send(
            "Invalid command.\n\n`gk create permset named <name> for <role> `")
        return

    name = match.group(1)
    name = re.sub(r"\ ", "-", re.sub(r"[^a-zA-Z0-9_\ ]", "", name))
    role_name = match.group(2).lower()
    role = find(lambda r: r.name.lower() == role_name, message.guild.roles)
    if not role:
        await message.channel.send(
            f"No role named `{role_name}` was found.")
        return

    result, response = create_permset(bot.db, role, name, Permission.default())
    if not result:
        await message.channel.send(f"{response}! 😧")
        return

    permissions = []

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

    if permissions:
        result, response = edit_permset(bot.db, role, name, permissions)
        await message.channel.send(f"{response}. {'🎉' if result else '💩'}")


commands = {
    "on_message": {
        "gk create permset named": create_permset_named,
    },
}
