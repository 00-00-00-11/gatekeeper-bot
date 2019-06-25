import os

from bot import create_bot

if __name__ == "__main__":
    token = os.environ.get("BOT_TOKEN")

    if not token:
        raise EnvironmentError

    bot = create_bot()
    bot.run(token)
