"""
helpers.py
Các hàm tiện ích dùng chung cho toàn bộ bot
"""

import json
import logging
from pathlib import Path

import discord
from datetime import datetime, timezone

logger = logging.getLogger("bot.helpers")


def _load_default_color() -> int:
    """Đọc 'embed_color' từ config.json (dạng '#RRGGBB') nếu có, để field này
    trong config.json thực sự có tác dụng thay vì bị bỏ quên. Nếu thiếu/lỗi,
    dùng màu blurple mặc định của Discord."""
    fallback = 0x5865F2
    try:
        config_path = Path(__file__).resolve().parent.parent / "config.json"
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        raw = config.get("embed_color")
        if raw:
            return int(str(raw).lstrip("#"), 16)
    except Exception as e:
        logger.warning(f"Không đọc được embed_color từ config.json, dùng màu mặc định: {e}")
    return fallback


# =====================================================================
# MÀU SẮC
# =====================================================================
# Màu chức năng (trạng thái) - dùng cho success/error/info/warning
COLOR_DEFAULT = _load_default_color()   # Lấy từ config.json["embed_color"], fallback blurple nếu thiếu
COLOR_SUCCESS = 0x57F287   # Xanh lá tươi
COLOR_ERROR = 0xED4245     # Đỏ
COLOR_INFO = 0x00B0F4      # Xanh dương nhạt
COLOR_WARNING = 0xFEE75C   # Vàng cảnh báo

# Màu rực rỡ theo TỪNG NHÓM CHỨC NĂNG - để mỗi mảng của bot có "cá tính" riêng
CATEGORY_COLORS = {
    "economy":   0xFFC300,  # 💰 Kinh tế - vàng kim
    "taixiu":    0xF39C12,  # 🎲 Tài Xỉu - cam rực
    "baucua":    0x9B59B6,  # 🎡 Bầu Cua - tím
    "coinflip":  0xE91E63,  # 🪙 Coinflip có cược - hồng magenta
    "fun":       0x1ABC9C,  # 🎉 Game vui (rollfun/flipfun) - xanh ngọc
    "keyword":   0x16A085,  # 🔑 Từ khóa - xanh lá đậm
    "wordchain": 0x3498DB,  # 🔤 Nối từ - xanh dương
    "settings":  0x5865F2,  # ⚙️ Cài đặt - blurple
    "info":      0x8E44AD,  # ℹ️ Thông tin - tím than
    "utility":   0x95A5A6,  # 🛠️ Tiện ích - bạc
}

BRAND_FOOTER = "✨ Loop Bot"


def get_category_color(category: str) -> int:
    """Lấy màu rực rỡ theo nhóm chức năng, trả về màu mặc định nếu không tìm thấy."""
    return CATEGORY_COLORS.get(category, COLOR_DEFAULT)


def check_admin(user: discord.Member) -> bool:
    """Kiểm tra thành viên có quyền Administrator hay không"""
    if isinstance(user, discord.Member):
        return user.guild_permissions.administrator
    return False


def make_embed(
    title: str,
    description: str = "",
    color: int = COLOR_DEFAULT,
    footer: str = BRAND_FOOTER,
    thumbnail_url: str = None,
) -> discord.Embed:
    """Tạo embed chuẩn có timestamp + footer thương hiệu.
    Truyền color=get_category_color("...") để dùng màu rực rỡ theo nhóm chức năng."""
    embed = discord.Embed(
        title=title,
        description=description,
        color=color,
        timestamp=datetime.now(timezone.utc),
    )
    if footer:
        embed.set_footer(text=footer)
    if thumbnail_url:
        embed.set_thumbnail(url=thumbnail_url)
    return embed


def success_embed(message: str, title: str = "✅ Thành công", footer: str = BRAND_FOOTER) -> discord.Embed:
    """Embed màu xanh báo thành công"""
    embed = discord.Embed(
        title=title,
        description=message,
        color=COLOR_SUCCESS,
        timestamp=datetime.now(timezone.utc),
    )
    if footer:
        embed.set_footer(text=footer)
    return embed


def error_embed(message: str, title: str = "❌ Lỗi", footer: str = BRAND_FOOTER) -> discord.Embed:
    """Embed màu đỏ báo lỗi"""
    embed = discord.Embed(
        title=title,
        description=message,
        color=COLOR_ERROR,
        timestamp=datetime.now(timezone.utc),
    )
    if footer:
        embed.set_footer(text=footer)
    return embed


def warning_embed(message: str, title: str = "⚠️ Lưu ý", footer: str = BRAND_FOOTER) -> discord.Embed:
    """Embed màu vàng cảnh báo (dùng cho các trường hợp không hẳn lỗi nhưng cần chú ý)"""
    embed = discord.Embed(
        title=title,
        description=message,
        color=COLOR_WARNING,
        timestamp=datetime.now(timezone.utc),
    )
    if footer:
        embed.set_footer(text=footer)
    return embed


def format_number(num: int) -> str:
    """Định dạng số có dấu phẩy ngăn cách hàng nghìn. VD: 1234567 -> 1,234,567"""
    return f"{num:,}"


def progress_bar(current: int, maximum: int, length: int = 10) -> str:
    """Tạo thanh tiến trình bằng ký tự khối, VD: ▰▰▰▰▰▱▱▱▱▱ 50%"""
    if maximum <= 0:
        ratio = 0
    else:
        ratio = max(0, min(1, current / maximum))
    filled = round(length * ratio)
    return "▰" * filled + "▱" * (length - filled) + f" {round(ratio * 100)}%"


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
