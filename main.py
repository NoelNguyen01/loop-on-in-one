import discord
from discord.ext import commands
import json
import os

# Load config
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

# Khởi tạo bot với activity ngay từ đầu
bot = commands.Bot(
    command_prefix=config["prefix"],
    intents=discord.Intents.all(),
    help_command=None,  
    activity=discord.Game(name="🔄 LOOP ON IN ONE | !help")  
