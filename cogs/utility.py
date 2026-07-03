"""
cogs/utility.py
Các lệnh tiện ích: ping, avatar, roll, flip
"""

import random
import logging

import discord
from discord import app_commands
from discord.ext import commands

from utils.helpers import make_embed

logger = logging.getLogger("bot.utility")

DICE_EMOJIS = ["⚀", "⚁", "⚂", "⚃", "⚄", "⚅"]


class Utility(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # -------------------------------------------------------------
    # /ping
    # -------------------------------------------------------------
    @app_commands.command(name="ping", description="Kiểm tra độ trễ của bot")
    async def ping(self, interaction: discord.Interaction):
        latency = round(self.bot.latency * 1000)
        embed = make_embed("🏓 Pong!", f"Độ trễ: **{latency}ms**")
        await interaction.response.send_message(embed=embed)

    # -------------------------------------------------------------
    # /avatar
    # -------------------------------------------------------------
    @app_commands.command(name="avatar", description="Xem avatar của người dùng")
    @app_commands.describe(user="Người muốn xem avatar (bỏ trống để xem của bạn)")
    async def avatar(self, interaction: discord.Interaction, user: discord.Member = None):
        target = user or interaction.user
        embed = make_embed(f"🖼️ Avatar của {target.display_name}")
        embed.set_image(url=target.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    # -------------------------------------------------------------
    # /roll
    # -------------------------------------------------------------
    @app_commands.command(name="roll", description="Tung xí ngầu 1-6")
    async def roll(self, interaction: discord.Interaction):
        result = random.randint(1, 6)
        embed = make_embed("🎲 Xí ngầu", f"{DICE_EMOJIS[result - 1]} Kết quả: **{result}**")
        await interaction.response.send_message(embed=embed)

    # -------------------------------------------------------------
    # /flip
    # -------------------------------------------------------------
    @app_commands.command(name="flip", description="Tung đồng xu")
    async def flip(self, interaction: discord.Interaction):
        result = random.choice(["Sấp", "Ngửa"])
        embed = make_embed("🪙 Đồng xu", f"Kết quả: **{result}**")
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Utility(bot))
