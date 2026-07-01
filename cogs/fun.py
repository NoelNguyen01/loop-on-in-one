import discord
from discord.ext import commands
from discord import app_commands
import random

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Lệnh slash /8ball
    @app_commands.command(name="8ball", description="🎱 Hỏi ý kiến bóng ma thuật")
    @app_commands.describe(question="Câu hỏi của bạn")
    async def slash_8ball(self, interaction: discord.Interaction, question: str):
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
        await interaction.response.send_message(embed=embed)

    # Lệnh slash /gay
    @app_commands.command(name="gay", description="🌈 Đoán độ gay của ai đó")
    @app_commands.describe(member="Người bạn muốn đoán")
    async def slash_gay(self, interaction: discord.Interaction, member: discord.Member = None):
        target = member or interaction.user
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
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Fun(bot))
