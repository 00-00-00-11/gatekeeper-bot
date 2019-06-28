import re

from discord.utils import find

from bot.db import Role
from bot.utils import Permission


async def invite_users(bot, message):
    """
    Inviting users to a role.
    """

    match = re.search(r"to (.+$)", message.content)

    if not match:
        await message.channel.send(
            "Invalid command.\n\n`gk invite <user mention> [<user_mention>, ...] to <role>")
        return

    role = find(
        lambda r: r.name.lower() == match.group(1).lower(),
        message.guild.roles)

    if not role:
        await message.channel.send(
            f"No role named **\"{match.group(1)}\"** was found.")
        return

    role_entry = Role.get(role)

    if not role_entry:
        await message.channel.send(
            f"Role named **\"{match.group(1)}\"** is a simple role.")
        return

    if not role_entry.check_member_for_perm(
            message.author,
            Permission.INVITE_USERS()):
        await message.channel.send(
            "You are not authorized to perform this action.")
        return

    for user in message.mentions:
        role_entry.add_member(user, "default")

    await message.channel.send(f"{len(message.mentions)} were added to **\"{match.group(1)}\"**")


async def kick_users(bot, message):
    """
    Kicking users from a role.
    """

    match = re.search(r"from (.+$)", message.content)

    if not match:
        await message.channel.send(
            "Invalid command.\n\n`gk kick <user mention> [<user_mention>, ...] from <role>")
        return

    role = find(
        lambda r: r.name.lower() == match.group(1).lower(),
        message.guild.roles)

    if not role:
        await message.channel.send(
            f"No role named **\"{match.group(1)}\"** was found.")
        return

    role_entry = Role.get(role)

    if not role_entry:
        await message.channel.send(
            f"Role named **\"{match.group(1)}\"** is a simple role.")
        return

    if not role_entry.check_member_for_perm(
            message.author,
            Permission.REMOVE_USERS()):
        await message.channel.send(
            "You are not authorized to perform this action.")
        return

    for user in message.mentions:
        role_entry.remove_member(user)

    await message.channel.send(f"{len(message.mentions)} were removed from **\"{match.group(1)}\"**")


commands = {
    "on_message": {
        "gk invite": invite_users,
        "gk kick": kick_users,
    }
}
