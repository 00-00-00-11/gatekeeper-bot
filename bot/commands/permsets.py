import re

from discord.utils import find

from bot.db import create_permset
from bot.db import edit_permset
from bot.db import delete_permset
from bot.db import delete_all_permsets
from bot.db import create_member
from bot.db import delete_all_members_under
from bot.db import get_giveable_permset
from bot.db import check_for_perm

from bot.utils import select_permissions
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

    if not check_for_perm(
            bot.db,
            role,
            message.author,
            Permission.CREATE_PERMSETS):
        await message.channel.send(
            "You do not have sufficient permissions to perform this action.")
        return

    result, response = create_permset(bot.db, role, name, Permission.default())
    if not result:
        await message.channel.send(f"{response}! 😧")
        return

    permissions = await select_permissions(
        bot,
        message.author,
        get_giveable_permset(bot.db, role, message.author),
        destination=message.channel)

    if permissions:
        result, response = edit_permset(bot.db, role, name, permissions)
        await message.channel.send(f"{response}. {'🎉' if result else '💩'}")


async def delete_permset_named(bot, message):
    """
    Delete a permset and its members
    """

    match = re.search(r"named (\S+) for (.+$)", message.content)
    if not match:
        await message.channel.send(
            "Invalid command.\n\n`gk delete permset named <name> for <role> `")
        return

    name = match.group(1)
    name = re.sub(r"\ ", "-", re.sub(r"[^a-zA-Z0-9_\ ]", "", name))
    role_name = match.group(2).lower()
    role = find(lambda r: r.name.lower() == role_name, message.guild.roles)
    if not role:
        await message.channel.send(
            f"No role named `{role_name}` was found.")
        return

    delete_permset(bot.db, role, name)


async def grant_permset_to(bot, message):
    """
    Grant users to a permset.
    """

    match = re.search(r"named (\S+) for (.+) to", message.content)
    if not match:
        await message.channel.send(
            "Invalid command.\n\n`gk grant permset named <name> for <role> to <user mention> [<user mention>, ...]`")
        return

    name = match.group(1)
    name = re.sub(r"\ ", "-", re.sub(r"[^a-zA-Z0-9_\ ]", "", name))
    role_name = match.group(2).lower()
    role = find(lambda r: r.name.lower() == role_name, message.guild.roles)
    if not role:
        await message.channel.send(
            f"No role named `{role_name}` was found.")
        return
    users = message.mentions

    for user in users:
        create_member(bot.db, role, user, name)


async def clear_permsets_for(bot, role):
    """
    Deletes all permsets related to a role.
    """

    delete_all_permsets(bot.db, role)


commands = {
    "on_message": {
        "gk create permset named": create_permset_named,
        "gk delete permset named": delete_permset_named,
        "gk grant permset named": grant_permset_to,
    },
    "on_guild_role_delete": [
        clear_permsets_for,
    ]
}
