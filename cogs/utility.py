import discord
from discord.ext import commands
import random
import asyncio
from datetime import datetime

class Utility(commands.Cog):
    """🎯 Lệnh tiện ích"""
    
    def __init__(self, bot):
        self.bot = bot
        self.giveaways = {}

    @commands.command(name="poll", help="📊 Tạo bình chọn")
    async def poll(self, ctx, duration: int, *, question):
        """Tạo bình chọn với thời gian"""
        embed = discord.Embed(
            title="📊 Bình chọn",
            description=question,
            color=0x00D4FF
        )
        embed.add_field(name="⏰ Thời gian", value=f"{duration} giây", inline=True)
        embed.add_field(name="👤 Người tạo", value=ctx.author.mention, inline=True)
        embed.set_footer(text="👍 Đồng ý | 👎 Không đồng ý")
        
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("👍")
        await msg.add_reaction("👎")
        
        await asyncio.sleep(duration)
        
        msg = await ctx.channel.fetch_message(msg.id)
        thumbs_up = 0
        thumbs_down = 0
        
        for reaction in msg.reactions:
            if str(reaction.emoji) == "👍":
                thumbs_up = reaction.count - 1
            elif str(reaction.emoji) == "👎":
                thumbs_down = reaction.count - 1
        
        result_embed = discord.Embed(
            title="📊 Kết quả bình chọn",
            description=question,
            color=0x00D4FF
        )
        result_embed.add_field(name="👍 Đồng ý", value=thumbs_up, inline=True)
        result_embed.add_field(name="👎 Không đồng ý", value=thumbs_down, inline=True)
        result_embed.add_field(name="📊 Tổng", value=thumbs_up + thumbs_down, inline=True)
        await ctx.send(embed=result_embed)

    @commands.command(name="giveaway", help="🎁 Tạo giveaway")
    @commands.has_permissions(administrator=True)
    async def giveaway(self, ctx, duration: int, winners: int, *, prize):
        """Tạo giveaway với số người thắng"""
        embed = discord.Embed(
            title="🎁 GIVEAWAY",
            description=f"**Giải thưởng:** {prize}\n**Số người thắng:** {winners}",
            color=0xFFD700
        )
        embed.add_field(name="⏰ Thời gian", value=f"{duration} giây", inline=True)
        embed.add_field(name="👤 Người tổ chức", value=ctx.author.mention, inline=True)
        embed.set_footer(text="Nhấn 🎉 để tham gia!")
        
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("🎉")
        
        await asyncio.sleep(duration)
        
        msg = await ctx.channel.fetch_message(msg.id)
        users = []
        
        for reaction in msg.reactions:
            if str(reaction.emoji) == "🎉":
                async for user in reaction.users():
                    if not user.bot:
                        users.append(user)
        
        if len(users) == 0:
            await ctx.send("❌ Không có ai tham gia giveaway!")
            return
        
        winners_list = random.sample(users, min(winners, len(users)))
        winner_mentions = " ".join([w.mention for w in winners_list])
        
        winner_embed = discord.Embed(
            title="🎉 KẾT THÚC GIVEAWAY",
            description=f"**Giải thưởng:** {prize}",
            color=0xFFD700
        )
        winner_embed.add_field(name="🏆 Người thắng", value=winner_mentions, inline=False)
        await ctx.send(embed=winner_embed)

    @commands.command(name="remind", help="⏰ Đặt lời nhắc")
    async def remind(self, ctx, duration: int, *, message):
        """Đặt lời nhắc sau khoảng thời gian"""
        await ctx.send(f"⏰ Đã đặt lời nhắc trong {duration} giây!")
        await asyncio.sleep(duration)
        await ctx.send(f"🔔 **{ctx.author.mention}** Nhắc nhở: {message}")

    @commands.command(name="serverinfo", help="ℹ️ Thông tin server")
    async def serverinfo(self, ctx):
        """Hiển thị thông tin server"""
        guild = ctx.guild
        
        embed = discord.Embed(
            title=f"ℹ️ Thông tin {guild.name}",
            color=0x00D4FF
        )
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        embed.add_field(name="👑 Chủ sở hữu", value=guild.owner.mention, inline=True)
        embed.add_field(name="👥 Thành viên", value=guild.member_count, inline=True)
        embed.add_field(name="📅 Ngày tạo", value=guild.created_at.strftime("%d/%m/%Y %H:%M"), inline=True)
        embed.add_field(name="📢 Kênh thoại", value=len(guild.voice_channels), inline=True)
        embed.add_field(name="💬 Kênh văn bản", value=len(guild.text_channels), inline=True)
        embed.add_field(name="🎭 Vai trò", value=len(guild.roles), inline=True)
        
        await ctx.send(embed=embed)

    @commands.command(name="userinfo", help="👤 Thông tin thành viên")
    async def userinfo(self, ctx, member: discord.Member = None):
        """Hiển thị thông tin thành viên"""
        member = member or ctx.author
        
        embed = discord.Embed(
            title=f"👤 Thông tin {member.display_name}",
            color=0x00D4FF
        )
        
        if member.avatar:
            embed.set_thumbnail(url=member.avatar.url)
        
        embed.add_field(name="🆔 ID", value=member.id, inline=True)
        embed.add_field(name="📛 Tên", value=member.name, inline=True)
        embed.add_field(name="📝 Nickname", value=member.display_name or "Không có", inline=True)
        embed.add_field(name="📅 Ngày tham gia", value=member.joined_at.strftime("%d/%m/%Y %H:%M"), inline=True)
        embed.add_field(name="📅 Ngày tạo", value=member.created_at.strftime("%d/%m/%Y %H:%M"), inline=True)
        embed.add_field(name="🎭 Vai trò", value=len(member.roles) - 1, inline=True)
        
        if member.bot:
            embed.add_field(name="🤖", value="Đây là bot", inline=False)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Utility(bot))
