async def pong(bot, message):
    await message.channel.send("pong!")

commands = {
    "on_message": {
        "!ping": pong,
    },
}
