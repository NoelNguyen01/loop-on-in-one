import discord
from discord.ext import commands
import random
import aiohttp
import asyncio

class Fun(commands.Cog):
    """😂 Lệnh giải trí"""
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="gay", help="🌈 Đoán độ gay")
    async def gay(self, ctx, member: discord.Member = None):
        """Đoán độ gay của ai đó"""
        target = member or ctx.author
        percentage = random.randint(0, 100)
        
        embed = discord.Embed(
            title="🌈 Máy đo độ gay",
            color=0xFF69B4
        )
        embed.add_field(name="👤 Người", value=target.mention, inline=True)
        embed.add_field(name="💖 Độ gay", value=f"{percentage}%", inline=True)
        
        green = percentage // 10
        red = 10 - green
        bar = "🟩" * green + "🟥" * red
        embed.add_field(name="📊", value=bar, inline=False)
        
        if percentage >= 80:
            embed.set_footer(text="🌈 Siêu gay! Tuyệt vời!")
        elif percentage >= 50:
            embed.set_footer(text="🌈 Có vẻ hơi gay rồi đấy!")
        else:
            embed.set_footer(text="❓ Chưa có dấu hiệu gì!")
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Fun(bot))
