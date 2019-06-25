async def pong(bot, message):
    await message.channel.send("pong!")

commands = {
    "!ping": pong,
}
