import logging
from os import getenv

import discord
from discord import app_commands, ui
from discord.ext import commands

#Set up logging using a handler to print to standard system error output
handler = logging.StreamHandler()
logger = logging.Logger("Server_Status")
logger.setLevel(logging.INFO)
logger.addHandler(handler)


#Gets the guild ID from the env file, raises error if missing
guild_id = getenv("GUILD_ID")
if guild_id is None: raise ValueError("Missing GUILD_ID env")
guild = discord.Object(int(guild_id))

#Gets the bot token from the env file, raises error if missing
bot_token = getenv("BOT_TOKEN")
if bot_token is None: raise ValueError("Missing BOT_TOKEN env")

#The main bot class
class Server_Status_Bot(commands.Bot):

    def __init__(self, guild : discord.Object) -> None:
        #Sets the bot permissions to be the required integer and adds !! as a command prefix
        intents = discord.Intents().default()
        intents.message_content=True
        self.guild = guild
        super().__init__(command_prefix=commands.when_mentioned_or("!!"),intents=intents)


    #When the bot has loaded log this and then try to sync commands with the specified guild
    async def on_ready(self):
        logger.info("Logged in as %s", self.user)
        try:
            synced = await self.tree.sync(guild=self.guild)
            id = guild.id if guild != None else "all"
            logger.info("Synced %s commands with server %s", len(synced), id)
        except Exception as e:
            logger.error(e)


bot = Server_Status_Bot(guild)


bot.run(token=bot_token, log_handler=handler)

