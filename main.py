#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import json
import os
from dotenv import load_dotenv

load_dotenv()  # Load biến từ .env

# Đọc config
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

# Khởi tạo bot
bot = commands.Bot(
    command_prefix=config.get("prefix", "!"),
    intents=discord.Intents.all(),
    help_command=None,
    activity=discord.Game(name="🔄 LOOP ON IN ONE | !help"),
    status=discord.Status.online
)

@bot.event
async def on_ready():
    print("=" * 50)
    print(f"🤖 {bot.user.name} đã hoạt động!")
    print(f"🆔 ID: {bot.user.id}")
    print(f"📊 Prefix: {config.get('prefix', '!')}")
    print(f"📦 Số cog: {len(bot.cogs)}")
    print("=" * 50)
    
    # Thông báo lên console
    await bot.change_presence(
        activity=discord.Game(name=f"🔄 LOOP ON IN ONE | {config.get('prefix', '!')}help"),
        status=discord.Status.online
    )

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"❌ Lệnh không tồn tại. Gõ `{config.get('prefix', '!')}help` để xem danh sách.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Bạn không có quyền sử dụng lệnh này!")
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send("❌ Bot không có đủ quyền để thực hiện lệnh này!")
    else:
        await ctx.send(f"❌ Đã xảy ra lỗi: {str(error)}")
        print(f"Lỗi: {error}")

@bot.command(name="ping")
async def ping(ctx):
    """🏓 Kiểm tra độ trễ của bot"""
    latency = round(bot.latency * 1000)
    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"Độ trễ: **{latency}ms**",
        color=0x00D4FF
    )
    embed.set_footer(text="LOOP ON IN ONE")
    await ctx.send(embed=embed)

@bot.command(name="reload")
@commands.is_owner()
async def reload_all(ctx):
    """🔄 Reload tất cả cogs (Chỉ Owner)"""
    await ctx.send("🔄 Đang reload tất cả cog...")
    for cog in list(bot.cogs.keys()):
        try:
            await bot.reload_extension(f"cogs.{cog.lower()}")
        except Exception as e:
            await ctx.send(f"❌ Lỗi reload {cog}: {e}")
    await ctx.send("✅ Đã reload xong!")

# Load cogs tự động
async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py") and not filename.startswith("__"):
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                print(f"✅ Loaded: {filename}")
            except Exception as e:
                print(f"❌ Failed to load {filename}: {e}")

@bot.event
async def on_connect():
    await load_cogs()

if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("❌ LỖI: Không tìm thấy DISCORD_TOKEN!")
        print("📝 Vui lòng tạo file .env và thêm DISCORD_TOKEN=your_token_here")
        exit(1)
    
    try:
        bot.run(token)
    except KeyboardInterrupt:
        print("\n🛑 Bot đã dừng bởi người dùng.")
    except Exception as e:
        print(f"❌ Lỗi khi chạy bot: {e}")
