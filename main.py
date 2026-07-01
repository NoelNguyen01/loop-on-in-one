import discord
from discord.ext import commands

# Cấu hình bot với tên dự án
bot = commands.Bot(
    command_prefix=config["prefix"],
    intents=discord.Intents.all(),
    help_command=None,
    activity=discord.Game(name="🔄 LOOP ON IN ONE | !help")
)
