import logging
import subprocess
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

class Warn_Embed(discord.Embed):
    def __init__(self, warn_message : str, command : str):
        super().__init__(colour=discord.colour.Colour.dark_gold(),  title="Command Warning", timestamp=datetime.now())
        self.add_field(name="Warning Field", value="#WARN")
        self.add_field(name="Command", value=f"While executing the command : {command} a warning occurred")
        self.add_field(name="Warn Message", value=warn_message)


class Error_Embed(discord.Embed):
    def __init__(self, error_message : str, command : str):
        super().__init__(colour=discord.colour.Colour.red(),  title="Command Error", timestamp=datetime.now())
        self.add_field(name="Warning Field", value="#ERROR")
        self.add_field(name="Command", value=f"While executing the command : {command} an error occurred")
        self.add_field(name="Error Message", value=error_message)


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

@bot.tree.command(name="Check Local Connection",description="Pings the IP address in the config file to check if the local LAN is connected properly")
async def check_local_connection(interaction : discord.Interaction) -> None:
    logger.info("Check Local Connection Triggered, checking local connection")
    ping = subprocess.run(["ping",config_file["ping_ip"]], stdout=subprocess.PIPE, text=True, timeout=5)
    output = ping.stdout.splitlines()
    j = -1
    for i in range(len(output)):
        if output[i].find("---") != -1:
            j = i + 1
            break
    if j == -1:
        logger.error("Ping Command Failed, Expected Identifier Not Found")
        await interaction.response.send_message(embed=Error_Embed("Usage of Ping Command Failed, Expected Successful command identifier not found","Check Local Connection"))
        await interaction.followup.send(embed=Error_Embed(f"Command Output follows:\n{output}","Check Local Connection"))
        return
    info_line = output[j]
    stat_line = output[j+1]

    output_type : str = "clear"
    output_message : list[str] = []

    info_data = info_line.split(", ") #w packets transmitted, x received, y% packet loss, time zms
    info : dict[str,int]= {}
    info["transmitted"] = int(info_data[0].split(" ")[0])
    info["received"] = int(info_data[1].split(" ")[0])
    info["loss"] = int(info_data[2].split(" ")[0].strip("%"))
    info["time"] = int(info_data[3].split(" ")[-1].strip("ms"))


    stat_data = stat_line.split("=")[1].strip("ms").split("/") #rtt min/avg/max/mdev = w/x/y/z ms
    stats : dict[str,float] = {}
    stats["min"] = float(stat_data[0])
    stats["avg"] = float(stat_data[1])
    stats["max"] = float(stat_data[2])
    stats["mdev"] = float(stat_data[3])


    if info["loss"] > 25:
        output_type = "warn"
        output_message.append(f"Significant packet loss: {info['loss']}%")
    if stats["min"] > 0.7 or stats["max"] > 1.5 or stats["avg"] > 1.0:
        output_type = "warn"
        output_message.append(f"Abnormal response time: Max={stats['max']}, Min={stats['min']}, Avg={stats['avg']}")
    if info["transmitted"] < 4:
        output_type = "warn"
        output_message.append(f"Minimal Packets sent ({info['transmitted']}) data may be unreliable")


    if output_type == "warn":
        output_embed = Warn_Embed("\n".join(output_message),"Check Local Connection")
    elif output_type == "clear":
        output_embed = Message_Embed("Check Local Connection","Local Connection is Okay, No issues Detected")
    else:
        raise Exception(f"Unknown Output Type : {output_type}")

    await interaction.response.send_message(embed=output_embed)
    return


bot.run(token=bot_token, log_handler=handler)

