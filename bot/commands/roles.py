import re
import random

from discord import Colour
from discord.utils import escape_mentions
from discord.utils import find

from bot.db import create_role


async def create_role_named(bot, message):
    """

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


commands = {
    "on_message": {
        "gk create role named": create_role_named,
    },
}
