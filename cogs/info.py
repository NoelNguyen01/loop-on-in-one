import discord
from discord.ext import commands

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="info", aliases=["about"])
    async def bot_info(self, ctx):
        """📖 Thông tin bot"""
        embed = discord.Embed(
            title="🔄 LOOP ON IN ONE",
            description="Bot Discord đa năng, tích hợp mọi tính năng quản trị trong một gói duy nhất.",
            color=0x00D4FF
        )
        embed.add_field(name="📌 Phiên bản", value="1.0.0", inline=True)
        embed.add_field(name="👨‍💻 Tác giả", value="NoelNguyen01", inline=True)
        embed.add_field(name="💡 Ý tưởng", value="Dyno + Mimu, nhưng trong một bot!", inline=False)
        embed.add_field(
            name="🔗 GitHub",
            value="[NoelNguyen01/loop-on-in-one](https://github.com/NoelNguyen01/loop-on-in-one)",
            inline=False
        )
        embed.set_footer(text="🔄 Loop On In One - Vòng lặp của mọi tính năng")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Info(bot))
