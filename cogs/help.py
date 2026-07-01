
import discord
from discord import app_commands
from discord.ext import commands

from utils.helpers import make_embed

CATEGORIES = {
    "🪙 Kinh tế": [
        "balance", "daily", "work", "shop", "additem", "buy", "sell",
        "give", "rob", "gamble", "leaderboard", "pay_all",
    ],
    "📊 Level / XP": [
        "rank", "leaderboard_xp", "reset_levels", "add_xp", "set_level",
        "level_role", "double_xp", "set_xp_rate", "ignore_channel",
    ],
    "🛡️ Moderation": [
        "warn", "warnings", "remove_warn", "mute", "unmute", "timeout",
        "kick", "ban", "unban", "clear", "slowmode",
    ],
    "🎮 Giải trí": [
        "avatar", "server_info", "user_info", "ping", "roll", "flip",
        "eightball", "quote", "suggest", "poll",
    ],
    "🎁 Role": ["give_role", "remove_role", "autorole", "mute_role"],
    "🔧 Log & Auto-Mod": ["set_log", "auto_mod", "anti_spam", "anti_link", "anti_mention"],
    "🎨 Cài đặt server": [
        "set_prefix", "set_currency", "set_welcome", "set_goodbye",
        "set_rank_channel", "reset_server",
    ],
    "📈 Thống kê": ["server_stats", "user_stats", "top_activity", "bot_info"],
    "🔐 Admin": ["backup", "restore", "blacklist", "whitelist"],
    "🧠 Đặc biệt": ["marry", "divorce", "profile"],
}


class Help(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="help", description="Xem danh sách toàn bộ lệnh của bot theo nhóm")
    async def help_cmd(self, interaction: discord.Interaction):
        embed = make_embed(
            "📖 Danh sách lệnh — loop-on-in-one",
            "Tất cả lệnh đều dùng dạng slash `/`. Gõ `/` để Discord tự gợi ý.",
        )
        for category, commands_list in CATEGORIES.items():
            embed.add_field(
                name=category,
                value=" • ".join(f"`/{c}`" for c in commands_list),
                inline=False,
            )
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Help(bot))
