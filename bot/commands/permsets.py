from discord.utils import find

from bot.db import Permset
from bot.db import Role

from bot.utils import Permission
from bot.utils import find_match
from bot.utils import clean


async def list_permsets_for(bot, message):
    """
    List all permsets for a specific role.

    Example usage:

        gk list permsets for <role>
    """

    match = find_match(message.content, named=False)

    if not match:
        await message.channel.send(
            "Invalid command.\n\n`gk list permsets for <role>`.")
        return

    role = find(
        lambda r: r.name.lower() == match.group(1).lower(),
        message.guild.roles)

    if not role:
        await message.channel.send(
            f"No role named **\"{match.group(2)}\"** was found.\n"
            f"Consider creating one? `gk create role named {match.group(1)}`.")
        return

    permset_names = [str(p) for p in Permset.get_all(role)]
    permsets = "\n".join(permset_names)

    await message.channel.send(
        f"Permsets for role **\"{match.group(1)}\"** are:\n\n{permsets}")


async def create_permset_named(bot, message):
    """
    Creates a permset for a role.

    Example usage:

        gk create permset named <name> for <role>
    """

    match = find_match(message.content)

    if not match:
        await message.channel.send(
            "Invalid command.\n\n`gk create permset named <name> for <role> `.")
        return

    role = find(
        lambda r: r.name.lower() == match.group(2).lower(),
        message.guild.roles)

    if not role:
        await message.channel.send(
            f"No role named **\"{match.group(2)}\"** was found.\n"
            f"Consider creating one? `gk create role named {match.group(2)}`.")
        return

    role_entry = Role.get(role)

    if not role_entry:
        await message.channel.send(
            f"Role named **\"{match.group(1)}\"** is a simple role.")
        return

    if not role_entry.check_member_for_perm(
            message.author,
            Permission.MANAGE_PERMSETS()):
        await message.channel.send(
            "You are not authorized to perform this action.")
        return

    name = clean(match.group(1))

    if Permset.exists(name, role=role):
        await message.channel.send(
            f"Permset named **\"{name}\"** already exists.")
        return

    permset = Permset.create(role, name, Permission.default())

    permissions = await Permission.select_permissions(
        bot,
        message.author,
        Permset.for_user(role, message.author).giveable,
        destination=message.channel)

    if permissions:
        permset.update(permissions=permissions)

    await message.channel.send(f"Permset named **\"{name}\"** was created!")


async def update_permset_named(bot, message):
    """
    Updates a permset for a role.

    Example usage:

        gk update permset named <name> for <role>
    """

    match = find_match(message.content)

    if not match:
        await message.channel.send(
            "Invalid command.\n\n`gk update permset named <name> for <role> `")
        return

    role = find(
        lambda r: r.name.lower() == match.group(2).lower(),
        message.guild.roles)

    if not role:
        await message.channel.send(
            f"No role named **\"{match.group(2)}\"** was found.\n"
            f"Consider creating one? `gk create role named {match.group(2)}`.")
        return

    name = clean(match.group(1))
    permset = Permset.get(role, name)

    if not permset:
        await message.channel.send(
            f"No permset named **\"{name}\"** was found")
        return

    role_entry = Role.get(role)

    if not role_entry:
        await message.channel.send(
            f"Role named **\"{match.group(1)}\"** is a simple role.")
        return

    if not role_entry.check_member_for_perm(
            message.author,
            Permission.MANAGE_PERMSETS()):
        await message.channel.send(
            "You are not authorized to perform this action.")
        return

    permissions = await Permission.select_permissions(
        bot,
        message.author,
        Permset.for_user(role, message.author).giveable,
        destination=message.channel)

    if permissions:
        permset.update(permissions=permissions)
        await message.channel.send(f"Permset named **\"{name}\"** was updated!")


async def delete_permset_named(bot, message):
    """
    Delete a permset for a role.

    Example usage:

        gk delete permset named <name> for <role>
    """

    match = find_match(message.content)

    if not match:
        await message.channel.send(
            "Invalid command.\n\n`gk delete permset named <name> for <role> `")
        return

    role = find(
        lambda r: r.name.lower() == match.group(2).lower(),
        message.guild.roles)

    if not role:
        await message.channel.send(
            f"No role named **\"{match.group(2)}\"** was found.")
        return

    name = clean(match.group(1))
    permset = Permset.get(role, name)

    if not permset:
        await message.channel.send(
            f"No permset named **\"{name}\"** was found.")
        return

    role_entry = Role.get(role)

    if not role_entry:
        await message.channel.send(
            f"Role named **\"{match.group(1)}\"** is a simple role.")
        return

    if not role_entry.check_member_for_perm(
            message.author,
            Permission.MANAGE_PERMSETS()):
        await message.channel.send(
            "You are not authorized to perform this action.")
        return

    permset.delete()
    await message.channel.send(f"Permset named **\"{name}\"** was deleted!")


async def grant_permset_to(bot, message):
    """
    Grant a user to a permset.

    Example usage:

        gk grant permset named <name> for <role> to <user mention> [<user mention>, ...]
    """

    match = find_match(message.content, to=True)

    if not match:
        await message.channel.send(
            "Invalid command.\n\n`gk create permset named <name> for <role> `")
        return

    role = find(
        lambda r: r.name.lower() == match.group(2).lower(),
        message.guild.roles)

    if not role:
        await message.channel.send(
            f"No role named **\"{match.group(2)}\"** was found.\n"
            f"Consider creating one? `gk create role named {match.group(2)}`.")
        return

    role_entry = Role.get(role)

    if not role_entry:
        await message.channel.send(
            f"Role named **\"{match.group(1)}\"** is a simple role.")
        return

    if not role_entry.check_member_for_perm(
            message.author,
            Permission.MANAGE_USERS()):
        await message.channel.send(
            "You are not authorized to perform this action.")
        return

    name = clean(match.group(1))
    permset = Permset.get(role, name)

    if not permset:
        await message.channel.send(
            f"No permset named **\"{name}\"** was found")
        return

    for user in message.mentions:
        permset.add_member(user)

    await message.channel.send(
        f"Permset named **\"{name}\"** given to {len(message.mentions)} users!")


commands = {
    "on_message": {
        "gk list permsets": list_permsets_for,
        "gk create permset named": create_permset_named,
        "gk update permset named": update_permset_named,
        "gk delete permset named": delete_permset_named,
        "gk grant permset named": grant_permset_to,
    },
}
