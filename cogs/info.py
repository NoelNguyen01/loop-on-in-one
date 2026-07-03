"""
cogs/info.py
Các lệnh thông tin: serverinfo, userinfo, botinfo
"""

import platform
import logging

import discord
from discord import app_commands
from discord.ext import commands

from utils.helpers import make_embed, format_number

logger = logging.getLogger("bot.info")


class Info(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # -------------------------------------------------------------
    # /serverinfo
    # -------------------------------------------------------------
    @app_commands.command(name="serverinfo", description="Xem thông tin server")
    async def serverinfo(self, interaction: discord.Interaction):
        guild = interaction.guild
        embed = make_embed(f"📊 Thông tin server: {guild.name}")
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        embed.add_field(name="👑 Chủ sở hữu", value=str(guild.owner), inline=True)
        embed.add_field(name="👥 Thành viên", value=format_number(guild.member_count), inline=True)
        embed.add_field(name="📅 Ngày tạo", value=discord.utils.format_dt(guild.created_at, "D"), inline=True)
        embed.add_field(name="💬 Kênh chat", value=str(len(guild.text_channels)), inline=True)
        embed.add_field(name="🔊 Kênh voice", value=str(len(guild.voice_channels)), inline=True)
        embed.add_field(name="🎭 Số role", value=str(len(guild.roles)), inline=True)
        embed.add_field(name="😄 Emoji", value=str(len(guild.emojis)), inline=True)
        embed.add_field(name="🚀 Boost level", value=f"Cấp {guild.premium_tier}", inline=True)
        embed.add_field(name="🆔 Server ID", value=str(guild.id), inline=True)

        await interaction.response.send_message(embed=embed)

    # -------------------------------------------------------------
    # /userinfo
    # -------------------------------------------------------------
    @app_commands.command(name="userinfo", description="Xem thông tin user")
    @app_commands.describe(user="Người muốn xem thông tin (bỏ trống để xem của bạn)")
    async def userinfo(self, interaction: discord.Interaction, user: discord.Member = None):
        target = user or interaction.user
        embed = make_embed(f"👤 Thông tin: {target.display_name}")
        embed.set_thumbnail(url=target.display_avatar.url)

        embed.add_field(name="🏷️ Tên đầy đủ", value=str(target), inline=True)
        embed.add_field(name="🆔 User ID", value=str(target.id), inline=True)
        embed.add_field(name="🤖 Là Bot?", value="Có" if target.bot else "Không", inline=True)
        embed.add_field(name="📅 Tham gia Discord", value=discord.utils.format_dt(target.created_at, "D"), inline=True)
        if isinstance(target, discord.Member) and target.joined_at:
            embed.add_field(name="📥 Tham gia server", value=discord.utils.format_dt(target.joined_at, "D"), inline=True)

        roles = [role.mention for role in reversed(target.roles) if role.name != "@everyone"]
        roles_text = ", ".join(roles) if roles else "Không có role nào"
        if len(roles_text) > 1024:
            roles_text = roles_text[:1000] + "..."
        embed.add_field(name=f"🎭 Roles ({len(roles)})", value=roles_text, inline=False)

        await interaction.response.send_message(embed=embed)

    # -------------------------------------------------------------
    # /botinfo
    # -------------------------------------------------------------
    @app_commands.command(name="botinfo", description="Xem thông tin bot")
    async def botinfo(self, interaction: discord.Interaction):
        bot = self.bot
        embed = make_embed(f"🤖 Thông tin bot: {bot.user.name}")
        embed.set_thumbnail(url=bot.user.display_avatar.url)

        total_members = sum(g.member_count for g in bot.guilds)
        embed.add_field(name="🌐 Số server", value=format_number(len(bot.guilds)), inline=True)
        embed.add_field(name="👥 Tổng thành viên", value=format_number(total_members), inline=True)
        embed.add_field(name="📶 Ping", value=f"{round(bot.latency * 1000)}ms", inline=True)
        embed.add_field(name="🐍 Python", value=platform.python_version(), inline=True)
        embed.add_field(name="📚 discord.py", value=discord.__version__, inline=True)
        embed.add_field(name="⚙️ Slash commands", value=str(len(bot.tree.get_commands())), inline=True)

        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Info(bot))
