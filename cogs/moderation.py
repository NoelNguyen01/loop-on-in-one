import discord
from discord.ext import commands
from discord import app_commands
import asyncio

class Moderation(commands.Cog):
    """🛡️ Lệnh quản trị server"""
    
    def __init__(self, bot):
        self.bot = bot

    # ===== LỆNH PREFIX (!) =====
    
    @commands.command(name="warn", help="⚠️ Cảnh cáo thành viên")
    @commands.has_permissions(administrator=True)
    async def warn(self, ctx, member: discord.Member, *, reason="Không có lý do"):
        """Cảnh cáo thành viên"""
        user_data = self.bot.db.get_user(member.id)
        user_data["warns"] = user_data.get("warns", 0) + 1
        self.bot.db.save()
        
        embed = discord.Embed(
            title="⚠️ Cảnh cáo",
            description=f"{member.mention} đã bị cảnh cáo",
            color=0xFFA500
        )
        embed.add_field(name="📝 Lý do", value=reason, inline=False)
        embed.add_field(name="📊 Số lần", value=f"{user_data['warns']}/{self.bot.config.get('max_warns', 5)}", inline=True)
        embed.add_field(name="👤 Người thực hiện", value=ctx.author.mention, inline=True)
        await ctx.send(embed=embed)
        
        if user_data["warns"] >= self.bot.config.get('max_warns', 5):
            await member.ban(reason="Tự động ban - Quá số lần cảnh cáo tối đa")
            await ctx.send(f"🔨 {member.mention} đã bị tự động ban vì quá {self.bot.config.get('max_warns', 5)} lần cảnh cáo!")

    @commands.command(name="slowmode", help="🐢 Đặt chế độ chậm cho kênh")
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx, seconds: int = 0):
        """Đặt chế độ chậm"""
        if seconds > 21600:
            seconds = 21600
        
        await ctx.channel.edit(slowmode_delay=seconds)
        
        if seconds == 0:
            await ctx.send("🐢 Đã tắt chế độ chậm")
        else:
            await ctx.send(f"🐢 Đã đặt chế độ chậm: {seconds} giây")

    @commands.command(name="lock", help="🔒 Khóa kênh")
    @commands.has_permissions(administrator=True)
    async def lock(self, ctx, channel: discord.TextChannel = None):
        """Khóa kênh"""
        channel = channel or ctx.channel
        await channel.set_permissions(ctx.guild.default_role, send_messages=False)
        await ctx.send(f"🔒 Đã khóa kênh {channel.mention}")

    @commands.command(name="unlock", help="🔓 Mở khóa kênh")
    @commands.has_permissions(administrator=True)
    async def unlock(self, ctx, channel: discord.TextChannel = None):
        """Mở khóa kênh"""
        channel = channel or ctx.channel
        await channel.set_permissions(ctx.guild.default_role, send_messages=None)
        await ctx.send(f"🔓 Đã mở khóa kênh {channel.mention}")

    @commands.command(name="clear", help="🧹 Xóa tin nhắn hàng loạt")
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int = 100):
        """Xóa tin nhắn trong kênh"""
        if amount > 1000:
            amount = 1000
        
        deleted = await ctx.channel.purge(limit=amount + 1)
        
        msg = await ctx.send(f"🧹 Đã xóa {len(deleted)-1} tin nhắn")
        await asyncio.sleep(3)
        await msg.delete()

async def setup(bot):
    await bot.add_cog(Moderation(bot))
