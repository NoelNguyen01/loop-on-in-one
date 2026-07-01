

import asyncio
import json
import logging
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from database.db import Database

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("loop-on-in-one")

with open("config.json", "r", encoding="utf-8") as f:
    CONFIG = json.load(f)

INTENTS = discord.Intents.default()
INTENTS.members = True
INTENTS.message_content = True
INTENTS.voice_states = True

INITIAL_COGS = [
    "cogs.economy",
    "cogs.leveling",
    "cogs.moderation",
    "cogs.fun",
    "cogs.roles",
    "cogs.automod",
    "cogs.settings",
    "cogs.stats",
    "cogs.admin",
    "cogs.social",
    "cogs.help",
]


class LoopCommandTree(discord.app_commands.CommandTree):
    """CommandTree tùy chỉnh để chặn người dùng bị blacklist ở MỌI slash command."""

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.guild_id is None:
            return True
        bot: "LoopBot" = interaction.client  # type: ignore
        if await bot.db.is_blacklisted(interaction.guild_id, interaction.user.id):
            await interaction.response.send_message(
                "🚫 Bạn đã bị cấm sử dụng bot trong server này.", ephemeral=True
            )
            return False
        return True


class LoopBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned_or(CONFIG.get("default_prefix", "!")),
            intents=INTENTS,
            help_command=None,
            tree_cls=LoopCommandTree,
        )
        self.db = Database(CONFIG.get("database_path", "bot.db"))

    async def setup_hook(self):
        await self.db.connect()
        for cog in INITIAL_COGS:
            try:
                await self.load_extension(cog)
                logger.info("Đã tải cog: %s", cog)
            except Exception:
                logger.exception("Lỗi khi tải cog %s", cog)

        # Đồng bộ slash command.
        # Trong lúc phát triển, sync theo từng guild (GUILD_ID trong .env) để lệnh
        # cập nhật ngay lập tức. Khi lên production, sync global (có thể mất tới 1h).
        guild_id = os.getenv("DEV_GUILD_ID")
        if guild_id:
            guild = discord.Object(id=int(guild_id))
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
            logger.info("Đã sync slash command cho guild %s", guild_id)
        else:
            await self.tree.sync()
            logger.info("Đã sync slash command global")

    async def close(self):
        await self.db.close()
        await super().close()


bot = LoopBot()


@bot.event
async def on_ready():
    logger.info("Đăng nhập thành công: %s (ID: %s)", bot.user, bot.user.id)
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.watching, name="/help | loop-on-in-one")
    )


@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
    if isinstance(error, discord.app_commands.CheckFailure):
        if not interaction.response.is_done():
            await interaction.response.send_message(
                "❌ Bạn không có quyền hoặc không đủ điều kiện để dùng lệnh này.", ephemeral=True
            )
        return

    logger.exception("Lỗi khi xử lý lệnh %s", getattr(interaction.command, "name", "?"), exc_info=error)
    message = "⚠️ Đã xảy ra lỗi khi thực hiện lệnh này. Vui lòng thử lại sau."
    if interaction.response.is_done():
        await interaction.followup.send(message, ephemeral=True)
    else:
        await interaction.response.send_message(message, ephemeral=True)


async def main():
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise RuntimeError("Không tìm thấy DISCORD_TOKEN trong file .env")
    async with bot:
        await bot.start(token)


if __name__ == "__main__":
    asyncio.run(main())
