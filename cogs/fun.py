import discord
from discord.ext import commands
import random
import aiohttp
import asyncio

class Fun(commands.Cog):
    """😂 Lệnh giải trí"""
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="meme", help="😂 Lấy meme ngẫu nhiên")
    async def meme(self, ctx):
        """Lấy meme từ Reddit"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://meme-api.com/gimme") as response:
                    if response.status == 200:
                        data = await response.json()
                        embed = discord.Embed(
                            title="😂 Meme cho bạn",
                            color=0xFF6B6B
                        )
                        embed.set_image(url=data["url"])
                        embed.set_footer(text=f"👍 {data['ups']} | u/{data['author']}")
                        await ctx.send(embed=embed)
                    else:
                        await ctx.send("❌ Không thể lấy meme lúc này!")
        except:
            await ctx.send("❌ Không thể lấy meme lúc này!")

    @commands.command(name="8ball", help="🎱 Hỏi ý kiến bóng ma thuật")
    async def eight_ball(self, ctx, *, question):
        """Trả lời câu hỏi ngẫu nhiên"""
        responses = [
            "Chắc chắn rồi! ✅", "Có thể là như vậy 🤔", "Đừng hy vọng quá ❌",
            "Chắc chắn không! ❌", "Hỏi lại sau nhé 🔮", "Rất có thể ✅",
            "Tương lai mờ mịt 🌫️", "Không đời nào! ❌", "Đồng ý! ✅",
            "Tôi không nghĩ vậy 🤷", "Hãy tin vào bản thân 💪",
            "Có thể, nhưng không chắc 😐", "Tất nhiên là có! 🌟"
        ]
        
        embed = discord.Embed(
            title="🎱 Bóng ma thuật",
            color=0x9B59B6
        )
        embed.add_field(name="❓ Câu hỏi", value=question, inline=False)
        embed.add_field(name="🎯 Câu trả lời", value=random.choice(responses), inline=False)
        embed.set_footer(text="LOOP ON IN ONE")
        await ctx.send(embed=embed)

    @commands.command(name="guess", help="🔢 Game đoán số (1-100)")
    async def guess(self, ctx):
        """Game đoán số từ 1 đến 100"""
        number = random.randint(1, 100)
        attempts = 0
        max_attempts = 10
        
        await ctx.send("🔢 Tôi đang nghĩ đến một số từ 1 đến 100. Bạn có 10 lần đoán!")
        
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        
        while attempts < max_attempts:
            try:
                msg = await self.bot.wait_for('message', timeout=30.0, check=check)
                guess = int(msg.content)
                attempts += 1
                
                if guess < number:
                    await ctx.send(f"📈 Cao hơn! (Còn {max_attempts - attempts} lần)")
                elif guess > number:
                    await ctx.send(f"📉 Thấp hơn! (Còn {max_attempts - attempts} lần)")
                else:
                    await ctx.send(f"🎉 Chúc mừng! Bạn đã đoán đúng số **{number}** trong {attempts} lần!")
                    return
            except ValueError:
                await ctx.send("⚠️ Vui lòng nhập số hợp lệ!")
            except asyncio.TimeoutError:
                await ctx.send(f"⏰ Hết thời gian! Đáp án là **{number}**")
                return
        
        await ctx.send(f"😢 Hết lượt! Đáp án là **{number}**")

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
        
        bar = "🟩" * (percentage //) 
