import discord
from discord.ext import commands

class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        
        # Chặn link nếu không phải admin
        if "http://" in message.content or "https://" in message.content:
            if not message.author.guild_permissions.administrator:
                await message.delete()
                await message.channel.send(f"🔗 {message.author.mention} Không được gửi link!")

async def setup(bot):
    await bot.add_cog(AutoMod(bot))
