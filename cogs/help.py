"""
cogs/help.py
Lệnh trợ giúp hiển thị danh sách lệnh theo nhóm
"""

import discord
from discord import app_commands
from discord.ext import commands

from utils.helpers import make_embed, COLOR_DEFAULT

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
    "🔤 Nối từ": [
        (".ltt", "Bắt đầu ván nối từ (Anh/Việt) trong kênh"),
        (".ltp", "Dừng ván nối từ trong kênh"),
        (".ldm", "Xem bảng điểm ván nối từ hiện tại"),
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
        total_cmds = sum(len(v) for v in HELP_DATA.values())
        embed = make_embed(
            "📖 Danh sách lệnh",
            f"Bot có tổng cộng **{total_cmds}** lệnh, nhóm theo từng chức năng bên dưới 👇",
            color=COLOR_DEFAULT,
        )
        if self.bot.user:
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)

        for group, commands_list in HELP_DATA.items():
            value = "\n".join(f"`{cmd}` — {desc}" for cmd, desc in commands_list)
            embed.add_field(name=group, value=value, inline=False)

        embed.set_footer(text="💡 Đây là tên rút gọn hiển thị — vẫn gõ bằng lệnh slash (/) như bình thường trên Discord")
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Help(bot))
