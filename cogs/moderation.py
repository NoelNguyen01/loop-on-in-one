import discord
from discord.ext import commands
from discord import app_commands

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ban", description="⛔ Cấm thành viên vĩnh viễn")
    @app_commands.describe(member="Thành viên cần ban", reason="Lý do ban")
    @app_commands.checks.has_permissions(ban_members=True)
    async def slash_ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = "Không có lý do"):
        await member.ban(reason=reason)
        embed = discord.Embed(
            title="✅ Đã Ban",
            description=f"Đã ban {member.mention}",
            color=0xFF0000
        )
        embed.add_field(name="👤 Người thực hiện", value=interaction.user.mention, inline=True)
        embed.add_field(name="📝 Lý do", value=reason, inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="kick", description="🦶 Kick thành viên khỏi server")
    @app_commands.describe(member="Thành viên cần kick", reason="Lý do kick")
    @app_commands.checks.has_permissions(kick_members=True)
    async def slash_kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = "Không có lý do"):
        await member.kick(reason=reason)
        embed = discord.Embed(
            title="✅ Đã Kick",
            description=f"Đã kick {member.mention}",
            color=0xFF6B6B
        )
        embed.add_field(name="👤 Người thực hiện", value=interaction.user.mention, inline=True)
        embed.add_field(name="📝 Lý do", value=reason, inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="clear", description="🧹 Xóa tin nhắn hàng loạt")
    @app_commands.describe(amount="Số lượng tin nhắn cần xóa (1-1000)")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def slash_clear(self, interaction: discord.Interaction, amount: int = 100):
        if amount > 1000:
            amount = 1000
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.response.send_message(f"🧹 Đã xóa {len(deleted)} tin nhắn", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Moderation(bot))
