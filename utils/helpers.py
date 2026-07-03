"""
helpers.py
Các hàm tiện ích dùng chung cho toàn bộ bot
"""

import discord
from datetime import datetime, timezone

# Màu embed chuẩn
COLOR_DEFAULT = 0x00FF00
COLOR_SUCCESS = 0x2ECC71
COLOR_ERROR = 0xE74C3C
COLOR_INFO = 0x3498DB


def check_admin(user: discord.Member) -> bool:
    """Kiểm tra thành viên có quyền Administrator hay không"""
    if isinstance(user, discord.Member):
        return user.guild_permissions.administrator
    return False


def make_embed(title: str, description: str = "", color: int = COLOR_DEFAULT) -> discord.Embed:
    """Tạo embed chuẩn có timestamp"""
    embed = discord.Embed(
        title=title,
        description=description,
        color=color,
        timestamp=datetime.now(timezone.utc),
    )
    return embed


def success_embed(message: str, title: str = "✅ Thành công") -> discord.Embed:
    """Embed màu xanh báo thành công"""
    embed = discord.Embed(
        title=title,
        description=message,
        color=COLOR_SUCCESS,
        timestamp=datetime.now(timezone.utc),
    )
    return embed


def error_embed(message: str, title: str = "❌ Lỗi") -> discord.Embed:
    """Embed màu đỏ báo lỗi"""
    embed = discord.Embed(
        title=title,
        description=message,
        color=COLOR_ERROR,
        timestamp=datetime.now(timezone.utc),
    )
    return embed


def format_number(num: int) -> str:
    """Định dạng số có dấu phẩy ngăn cách hàng nghìn. VD: 1234567 -> 1,234,567"""
    return f"{num:,}"


def parse_duration(seconds: int) -> str:
    """Chuyển giây sang định dạng dễ đọc: giờ/phút/giây"""
    seconds = int(seconds)
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)

    parts = []
    if hours > 0:
        parts.append(f"{hours} giờ")
    if minutes > 0:
        parts.append(f"{minutes} phút")
    if secs > 0 or not parts:
        parts.append(f"{secs} giây")

    return " ".join(parts)
