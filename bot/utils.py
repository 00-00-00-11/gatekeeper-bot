import discord.utils

from enum import Enum


class Permission(Enum):
    CREATE_AND_DELETE = 1
    MODIFY_CHANNELS = 2
    MODIFY_ROLES = 3
    INVITE_USERS = 4
    REMOVE_USERS = 5

    @staticmethod
    def all() -> list:
        return [
            Permission.CREATE_AND_DELETE,
            Permission.MODIFY_CHANNELS,
            Permission.MODIFY_ROLES,
            Permission.INVITE_USERS,
            Permission.REMOVE_USERS, ]


async def request_answer(
        bot,
        user,
        question: str,
        options: dict,
        destination=None,
        timeout: float = 120.0):
    """
    Helper method to ask a question and run callbacks for each provided answer.

    Params:
        bot: The Discord Client that will ask the question.
        user: A Discord User that the question will be directed to.
        question: The question that will be asked.
        options: Dict of emoji and tuples that represent multiple choice 
                 options for the user to select. Keys must be valid emojis that 
                 the Client can react with. Each tuple contains descriptive 
                 text, and a callback function, in the format (description, 
                 callback)
        destination: Where to ask the question.
        timeout: How long the bot should wait for an answer.
    """

    # Format the body text...
    message_body = f"{question}\n\n"

    for emoji, values in options.items():
        description = values[0]
        message_body += f"{emoji} - {description}\n"

    message_body += f"\nType `submit` to submit.\n"

    # Determine where to send messages...
    if not destination:
        destination = user

    # Ask the question and add placeholder reactions.
    message = await destination.send(message_body)

    for emoji in options.keys():
        await message.add_reaction(emoji)

    # Initialize a list of results.
    results = []

    # Wait for the user to submit their reactions (choices).
    try:
        await bot.wait_for(
            "message",
            timeout=timeout,
            check=lambda m: m.author == user and m.content == "submit")
    except TimeoutError:
        await destination.send("Request expired. 👎")
        return

    # Get the reactions made by the user,
    # store the corresponding callback function in our list of results.
    message = discord.utils.get(bot.cached_messages, id=message.id)
    for reaction in message.reactions:
        users = await reaction.users().flatten()
        if user in users:
            results.append(options[reaction.emoji][1])

    await destination.send("Selections confirmed! 👍")

    # Run each callback.
    for callback in results:
        callback()
