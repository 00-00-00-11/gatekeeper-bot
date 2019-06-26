import discord.utils


class Permission:
    def __init__(
            self,
            emoji: str,
            value: int,
            description: str = None):
        self.emoji = emoji
        self.value = value
        self.description = description

    @staticmethod
    def default() -> list:
        return [
            Permission.INVITE_USERS,
            Permission.CREATE_AND_DELETE_CHANNELS, ]

    @staticmethod
    def all() -> list:
        return [
            Permission.CREATE_AND_DELETE_CHANNELS,
            Permission.MODIFY_CHANNELS,
            Permission.MODIFY_ROLES,
            Permission.INVITE_USERS,
            Permission.REMOVE_USERS,
            Permission.CREATE_PERMSETS,
            Permission.DELETE_ROLE, ]

    @staticmethod
    def from_value(value: int):
        value = int(value)
        if value == 1:
            return Permission.CREATE_AND_DELETE_CHANNELS
        elif value == 2:
            return Permission.MODIFY_CHANNELS
        elif value == 3:
            return Permission.MODIFY_ROLES
        elif value == 4:
            return Permission.INVITE_USERS
        elif value == 5:
            return Permission.REMOVE_USERS
        elif value == 6:
            return Permission.CREATE_PERMSETS
        elif value == 7:
            return Permission.DELETE_ROLE
        else:
            print("SOMETHING WRONG")

    @staticmethod
    def CREATE_AND_DELETE_CHANNELS():
        return Permission(
            "📻",
            1,
            description="Create and delete role specific channels.")

    @staticmethod
    def MODIFY_CHANNELS():
        return Permission(
            "📝",
            2,
            description="Modify properties of existing channels.")

    @staticmethod
    def MODIFY_ROLES():
        return Permission(
            "🖌",
            3,
            description="Modify properties of the related Discord role.")

    @staticmethod
    def INVITE_USERS():
        return Permission(
            "📯",
            4,
            description="Invite new users to the role.")

    @staticmethod
    def REMOVE_USERS():
        return Permission(
            "👞",
            5,
            description="Remove users from the role.")

    @staticmethod
    def CREATE_PERMSETS():
        return Permission(
            "📐",
            6,
            description="Create new permsets for the role.")

    @staticmethod
    def DELETE_ROLE():
        return Permission(
            "💣",
            7,
            description="Delete the entire role.")


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
