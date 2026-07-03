"""
cogs/help.py
Lệnh trợ giúp hiển thị danh sách lệnh theo nhóm
"""

import discord
from discord import app_commands
from discord.ext import commands

from utils.helpers import make_embed

HELP_DATA = {
    "💰 Kinh tế": [
        ("/daily", "Điểm danh nhận thưởng mỗi ngày"),
        ("/balance", "Xem số dư của bạn hoặc người khác"),
        ("/top", "Bảng xếp hạng người giàu nhất"),
        ("/transfer", "Chuyển tiền cho người khác"),
        ("/work", "Làm việc kiếm tiền (cooldown 1 phút)"),
        ("/shop", "Xem cửa hàng vật phẩm"),
        ("/buy", "Mua vật phẩm từ cửa hàng"),
    ],
    "🎮 Giải trí & Game": [
        ("/taixiu", "Chơi Tài Xỉu có cược"),
        ("/baucua", "Chơi Bầu Cua Tôm Cá có cược"),
        ("/coinflip", "Tung đồng xu có cược"),
        ("/rollfun", "Tung xí ngầu vui (không cược)"),
        ("/flipfun", "Tung đồng xu vui (không cược)"),
    ],
    "🔑 Từ khóa": [
        ("/setkeyword", "[Admin] Tạo từ khóa tự động phản hồi"),
        ("/delkeyword", "Xóa từ khóa (chủ tạo hoặc Admin)"),
        ("/listkeyword", "Xem danh sách từ khóa"),
    ],
    "⚙️ Cài đặt (Admin)": [
        ("/setwelcome", "Đặt kênh chào mừng"),
        ("/setgoodbye", "Đặt kênh tạm biệt"),
        ("/setvoicelog", "Đặt kênh log voice"),
        ("/setcurrency", "Đổi tên đơn vị tiền tệ"),
    ],
    "ℹ️ Thông tin": [
        ("/serverinfo", "Thông tin server"),
        ("/userinfo", "Thông tin user"),
        ("/botinfo", "Thông tin bot"),
    ],
    "🛠️ Tiện ích": [
        ("/ping", "Kiểm tra độ trễ"),
        ("/avatar", "Xem avatar"),
        ("/roll", "Tung xí ngầu 1-6"),
        ("/flip", "Tung đồng xu"),
    ],
}


class Help(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="help", description="Hiển thị danh sách tất cả lệnh của bot")
    async def help(self, interaction: discord.Interaction):
        embed = make_embed("📖 Danh sách lệnh", "Dưới đây là tất cả các lệnh được nhóm theo chức năng:")

        for group, commands_list in HELP_DATA.items():
            value = "\n".join(f"`{cmd}` — {desc}" for cmd, desc in commands_list)
            embed.add_field(name=group, value=value, inline=False)

        embed.set_footer(text="Dùng lệnh slash (/) để tương tác với bot")
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Help(bot))
