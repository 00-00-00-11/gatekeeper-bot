import re
import random

from discord import Colour
from discord.utils import escape_mentions
from discord.utils import find

from bot.db import create_role
from bot.db import delete_all_members
from bot.db import delete_all_permsets
from bot.db import check_for_perm

from bot.utils import Permission


async def create_role_named(bot, message):
    """
    Create a new role.
    """

    match = re.search(r"named (.+$)", message.content)
    if not match:
        await message.channel.send(
            "Please provide a name.\n\n`gk create role named <name>`")
        return

    name = match.group(1)

    # Create a new colour.
    hexx = "%06x" % random.randint(0, 0xFFFFFF)
    colour = Colour(int(hexx, 16))

    role = await message.guild.create_role(
        name=name,
        colour=colour,
        reason="Created for user with complex perms.")

    create_role(bot.db, role, message.author)
    await message.author.add_roles(role)
    await message.channel.send("Created role successfully. 👍")


async def delete_role_named(bot, message):
    """
    Delete a role by name.
    """

    match = re.search(r"named (.+$)", message.content)
    if not match:
        await message.channel.send(
            "Please provide a name.\n\n`gk delete role named <name>`")
        return

    name = match.group(1)

    role = find(lambda r: r.name == name, message.guild.roles)

    if not role:
        await message.channel.send(f"No role named `{name}` was found.")
        return

    if not check_for_perm(
            bot.db,
            role,
            message.author,
            Permission.DELETE_ROLE):
        await message.channel.send("You do not have sufficient permissions to perform this action.")
        return

    await role.delete()
    await message.channel.send("Deleted role! 💣")


async def clear_role(bot, role):
    """
    Clear a role from the database, removing its users and permsets.
    """

    # Delete the members in the role.
    delete_all_members(bot.db, role)

    # Delete all permsets for the role.
    delete_all_permsets(bot.db, role)


commands = {
    "on_message": {
        "gk create role named": create_role_named,
        "gk delete role named": delete_role_named,
    },
    "on_guild_role_delete": [
        clear_role,
    ]
}
