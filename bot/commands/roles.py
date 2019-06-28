import re
import random

from discord import Colour
from discord.utils import escape_mentions
from discord.utils import find

from bot.db import Role

from bot.utils import Permission
from bot.utils import find_match


async def create_role_named(bot, message):
    """
    Create a role with name.
    """

    match = find_match(message.content, only_named=True)

    if not match:
        await message.channel.send(
            "Invalid command.\n\n`gk create role named <name>`.")
        return

    name = match.group(1)

    if find(
            lambda r: r.name.lower() == name.lower(),
            message.guild.roles):
        await message.channel.send(
            f"Role name **\"{name}\"** is taken.")
        return

    if not message.author.guild_permissions.manage_roles:
        await message.channel.send(
            "You are not authorized to perform this action.")
        return

    hexx = "%06x" % random.randint(0, 0xFFFFFF)
    colour = Colour(int(hexx, 16))

    role = await message.guild.create_role(
        name=name,
        colour=colour,
        reason="Created for user with complex perms.")

    if Role.create(role, message.author):
        await message.author.add_roles(role)
        await message.channel.send(f"Role named **\"{name}\"** was created!")
        return

    await message.channel.send("Something went wrong...")
    return


async def delete_role_named(bot, message):
    """
    Delete a role by name.
    """

    match = find_match(message.content, only_named=True)

    if not match:
        await message.channel.send(
            "Invalid command.\n\n`gk create role named <name>`.")
        return

    name = match.group(1)

    role = find(
        lambda r: r.name.lower() == name.lower(),
        message.guild.roles)

    if not role:
        await message.channel.send(
            f"No role named **\"{name}\"** was found.")
        return

    if not message.author.guild_permissions.manage_roles:
        await message.channel.send(
            "You are not authorized to perform this action.")
        return

    Role.get(role).delete()
    await role.delete()

    await message.channel.send(f"Role named **\"{name}\"** was deleted!")


async def delete_role(bot, role):
    """
    Delete a role entry after its corresponding Discord role has been 
    removed.
    """

    role_entry = Role.get(role)
    if role_entry:
        role_entry.delete()


commands = {
    "on_message": {
        "gk create role named": create_role_named,
        "gk delete role named": delete_role_named,
    },
    "on_guild_role_delete": [
        delete_role,
    ]
}
