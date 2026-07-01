import discord
from discord.ext import commands

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = []

    @commands.command(name="play", help="🎵 Phát nhạc từ URL")
    async def play(self, ctx, url):
        """Phát một bài hát từ URL"""
        # Code to play music
        await ctx.send(f'Đang phát: {url}')

    @commands.command(name="pause", help="⏸️ Tạm dừng bài hát")
    async def pause(self, ctx):
        """Tạm dừng bài hát hiện tại"""
        # Code to pause music
        await ctx.send('⏸️ Bài hát đã được tạm dừng')

    @commands.command(name="skip", help="⏭️ Bỏ qua bài hát")
    async def skip(self, ctx):
        """Bỏ qua bài hát hiện tại"""
        # Code to skip music
        await ctx.send('⏭️ Đã bỏ qua bài hát')

    @commands.command(name="queue", help="📋 Hiển thị hàng đợi")
    async def queue(self, ctx):
        """Hiển thị hàng đợi bài hát"""
        if not self.queue:
            await ctx.send('📋 Hàng đợi trống!')
        else:
            queue_list = "\n".join([f"{i+1}. {song}" for i, song in enumerate(self.queue)])
            await ctx.send(f'📋 **Hàng đợi:**\n{queue_list}')

    @commands.command(name="stop", help="⏹️ Dừng phát nhạc")
    async def stop(self, ctx):
        """Dừng phát nhạc"""
        self.queue.clear()
        await ctx.send('⏹️ Đã dừng phát nhạc và xóa hàng đợi')

    @commands.command(name="add", help="➕ Thêm bài hát vào hàng đợi")
    async def add(self, ctx, url):
        """Thêm bài hát vào hàng đợi"""
        self.queue.append(url)
        await ctx.send(f'➕ Đã thêm vào hàng đợi: {url}')

async def setup(bot):
    await bot.add_cog(Music(bot))
