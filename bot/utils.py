import re
import discord.utils


def find_match(
        content: str,
        named: bool = True,
        only_named: bool = False,
        to: bool = False) -> object:
    """
    Find match for command parsing.
    """

    if only_named:
        match = re.search(r"named (.+$)", content)
        return match
    if not named:
        match = re.search(r"for (.+)", content)
        return match
    if to:
        match = re.search(r"named (\S+) for (.+) to", content)
        return match
    match = re.search(r"named (\S+) for (.+)", content)
    return match


def clean(
        content: str) -> str:
    """
    Clean up a string of special characters and spaces.
    """

    return re.sub(r"\ ", "-", re.sub(r"[^a-zA-Z0-9_\ ]", "", content))


class Permission:
    def __init__(
            self,
            emoji: str,
            value: int,
            description: str = None):
        self.emoji = emoji
        self.value = value
        self.description = description

    def __eq__(self, other):
        try:
            return self.value == other.value
        except AttributeError:
            return False

    def __ne__(self, other):
        return not self == other

    @staticmethod
    def default() -> list:
        return [
            Permission.INVITE_USERS, ]

    @staticmethod
    def all() -> list:
        return [
            Permission.INVITE_USERS,
            Permission.REMOVE_USERS,
            Permission.MANAGE_USERS,
            Permission.MANAGE_PERMSETS, ]

    @staticmethod
    def from_value(value: int):
        value = int(value)
        if value == 1:
            return Permission.INVITE_USERS
        elif value == 2:
            return Permission.REMOVE_USERS
        elif value == 3:
            return Permission.MANAGE_USERS
        elif value == 4:
            return Permission.MANAGE_PERMSETS
        else:
            return None

    @staticmethod
    def INVITE_USERS():
        return Permission(
            "📯",
            1,
            description="Invite new users to the role.")

    @staticmethod
    def REMOVE_USERS():
        return Permission(
            "👞",
            2,
            description="Remove users from the role.")

    @staticmethod
    def MANAGE_USERS():
        return Permission(
            "📣",
            3,
            description="Promote, demote and remove users from the role.")

    @staticmethod
    def MANAGE_PERMSETS():
        return Permission(
            "🔨",
            4,
            description="Create, edit and delete permsets for the role.")

    @staticmethod
    async def select_permissions(
            bot,
            user,
            permissions: list,
            destination=None,
            timeout: float = 120.0) -> list:
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
        message_body = f"When creating the permset, what permissions would you like me to give?\n\n"

        emojis = []
        for permission in permissions:
            emojis.append(permission().emoji)
            message_body += f"{permission().emoji} - {permission().description}\n"

        message_body += f"\nType `submit` to submit.\n"

        # Determine where to send messages...
        if not destination:
            destination = user

        # Ask the question and add placeholder reactions.
        message = await destination.send(message_body)

        for emoji in emojis:
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
            return None

        # Get the reactions made by the user,
        # store the corresponding callback function in our list of results.
        message = discord.utils.get(bot.cached_messages, id=message.id)
        for reaction in message.reactions:
            users = await reaction.users().flatten()
            if user in users:
                results.append(permissions[emojis.index(reaction.emoji)])

        await destination.send("Selections confirmed! 👍")

        return results
