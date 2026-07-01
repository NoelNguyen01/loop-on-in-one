

import time
import discord
from discord import app_commands
from discord.ext import commands

from utils.helpers import make_embed, error_embed, success_embed

PROPOSAL_TIMEOUT = 5 * 60


class Social(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="marry", description="Cầu hôn một thành viên khác")
    async def marry(self, interaction: discord.Interaction, member: discord.Member):
        if member.bot or member.id == interaction.user.id:
            await interaction.response.send_message(embed=error_embed("Không thể cầu hôn đối tượng này."), ephemeral=True)
            return

        existing = await self.bot.db.get_marriage(interaction.guild_id, interaction.user.id)
        if existing:
            await interaction.response.send_message(
                embed=error_embed(f"Bạn đã kết hôn với <@{existing['partner_id']}> rồi."), ephemeral=True
            )
            return

        target_married = await self.bot.db.get_marriage(interaction.guild_id, member.id)
        if target_married:
            await interaction.response.send_message(embed=error_embed(f"{member.mention} đã kết hôn với người khác rồi."), ephemeral=True)
            return

        # Nếu đối phương đã cầu hôn mình trước đó → kết hôn ngay
        reverse = await self.bot.db.get_proposal(interaction.guild_id, member.id, interaction.user.id)
        if reverse:
            await self.bot.db.delete_proposal(interaction.guild_id, member.id, interaction.user.id)
            await self.bot.db.create_marriage(interaction.guild_id, interaction.user.id, member.id)
            await interaction.response.send_message(
                embed=success_embed(f"💍 {interaction.user.mention} và {member.mention} đã chính thức kết hôn!")
            )
            return

        await self.bot.db.add_proposal(interaction.guild_id, interaction.user.id, member.id)
        await interaction.response.send_message(
            embed=make_embed(
                "💌 Lời cầu hôn",
                f"{interaction.user.mention} vừa cầu hôn {member.mention}!\n"
                f"{member.mention}, gõ `/marry {interaction.user.display_name}` để đồng ý trong vòng 5 phút.",
            )
        )

    @app_commands.command(name="divorce", description="Ly hôn với người bạn đời hiện tại")
    async def divorce(self, interaction: discord.Interaction):
        marriage = await self.bot.db.get_marriage(interaction.guild_id, interaction.user.id)
        if not marriage:
            await interaction.response.send_message(embed=error_embed("Bạn hiện chưa kết hôn với ai."), ephemeral=True)
            return
        await self.bot.db.delete_marriage(interaction.guild_id, interaction.user.id, marriage["partner_id"])
        await interaction.response.send_message(
            embed=success_embed(f"💔 Bạn đã ly hôn với <@{marriage['partner_id']}>.")
        )

    @app_commands.command(name="profile", description="Xem hồ sơ tổng hợp (level, coin, hôn nhân...) của một thành viên")
    async def profile(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        user = await self.bot.db.get_user(interaction.guild_id, member.id)
        marriage = await self.bot.db.get_marriage(interaction.guild_id, member.id)
        settings = await self.bot.db.get_guild_settings(interaction.guild_id)

        embed = make_embed(f"🪪 Hồ sơ của {member.display_name}")
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="Level", value=str(user["level"]))
        embed.add_field(name="XP", value=f"{user['xp']:,}")
        embed.add_field(name="Số dư", value=f"{user['balance']:,} {settings['currency_name']}")
        embed.add_field(name="Tin nhắn", value=str(user["message_count"]))
        embed.add_field(
            name="Hôn nhân",
            value=f"💍 <@{marriage['partner_id']}>" if marriage else "Độc thân",
        )
        if member.joined_at:
            embed.set_footer(text=f"Tham gia server: {member.joined_at.strftime('%d/%m/%Y')}")
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Social(bot))
