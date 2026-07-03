"""
main.py
File khởi động chính của Discord Bot
"""

import os
import sys
import json
import logging
import asyncio
from pathlib import Path

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

from database.db_manager import DBManager

# ---------------------------------------------------------------
# CẤU HÌNH LOGGING
# ---------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("bot.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("bot.main")

# ---------------------------------------------------------------
# NẠP BIẾN MÔI TRƯỜNG VÀ CONFIG
# ---------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"


def validate_env_or_exit():
    """Kiểm tra cấu hình .env ngay khi khởi động, gộp chung mọi trường hợp lỗi
    liên quan đến token vào MỘT chỗ duy nhất thay vì rải rác nhiều nơi."""
    if not ENV_PATH.exists():
        # Lỗi thường gặp: người dùng sửa token trực tiếp vào ".env.example" rồi chạy bot.
        # load_dotenv() CHỈ đọc file tên đúng là ".env", nên sửa ".env.example" sẽ
        # không có tác dụng gì - TOKEN vẫn luôn rỗng.
        logger.error(
            "Không tìm thấy file '.env' tại %s.\n"
            "  -> Hãy TẠO file '.env' (sao chép từ '.env.example'), KHÔNG sửa trực tiếp '.env.example'.\n"
            "     Ví dụ (Linux/macOS): cp .env.example .env\n"
            "     Ví dụ (Windows CMD): copy .env.example .env\n"
            "  -> Sau đó mở '.env' và điền DISCORD_TOKEN thật vào.",
            ENV_PATH,
        )
        sys.exit(1)

    load_dotenv(dotenv_path=ENV_PATH)
    token = os.getenv("DISCORD_TOKEN", "").strip()
    if not token:
        # File .env tồn tại nhưng DISCORD_TOKEN để trống hoặc chưa điền
        logger.error(
            "File '.env' tồn tại nhưng DISCORD_TOKEN đang trống.\n"
            "  -> Mở file '.env' và điền token thật lấy từ "
            "https://discord.com/developers/applications vào dòng DISCORD_TOKEN=..."
        )
        sys.exit(1)

    dev_guild_id = os.getenv("DEV_GUILD_ID", "").strip() or None
    return token, dev_guild_id


TOKEN, DEV_GUILD_ID = validate_env_or_exit()

with open(BASE_DIR / "config.json", "r", encoding="utf-8") as f:
    CONFIG = json.load(f)

# ---------------------------------------------------------------
# KHỞI TẠO INTENTS
# ---------------------------------------------------------------
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True


class LoopBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents, help_command=None)
        self.config = CONFIG
        self.db = DBManager("bot.db")

    async def setup_hook(self):
        """Chạy khi bot khởi động - kết nối DB và load cog"""
        await self.db.connect()

        cogs_to_load = [
            "cogs.economy",
            "cogs.fun",
            "cogs.help",
            "cogs.info",
            "cogs.keyword",
            "cogs.settings",
            "cogs.utility",
        ]

        for cog in cogs_to_load:
            try:
                await self.load_extension(cog)
                logger.info(f"Đã tải cog: {cog}")
            except Exception as e:
                logger.error(f"Lỗi khi tải cog {cog}: {e}", exc_info=True)

        # Đồng bộ slash command
        try:
            if DEV_GUILD_ID:
                guild = discord.Object(id=int(DEV_GUILD_ID))
                self.tree.copy_global_to(guild=guild)
                synced = await self.tree.sync(guild=guild)
                logger.info(f"Đã đồng bộ {len(synced)} slash command tới guild dev {DEV_GUILD_ID}")
            else:
                synced = await self.tree.sync()
                logger.info(f"Đã đồng bộ {len(synced)} slash command toàn cục")
        except Exception as e:
            logger.error(f"Lỗi khi đồng bộ slash command: {e}", exc_info=True)

    async def close(self):
        await self.db.close()
        await super().close()


bot = LoopBot()


@bot.event
async def on_ready():
    logger.info(f"Bot đã đăng nhập với tên: {bot.user} (ID: {bot.user.id})")
    logger.info(f"Đang phục vụ {len(bot.guilds)} server")
    activity = discord.Activity(type=discord.ActivityType.watching, name="/help")
    await bot.change_presence(activity=activity)


# ---------------------------------------------------------------
# XỬ LÝ LỖI TOÀN CỤC CHO SLASH COMMAND
# ---------------------------------------------------------------
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    from utils.helpers import error_embed

    if isinstance(error, app_commands.CommandOnCooldown):
        msg = f"⏳ Vui lòng đợi **{error.retry_after:.1f} giây** trước khi dùng lại lệnh này."
    elif isinstance(error, app_commands.MissingPermissions):
        msg = "🚫 Bạn không có quyền sử dụng lệnh này."
    elif isinstance(error, app_commands.CheckFailure):
        msg = "🚫 Bạn không đủ điều kiện để dùng lệnh này (có thể cần quyền Admin)."
    else:
        msg = "⚠️ Đã xảy ra lỗi khi thực hiện lệnh. Vui lòng thử lại sau."
        logger.error(f"Lỗi slash command '{interaction.command}': {error}", exc_info=True)

    embed = error_embed(msg)
    try:
        if interaction.response.is_done():
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message(embed=embed, ephemeral=True)
    except discord.HTTPException:
        pass


@bot.event
async def on_command_error(ctx, error):
    # Bot chủ yếu dùng slash command, prefix command chỉ để dự phòng
    if isinstance(error, commands.CommandNotFound):
        return
    logger.error(f"Lỗi prefix command: {error}", exc_info=True)


# ---------------------------------------------------------------
# CHẠY BOT
# ---------------------------------------------------------------
async def main():
    # TOKEN đã được kiểm tra hợp lệ ở validate_env_or_exit() ngay khi module này
    # được nạp (đầu file) - không cần kiểm tra lại ở đây nữa.
    async with bot:
        await bot.start(TOKEN)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot đã dừng bởi người dùng.")
