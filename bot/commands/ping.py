async def pong(bot, message):
    await message.channel.send("pong!")
    await bot.log("Message has been recieved and responded to.")

commands = {
    "on_message": {
        "!ping": pong,
    },
}
