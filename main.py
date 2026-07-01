#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import json
import os
from dotenv import load_dotenv

# ==== 1. LOAD BIẾN MÔI TRƯỜNG ====
load_dotenv()  # Đọc file .env

# Đọc token từ biến môi trường
TOKEN = os.getenv("DISCORD_TOKEN")  # ← QUAN TRỌNG: Tên biến phải đúng

# ==== 2. KIỂM TRA TOKEN ====
if not TOKEN:
    print("=" * 60)
    print("❌ LỖI: KHÔNG TÌM THẤY DISCORD_TOKEN!")
    print("=" * 60)
    print("📝 Hãy tạo file .env với nội dung:")
    print("   DISCORD_TOKEN=your_token_here")
    print("   PREFIX=!")
    print("=" * 60)
    exit(1)  # Thoát nếu không có token

# ==== 3. ĐỌC CONFIG ====
try:
    with open("config.json", "r", encoding="utf-8") as f:
        config = json.load(f)
except FileNotFoundError:
    print("⚠️ Không tìm thấy config.json, dùng config mặc định")
    config = {
        "prefix": "!",
        "bot_name": "LOOP ON IN ONE",
        "embed_color": "#00D4FF",
        "version": "1.0.0"
    }

# ==== 4. KHỞI TẠO BOT ====
bot = commands.Bot(
    command_prefix=config.get("prefix", "!"),
    intents=discord.Intents.all(),
    help_command=None,
    activity=discord.Game(name="🔄 LOOP ON IN ONE | !help"),
    status=discord.Status.online
)

# ==== 5. SỰ KIỆN ON_READY ====
@bot.event
async def on_ready():
    print("=" * 60)
    print(f"✅ LOOP ON IN ONE đã hoạt động!")
    print(f"🤖 Tên: {bot.user.name}")
    print(f"🆔 ID: {bot.user.id}")
    print(f"📊 Prefix: {config.get('prefix', '!')}")
    print(f"📦 Số cog: {len(bot.cogs)}")
    print("=" * 60)

# ==== 6. LOAD COGS ====
async def load_cogs():
    if not os.path.exists("./cogs"):
        os.makedirs("./cogs")
        print("📁 Thư mục cogs đã được tạo!")
        return
    
    loaded = 0
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py") and not filename.startswith("__"):
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                print(f"✅ Đã load: {filename}")
                loaded += 1
            except Exception as e:
                print(f"❌ Lỗi load {filename}: {e}")
    
    if loaded == 0:
        print("⚠️ Không có cog nào được load!")
    else:
        print(f"📦 Đã load {loaded} cog(s)")

@bot.event
async def on_connect():
    await load_cogs()

# ==== 7. XỬ LÝ LỖI ====
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"❌ Lệnh không tồn tại. Gõ `{config.get('prefix', '!')}help` để xem danh sách.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Bạn không có quyền sử dụng lệnh này!")
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send("❌ Bot không có đủ quyền để thực hiện lệnh này!")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Thiếu tham số: `{error.param.name}`")
    else:
        await ctx.send(f"❌ Đã xảy ra lỗi: {str(error)}")
        print(f"Lỗi: {error}")

# ==== 8. CHẠY BOT ====
if __name__ == "__main__":
    try:
        print("🔄 Đang khởi động LOOP ON IN ONE...")
        bot.run(TOKEN)  # ← QUAN TRỌNG: Dùng biến TOKEN đã kiểm tra
    except discord.errors.LoginFailure:
        print("=" * 60)
        print("❌ LỖI ĐĂNG NHẬP: TOKEN KHÔNG HỢP LỆ!")
        print("=" * 60)
        print("📝 Hãy kiểm tra:")
        print("   1. Token đã được copy chính xác chưa?")
        print("   2. Token có còn hiệu lực không?")
        print("   3. Đã bật Privileged Gateway Intents trong Discord Developer Portal chưa?")
        print("=" * 60)
    except KeyboardInterrupt:
        print("\n🛑 Bot đã dừng bởi người dùng.")
    except Exception as e:
        print(f"❌ Lỗi không xác định: {e}")
