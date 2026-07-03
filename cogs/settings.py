"""
cogs/settings.py
Cài đặt server: kênh chào mừng, tạm biệt, log voice, tên tiền tệ
Chỉ Admin mới có quyền sử dụng các lệnh trong cog này
"""

import time
import logging

import discord
from discord import app_commands
from discord.ext import commands

from utils.helpers import make_embed, success_embed, error_embed, parse_duration

logger = logging.getLogger("bot.settings")


class Settings(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = bot.db
        # Lưu tạm id bản ghi voice_log đang mở của mỗi user để cập nhật khi rời voice
        self.active_voice_sessions = {}  # {(guild_id, user_id): (log_id, join_time, channel_name)}

    # -------------------------------------------------------------
    # /setwelcome
    # -------------------------------------------------------------
    @app_commands.command(name="setwelcome", description="[Admin] Đặt kênh chào mừng thành viên mới")
    @app_commands.default_permissions(administrator=True)
    @app_commands.checks.has_permissions(administrator=True)
    async def setwelcome(self, interaction: discord.Interaction, channel: discord.TextChannel):
        await self.db.set_guild_setting(interaction.guild_id, "welcome_channel", str(channel.id))
        await interaction.response.send_message(embed=success_embed(f"Đã đặt kênh chào mừng: {channel.mention}"))

    # -------------------------------------------------------------
    # /setgoodbye
    # -------------------------------------------------------------
    @app_commands.command(name="setgoodbye", description="[Admin] Đặt kênh tạm biệt thành viên")
    @app_commands.default_permissions(administrator=True)
    @app_commands.checks.has_permissions(administrator=True)
    async def setgoodbye(self, interaction: discord.Interaction, channel: discord.TextChannel):
        await self.db.set_guild_setting(interaction.guild_id, "goodbye_channel", str(channel.id))
        await interaction.response.send_message(embed=success_embed(f"Đã đặt kênh tạm biệt: {channel.mention}"))

    # -------------------------------------------------------------
    # /setvoicelog
    # -------------------------------------------------------------
    @app_commands.command(name="setvoicelog", description="[Admin] Đặt kênh log hoạt động voice")
    @app_commands.default_permissions(administrator=True)
    @app_commands.checks.has_permissions(administrator=True)
    async def setvoicelog(self, interaction: discord.Interaction, channel: discord.TextChannel):
        await self.db.set_guild_setting(interaction.guild_id, "voicelog_channel", str(channel.id))
        await interaction.response.send_message(embed=success_embed(f"Đã đặt kênh log voice: {channel.mention}"))

    # -------------------------------------------------------------
    # /setcurrency
    # -------------------------------------------------------------
    @app_commands.command(name="setcurrency", description="[Admin] Đổi tên đơn vị tiền tệ của server")
    @app_commands.default_permissions(administrator=True)
    @app_commands.checks.has_permissions(administrator=True)
    async def setcurrency(self, interaction: discord.Interaction, name: str):
        name = name.strip()
        if not (1 <= len(name) <= 20):
            await interaction.response.send_message(embed=error_embed("Tên tiền tệ phải từ 1-20 ký tự."), ephemeral=True)
            return
        await self.db.set_guild_setting(interaction.guild_id, "currency_name", name)
        await interaction.response.send_message(embed=success_embed(f"Đã đổi tên đơn vị tiền tệ thành **{name}**."))

    # -------------------------------------------------------------
    # Listener: chào mừng thành viên mới
    # -------------------------------------------------------------
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        settings = await self.db.get_guild_settings(member.guild.id)
        channel_id = settings["welcome_channel"]
        if not channel_id:
            return

        channel = member.guild.get_channel(int(channel_id))
        if channel is None:
            return

        embed = make_embed(
            "👋 Chào mừng thành viên mới!",
            f"Xin chào {member.mention}, chào mừng bạn đến với **{member.guild.name}**!\n"
            f"Server hiện có **{member.guild.member_count}** thành viên.",
            color=0x2ECC71,
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        try:
            await channel.send(embed=embed)
        except discord.HTTPException as e:
            logger.error(f"Không thể gửi tin chào mừng: {e}")

    # -------------------------------------------------------------
    # Listener: tạm biệt thành viên rời server
    # -------------------------------------------------------------
    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        settings = await self.db.get_guild_settings(member.guild.id)
        channel_id = settings["goodbye_channel"]
        if not channel_id:
            return

        channel = member.guild.get_channel(int(channel_id))
        if channel is None:
            return

        embed = make_embed(
            "👋 Tạm biệt!",
            f"**{member.display_name}** đã rời khỏi server. Hẹn gặp lại!",
            color=0xE74C3C,
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        try:
            await channel.send(embed=embed)
        except discord.HTTPException as e:
            logger.error(f"Không thể gửi tin tạm biệt: {e}")

    # -------------------------------------------------------------
    # Listener: log hoạt động voice
    # -------------------------------------------------------------
    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        settings = await self.db.get_guild_settings(member.guild.id)
        channel_id = settings["voicelog_channel"]

        key = (member.guild.id, member.id)
        now = int(time.time())

        # User vào voice (trước đó không ở kênh nào, giờ đã vào)
        if before.channel is None and after.channel is not None:
            log_id = await self.db.add_voice_join(member.id, member.guild.id, after.channel.name, now)
            self.active_voice_sessions[key] = (log_id, now, after.channel.name)

            if channel_id:
                log_channel = member.guild.get_channel(int(channel_id))
                if log_channel:
                    embed = make_embed(
                        "🔊 Vào Voice",
                        f"{member.mention} đã vào kênh **{after.channel.name}**",
                        color=0x3498DB,
                    )
                    try:
                        await log_channel.send(embed=embed)
                    except discord.HTTPException:
                        pass

        # User rời voice hoàn toàn (trước đó ở kênh, giờ không còn ở kênh nào)
        elif before.channel is not None and after.channel is None:
            session = self.active_voice_sessions.pop(key, None)
            if session:
                log_id, join_time, channel_name = session
                duration = now - join_time
                await self.db.update_voice_leave(log_id, now, duration)

                if channel_id:
                    log_channel = member.guild.get_channel(int(channel_id))
                    if log_channel:
                        embed = make_embed(
                            "🔇 Rời Voice",
                            f"{member.mention} đã rời kênh **{channel_name}**\n"
                            f"Thời gian ở lại: **{parse_duration(duration)}**",
                            color=0x95A5A6,
                        )
                        try:
                            await log_channel.send(embed=embed)
                        except discord.HTTPException:
                            pass

        # User chuyển kênh voice
        elif before.channel is not None and after.channel is not None and before.channel != after.channel:
            session = self.active_voice_sessions.get(key)
            if session:
                log_id, join_time, _ = session
                duration = now - join_time
                await self.db.update_voice_leave(log_id, now, duration)

            new_log_id = await self.db.add_voice_join(member.id, member.guild.id, after.channel.name, now)
            self.active_voice_sessions[key] = (new_log_id, now, after.channel.name)

            if channel_id:
                log_channel = member.guild.get_channel(int(channel_id))
                if log_channel:
                    embed = make_embed(
                        "🔀 Chuyển kênh Voice",
                        f"{member.mention} đã chuyển từ **{before.channel.name}** sang **{after.channel.name}**",
                        color=0xF1C40F,
                    )
                    try:
                        await log_channel.send(embed=embed)
                    except discord.HTTPException:
                        pass


async def setup(bot: commands.Bot):
    await bot.add_cog(Settings(bot))

