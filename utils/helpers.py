"""
utils/helpers.py
-----------------
Các hàm tiện ích dùng chung cho toàn bộ bot: tạo embed, format số tiền,
kiểm tra quyền admin và quản lý cooldown thủ công cho slash command.
"""

import json
import time
import discord

# ---------------------------------------------------------------
# ĐỌC CONFIG
# ---------------------------------------------------------------
with open("config.json", "r", encoding="utf-8") as f:
    CONFIG = json.load(f)

EMBED_COLOR = int(CONFIG["embed_color"], 16)
SUCCESS_COLOR = int(CONFIG["success_color"], 16)
ERROR_COLOR = int(CONFIG["error_color"], 16)


# ---------------------------------------------------------------
# EMBED HELPERS
# ---------------------------------------------------------------
def make_embed(title: str, description: str = "", color: int = EMBED_COLOR) -> discord.Embed:
    embed = discord.Embed(title=title, description=description, color=color)
    return embed


def success_embed(title: str, description: str = "") -> discord.Embed:
    return make_embed(f"✅ {title}", description, SUCCESS_COLOR)


def error_embed(title: str, description: str = "") -> discord.Embed:
    return make_embed(f"❌ {title}", description, ERROR_COLOR)


def format_currency(amount: int, currency_name: str = "Xu") -> str:
    """Format số tiền có dấu chấm ngăn cách hàng nghìn, ví dụ: 10.000 Xu"""
    icon = CONFIG.get("currency_icon", "💰")
    return f"{icon} {amount:,.0f} {currency_name}".replace(",", ".")


# ---------------------------------------------------------------
# KIỂM TRA QUYỀN
# ---------------------------------------------------------------
def is_admin(member: discord.Member) -> bool:
    """Kiểm tra thành viên có quyền Administrator hay không."""
    if isinstance(member, discord.Member):
        return member.guild_permissions.administrator
    return False


async def check_admin_or_respond(ctx: discord.ApplicationContext) -> bool:
    """Trả về True nếu là admin, ngược lại tự động phản hồi lỗi và trả về False."""
    if not is_admin(ctx.author):
        await ctx.respond(
            embed=error_embed("Không đủ quyền", "Chỉ **Quản trị viên (Admin)** mới có thể dùng lệnh này."),
            ephemeral=True,
        )
        return False
    return True


# ---------------------------------------------------------------
# COOLDOWN THỦ CÔNG (an toàn cho mọi phiên bản py-cord)
# ---------------------------------------------------------------
class CooldownManager:
    """
    Quản lý cooldown theo (command_name, user_id) bằng bộ nhớ trong.
    Dùng cho các lệnh game/kinh tế để chống spam.
    """

    def __init__(self):
        self._last_used: dict[tuple[str, int], float] = {}

    def check(self, command_name: str, user_id: int, cooldown_seconds: float) -> float:
        """
        Kiểm tra cooldown. Trả về 0 nếu được phép dùng lệnh (và tự ghi nhận thời điểm dùng),
        hoặc trả về số giây còn lại nếu vẫn đang trong thời gian chờ.
        """
        key = (command_name, user_id)
        now = time.time()
        last = self._last_used.get(key, 0)
        elapsed = now - last
        if elapsed >= cooldown_seconds:
            self._last_used[key] = now
            return 0
        return round(cooldown_seconds - elapsed, 1)

    def reset(self, command_name: str, user_id: int):
        self._last_used.pop((command_name, user_id), None)


# Đối tượng cooldown dùng chung toàn bot
cooldowns = CooldownManager()
