import discord
from discord.ext import commands

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="reload")
    @commands.is_owner()
    async def reload_cog(self, ctx, cog_name: str):
        """🔄 Tải lại cog"""
        try:
            await self.bot.reload_extension(f"cogs.{cog_name}")
            await ctx.send(f"✅ Đã reload cog: `{cog_name}`")
        except Exception as e:
            await ctx.send(f"❌ Lỗi reload: {e}")

    @commands.command(name="shutdown")
    @commands.is_owner()
    async def shutdown(self, ctx):
        """🔴 Tắt bot"""
        await ctx.send("🔄 Đang tắt bot...")
        await self.bot.close()

async def setup(bot):
    await bot.add_cog(Admin(bot))
