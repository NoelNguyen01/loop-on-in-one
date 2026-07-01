import discord
from discord.ext import commands

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = []

    @commands.command()
    async def play(self, ctx, url):
        """Phát một bài hát từ URL"""
        # Code to play music
        await ctx.send(f'Đang phát: {url}')  

    @commands.command()
    async def pause(self, ctx):
        """Tạm dừng bài hát hiện tại"""
        # Code to pause music
        await ctx.send('Bài hát đã được tạm dừng')

    @commands.command()
    async def skip(self, ctx):
        """Bỏ qua bài hát hiện tại"""
        # Code to skip music
        await ctx.send('Đã bỏ qua bài hát')

    @commands.command()
    async def queue(self, ctx):
        """Hiển thị hàng đợi bài hát"""
        # Code to show the queue
        await ctx.send('Hàng đợi bài hát của bạn:')  

    @commands.command()
    async def stop(self, ctx):
        """Dừng phát nhạc"""
        # Code to stop music
        await ctx.send('Đã dừng phát nhạc')

# Đăng ký cogs
def setup(bot):
await bot.add_cog(Music(bot))
