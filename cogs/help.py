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
        (".ldl", "Điểm danh nhận thưởng mỗi ngày"),
        (".lblc", "Xem số dư của bạn hoặc người khác"),
        (".lt", "Bảng xếp hạng người giàu nhất"),
        (".lrfr", "Chuyển tiền cho người khác"),
        (".lw", "Làm việc kiếm tiền (cooldown 1 phút)"),
        (".lh", "Xem cửa hàng vật phẩm"),
        (".lb", "Mua vật phẩm từ cửa hàng"),
    ],
    "🎮 Giải trí & Game": [
        (".ltx", "Chơi Tài Xỉu có cược"),
        (".lbc", "Chơi Bầu Cua Tôm Cá có cược"),
        (".lcl", "Tung đồng xu có cược"),
        (".lrfn", "Tung xí ngầu vui (không cược)"),
        (".llf", "Tung đồng xu vui (không cược)"),
    ],
    "🔑 Từ khóa": [
        (".ls", "[Admin] Tạo từ khóa tự động phản hồi"),
        (".ld", "Xóa từ khóa (chủ tạo hoặc Admin)"),
        (".llt", "Xem danh sách từ khóa"),
    ],
    "⚙️ Cài đặt (Admin)": [
        (".lswcm", "Đặt kênh chào mừng"),
        (".lsgb", "Đặt kênh tạm biệt"),
        (".lsvcl", "Đặt kênh log voice"),
        (".lscrc", "Đổi tên đơn vị tiền tệ"),
    ],
    "ℹ️ Thông tin": [
        (".lsvrf", "Thông tin server"),
        (".lsrf", "Thông tin user"),
        (".lbtf", "Thông tin bot"),
    ],
    "🛠️ Tiện ích": [
        (".lp", "Kiểm tra độ trễ"),
        (".lvt", "Xem avatar"),
        (".lr", "Tung xí ngầu 1-6"),
        (".llp", "Tung đồng xu"),
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
