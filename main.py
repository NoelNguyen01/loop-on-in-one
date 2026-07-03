import os
import logging
from dotenv import load_dotenv
import discord
from discord.ext import commands

# ==================== LOGGING ====================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ==================== LOAD ENV ====================
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
DEV_GUILD_ID = os.getenv('DEV_GUILD_ID')

if not TOKEN:
    logger.error("❌ Không tìm thấy DISCORD_TOKEN trong .env")
    exit(1)

# ==================== INTENTS ====================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = discord.Bot(intents=intents)

# ==================== COGS CẦN LOAD ====================
INITIAL_COGS = [
    "cogs.economy",    # Kinh tế: balance, daily, work, shop, give, rob, gamble
    "cogs.fun",        # Giải trí: avatar, ping, roll, flip, 8ball, poll
    "cogs.settings",   # Cài đặt: welcome, goodbye, log channel, đổi tên tiền tệ
    "cogs.help",       # Trợ giúp: /help
    
    # ======== ĐÃ LOẠI BỎ ========
    # "cogs.leveling",    # XP/Level
    # "cogs.moderation",  # warn, kick, ban, clear
    # "cogs.roles",       # role tự động
    # "cogs.automod",     # chống spam, link
    # "cogs.stats",       # thống kê
    # "cogs.admin",       # backup/restore
    # "cogs.social",      # kết hôn
]

# ==================== LOAD COGS ====================
for cog in INITIAL_COGS:
    try:
        bot.load_extension(cog)
        logger.info(f"✅ Đã load: {cog}")
    except Exception as e:
        logger.error(f"❌ Lỗi load {cog}: {e}")

# ==================== SỰ KIỆN ON_READY ====================
@bot.event
async def on_ready():
    logger.info(f"✅ Bot đã sẵn sàng! Tên: {bot.user}")
    logger.info(f"✅ Đã kết nối đến {len(bot.guilds)} server(s)")
    
    try:
        await bot.sync_commands()
        logger.info("✅ Đã đồng bộ slash commands")
    except Exception as e:
        logger.error(f"❌ Lỗi đồng bộ: {e}")

# ==================== XỬ LÝ LỖI COMMAND ====================
@bot.event
async def on_application_command_error(ctx, error):
    if isinstance(error, discord.errors.Forbidden):
        await ctx.respond("❌ Bot không có quyền thực hiện hành động này!", ephemeral=True)
    elif isinstance(error, discord.errors.HTTPException):
        await ctx.respond("❌ Lỗi kết nối, vui lòng thử lại!", ephemeral=True)
    else:
        logger.error(f"Lỗi: {error}")
        await ctx.respond(f"❌ Đã xảy ra lỗi: {error}", ephemeral=True)

# ==================== KHỞI CHẠY ====================
if __name__ == "__main__":
    try:
        bot.run(TOKEN)
    except discord.errors.LoginFailure:
        logger.error("❌ Token không hợp lệ!")
    except Exception as e:
        logger.error(f"❌ Lỗi khởi chạy: {e}")
