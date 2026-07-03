"""
cogs/keyword.py
Hệ thống từ khóa tự động phản hồi
"""

import logging

import discord
from discord import app_commands
from discord.ext import commands

from utils.helpers import make_embed, success_embed, error_embed, check_admin

logger = logging.getLogger("bot.keyword")


class Keyword(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = bot.db

    # -------------------------------------------------------------
    # /setkeyword
    # -------------------------------------------------------------
    @app_commands.command(name="setkeyword", description="Tạo từ khóa tự động phản hồi")
    @app_commands.describe(keyword="Từ khóa kích hoạt", response="Nội dung bot sẽ trả lời")
    async def setkeyword(self, interaction: discord.Interaction, keyword: str, response: str):
        keyword = keyword.strip().lower()
        if len(keyword) < 2:
            await interaction.response.send_message(embed=error_embed("Từ khóa phải có ít nhất 2 ký tự."), ephemeral=True)
            return

        success = await self.db.add_keyword(interaction.guild_id, keyword, response, interaction.user.id)
        if success:
            embed = success_embed(f"Đã tạo từ khóa `{keyword}` → \"{response}\"")
        else:
            embed = error_embed(f"Từ khóa `{keyword}` đã tồn tại. Hãy xóa trước nếu muốn thay đổi.")
        await interaction.response.send_message(embed=embed)

    # -------------------------------------------------------------
    # /delkeyword
    # -------------------------------------------------------------
    @app_commands.command(name="delkeyword", description="Xóa một từ khóa")
    @app_commands.describe(keyword="Từ khóa cần xóa")
    async def delkeyword(self, interaction: discord.Interaction, keyword: str):
        keyword = keyword.strip().lower()
        existing = await self.db.get_keyword(interaction.guild_id, keyword)

        if existing is None:
            await interaction.response.send_message(embed=error_embed("Từ khóa không tồn tại."), ephemeral=True)
            return

        is_admin = check_admin(interaction.user)
        is_creator = str(interaction.user.id) == existing["created_by"]

        if not (is_admin or is_creator):
            await interaction.response.send_message(
                embed=error_embed("Bạn chỉ có thể xóa từ khóa do mình tạo, hoặc cần quyền Admin."),
                ephemeral=True,
            )
            return

        await self.db.delete_keyword(interaction.guild_id, keyword)
        await interaction.response.send_message(embed=success_embed(f"Đã xóa từ khóa `{keyword}`."))

    # -------------------------------------------------------------
    # /listkeyword
    # -------------------------------------------------------------
    @app_commands.command(name="listkeyword", description="Xem danh sách từ khóa trong server")
    async def listkeyword(self, interaction: discord.Interaction):
        rows = await self.db.get_all_keywords(interaction.guild_id)

        if not rows:
            await interaction.response.send_message(embed=error_embed("Server chưa có từ khóa nào."))
            return

        lines = [f"`{row['keyword']}` — dùng {row['usage_count']} lần" for row in rows]
        # Discord embed field giới hạn 1024 ký tự, chia nhỏ nếu cần
        text = "\n".join(lines)
        if len(text) > 4000:
            text = text[:4000] + "\n... (còn nhiều hơn)"

        embed = make_embed(f"📋 Danh sách từ khóa ({len(rows)})", text)
        await interaction.response.send_message(embed=embed)

    # -------------------------------------------------------------
    # Listener: tự động phản hồi khi có từ khóa trong tin nhắn
    # -------------------------------------------------------------
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or message.guild is None:
            return

        content_lower = message.content.lower()
        rows = await self.db.get_all_keywords(message.guild.id)

        for row in rows:
            if row["keyword"] in content_lower:
                try:
                    await message.channel.send(row["response"])
                    await self.db.increment_keyword_usage(message.guild.id, row["keyword"])
                except discord.HTTPException as e:
                    logger.error(f"Không thể gửi phản hồi từ khóa: {e}")
                break  # chỉ phản hồi 1 từ khóa đầu tiên khớp để tránh spam


async def setup(bot: commands.Bot):
    await bot.add_cog(Keyword(bot))

