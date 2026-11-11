import logging
from datetime import datetime
from json import load
from os import getenv
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from typing import Any

import discord
from discord import app_commands, ui
from discord.ext import commands

#Set up logging using a handler to print to standard system error output
handler = logging.StreamHandler()
logger = logging.Logger("Server_Status")
logger.setLevel(logging.INFO)
logger.addHandler(handler)


with Path("src/config.json").open() as file:
    config_file : dict[str, Any] = load(file)



#Gets the guild ID from the env file, raises error if missing
guild_id = getenv("GUILD_ID")
if guild_id is None: raise ValueError("Missing GUILD_ID env")
guild = discord.Object(int(guild_id))

#Gets the bot token from the env file, raises error if missing
bot_token = getenv("BOT_TOKEN")
if bot_token is None: raise ValueError("Missing BOT_TOKEN env")


class Message_Embed(discord.Embed):
    def __init__(self, title : str, message : str):
        super().__init__(title=title, timestamp=datetime.now())
        self.add_field(name="message_field",value=message)


#The main bot class
class Server_Status_Bot(commands.Bot):

    def __init__(self, notification_channel_id : int, guild : discord.Object) -> None:
        #Sets the bot permissions to be the required integer and adds !! as a command prefix
        intents = discord.Intents().default()
        intents.message_content=True
        self.guild = guild
        self.notification_channel_id = notification_channel_id
        super().__init__(command_prefix=commands.when_mentioned_or("!!"),intents=intents)


    #When the bot has loaded log this and then try to sync commands with the specified guild
    async def on_ready(self) -> None:
        logger.info("Logged in as %s", self.user)
        try:
            synced = await self.tree.sync(guild=self.guild)
            id = guild.id if guild != None else "all"
            logger.info("Synced %s commands with server %s", len(synced), id)
        except Exception as e:
            logger.error(e)

        notification_channel = self.get_channel(self.notification_channel_id)
        if notification_channel is None: raise ValueError("No notification channel given")
        if not(isinstance(notification_channel , discord.channel.TextChannel)): raise ValueError("Notification Channel must be a normal text channel")

        self.notification_channel = notification_channel
        await self.notification_channel.send(embed=Message_Embed("Sever Status - Connection Update", "Server Status Bot successfully connected to discord"))

    async def close(self) -> None:
        await self.notification_channel.send(embed=Message_Embed("Sever Status - Connection Update", "Server Status Bot restarting"))
        return await super().close()


bot = Server_Status_Bot(config_file["notification_channel"], guild)


bot.run(token=bot_token, log_handler=handler)

