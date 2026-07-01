#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LOOP ON IN ONE - Discord Bot
Version: 1.0.0
Author: NoelNguyen01
"""

import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import json
import os
import sys
import asyncio
from dotenv import load_dotenv

# ==== LOAD ENVIRONMENT ====
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = os.getenv("PREFIX", "!")

# ==== CHECK TOKEN ====
if not TOKEN:
    print("=" * 60)
    print("❌ LỖI: KHÔNG TÌM THẤY DISCORD_TOKEN!")
    print("=" * 60)
    print("📝 Hãy tạo file .env với nội dung:")
    print("   DISCORD_TOKEN=your_token_here")
    print("   PREFIX=!")
    print("=" * 60)
    sys.exit(1)

# ==== LOAD CONFIG ====
try:
    with open("config.json", "r", encoding="utf-8") as f:
        config = json.load(f)
except FileNotFoundError:
    print("⚠️ Không tìm thấy config.json, dùng config mặc định")
    config = {
        "prefix": PREFIX,
        "bot_name": "LOOP ON IN ONE",
        "embed_color": "#00D4FF",
        "version": "1.0.0",
        "description": "Discord bot đa năng - Loop On In One"
    }

# ==== CUSTOM PREFIX FUNCTION ====
async def get_prefix(bot, message):
    """Lấy prefix từ config hoặc database"""
    if not message.guild:
        return PREFIX
    return PREFIX

# ==== INITIALIZE BOT ====
intents = discord.Intents.all()
bot = commands.Bot(
    command_prefix=get_prefix,
    intents=intents,
    help_command=None,
    activity=discord.Game(name=f"🔄 LOOP ON IN ONE | {PREFIX}help"),
    status=discord.Status.online
)

# ==== DATABASE MANAGER ====
class DatabaseManager:
    """Quản lý database đơn giản dùng JSON"""
    
    def __init__(self):
        self.data = {}
        self.load()
    
    def load(self):
        """Load dữ liệu từ file"""
        try:
            with open("database/data.json", "r", encoding="utf-8") as f:
                self.data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.data = {
                "users": {},
                "guilds": {},
                "warns": {},
                "economy": {},
                "levels": {}
            }
            self.save()
    
    def save(self):
        """Lưu dữ liệu ra file"""
        os.makedirs("database", exist_ok=True)
        with open("database/data.json", "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)
    
    def get_user(self, user_id):
        """Lấy dữ liệu user"""
        uid = str(user_id)
        if uid not in self.data["users"]:
            self.data["users"][uid] = {
                "balance": 0,
                "level": 0,
                "xp": 0,
                "daily": None,
                "warns": 0
            }
            self.save()
        return self.data["users"][uid]
    
    def get_guild(self, guild_id):
        """Lấy dữ liệu guild"""
        gid = str(guild_id)
        if gid not in self.data["guilds"]:
            self.data["guilds"][gid] = {
                "autorole": None,
                "welcome_channel": None,
                "log_channel": None,
                "prefix": PREFIX
            }
            self.save()
        return self.data["guilds"][gid]

# ==== INIT DATABASE ====
db = DatabaseManager()
bot.db = db

# ==== LOAD COGS ====
async def load_cogs():
    """Load tất cả cogs trong thư mục cogs"""
    if not os.path.exists("./cogs"):
        os.makedirs("./cogs")
        print("📁 Thư mục cogs đã được tạo!")
        return
    
    loaded = 0
    failed = 0
    
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py") and not filename.startswith("__"):
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                print(f"✅ Đã load: {filename}")
                loaded += 1
            except Exception as e:
                print(f"❌ Lỗi load {filename}: {e}")
                failed += 1
    
    print("=" * 50)
    print(f"📦 Đã load {loaded} cog(s)")
    if failed > 0:
        print(f"⚠️ Có {failed} cog(s) không load được")
    print("=" * 50)

# ==== SLASH COMMANDS (Lệnh /) ====
@bot.tree.command(name="ping", description="🏓 Kiểm tra độ trễ của bot")
async def slash_ping(interaction: discord.Interaction):
    """Lệnh slash /ping"""
    latency = round(bot.latency * 1000)
    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"Độ trễ: **{latency}ms**",
        color=0x00D4FF
    )
    embed.set_footer(text="LOOP ON IN ONE")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="info", description="📖 Thông tin về bot")
async def slash_info(interaction: discord.Interaction):
    """Lệnh slash /info"""
    # ===== LỆNH SLASH QUẢN TRỊ =====

@bot.tree.command(name="ban", description="⛔ Cấm người dùng")
@app_commands.describe(member="Thành viên cần ban", reason="Lý do ban")
@app_commands.checks.has_permissions(ban_members=True)
async def slash_ban(interaction: discord.Interaction, member: discord.Member, reason: str = "Không có lý do"):
    await member.ban(reason=reason)
    embed = discord.Embed(title="✅ Đã Ban", description=f"Đã ban {member.mention}", color=0xFF0000)
    embed.add_field(name="📝 Lý do", value=reason)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="kick", description="🦶 Đuổi người dùng")
@app_commands.describe(member="Thành viên cần kick", reason="Lý do kick")
@app_commands.checks.has_permissions(kick_members=True)
async def slash_kick(interaction: discord.Interaction, member: discord.Member, reason: str = "Không có lý do"):
    await member.kick(reason=reason)
    embed = discord.Embed(title="✅ Đã Kick", description=f"Đã kick {member.mention}", color=0xFF6B6B)
    embed.add_field(name="📝 Lý do", value=reason)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="clear", description="🧹 Xóa tin nhắn hàng loạt")
@app_commands.describe(amount="Số lượng tin nhắn (1-100)")
@app_commands.checks.has_permissions(manage_messages=True)
async def slash_clear(interaction: discord.Interaction, amount: int = 10):
    if amount > 100:
        amount = 100
    deleted = await interaction.channel.purge(limit=amount)
    await interaction.response.send_message(f"🧹 Đã xóa {len(deleted)} tin nhắn", ephemeral=True)

# ===== LỆNH SLASH TIỆN ÍCH =====

@bot.tree.command(name="gif", description="🎞️ Tìm ảnh động trên Web")
@app_commands.describe(query="Từ khóa tìm kiếm GIF")
async def slash_gif(interaction: discord.Interaction, query: str):
    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://api.giphy.com/v1/gifs/translate?api_key=YOUR_GIPHY_API_KEY&s={query}"
            async with session.get(url) as resp:
                data = await resp.json()
                gif_url = data['data']['images']['original']['url']
                embed = discord.Embed(title=f"🎞️ GIF: {query}", color=0x00D4FF)
                embed.set_image(url=gif_url)
                await interaction.response.send_message(embed=embed)
    except:
        await interaction.response.send_message("❌ Không tìm thấy GIF!")

@bot.tree.command(name="me", description="📝 Nhấn mạnh nội dung")
@app_commands.describe(content="Nội dung cần nhấn mạnh")
async def slash_me(interaction: discord.Interaction, content: str):
    embed = discord.Embed(description=f"**{interaction.user.display_name}** {content}", color=0x00D4FF)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="msg", description="💬 Nhắn tin cho người dùng")
@app_commands.describe(member="Người nhận", message="Nội dung tin nhắn")
@app_commands.checks.has_permissions(administrator=True)
async def slash_msg(interaction: discord.Interaction, member: discord.Member, message: str):
    try:
        await member.send(f"📩 Tin nhắn từ **{interaction.user.display_name}** ở **{interaction.guild.name}**:\n{message}")
        await interaction.response.send_message(f"✅ Đã gửi tin nhắn cho {member.mention}!", ephemeral=True)
    except:
        await interaction.response.send_message("❌ Không thể gửi tin nhắn!", ephemeral=True)

# ===== LỆNH SLASH GIẢI TRÍ =====

@bot.tree.command(name="meme", description="😂 Lấy meme ngẫu nhiên")
async def slash_meme(interaction: discord.Interaction):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://meme-api.com/gimme") as response:
                if response.status == 200:
                    data = await response.json()
                    embed = discord.Embed(title="😂 Meme cho bạn", color=0xFF6B6B)
                    embed.set_image(url=data["url"])
                    embed.set_footer(text=f"👍 {data['ups']} | u/{data['author']}")
                    await interaction.response.send_message(embed=embed)
                else:
                    await interaction.response.send_message("❌ Không thể lấy meme lúc này!")
    except:
        await interaction.response.send_message("❌ Không thể lấy meme lúc này!")

@bot.tree.command(name="8ball", description="🎱 Hỏi ý kiến bóng ma thuật")
@app_commands.describe(question="Câu hỏi của bạn")
async def slash_8ball(interaction: discord.Interaction, question: str):
    import random
    responses = [
        "Chắc chắn rồi! ✅", "Có thể là như vậy 🤔", "Đừng hy vọng quá ❌",
        "Chắc chắn không! ❌", "Hỏi lại sau nhé 🔮", "Rất có thể ✅",
        "Tương lai mờ mịt 🌫️", "Không đời nào! ❌", "Đồng ý! ✅",
        "Tôi không nghĩ vậy 🤷", "Hãy tin vào bản thân 💪",
        "Có thể, nhưng không chắc 😐", "Tất nhiên là có! 🌟"
    ]
    embed = discord.Embed(title="🎱 Bóng ma thuật", color=0x9B59B6)
    embed.add_field(name="❓ Câu hỏi", value=question, inline=False)
    embed.add_field(name="🎯 Câu trả lời", value=random.choice(responses), inline=False)
    embed.set_footer(text="LOOP ON IN ONE")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="guess", description="🔢 Game đoán số (1-100)")
async def slash_guess(interaction: discord.Interaction):
    import random
    number = random.randint(1, 100)
    await interaction.response.send_message(f"🔢 Tôi đang nghĩ đến một số từ 1 đến 100. Hãy đoán! Gõ `!guessnumber` để chơi!")

# ===== LỆNH SLASH THÔNG TIN =====

@bot.tree.command(name="serverinfo", description="ℹ️ Thông tin server")
async def slash_serverinfo(interaction: discord.Interaction):
    guild = interaction.guild
    embed = discord.Embed(title=f"ℹ️ Thông tin {guild.name}", color=0x00D4FF)
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    embed.add_field(name="👑 Chủ sở hữu", value=guild.owner.mention, inline=True)
    embed.add_field(name="👥 Thành viên", value=guild.member_count, inline=True)
    embed.add_field(name="📅 Ngày tạo", value=guild.created_at.strftime("%d/%m/%Y"), inline=True)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="userinfo", description="👤 Thông tin thành viên")
@app_commands.describe(member="Thành viên cần xem")
async def slash_userinfo(interaction: discord.Interaction, member: discord.Member = None):
    member = member or interaction.user
    embed = discord.Embed(title=f"👤 Thông tin {member.display_name}", color=0x00D4FF)
    if member.avatar:
        embed.set_thumbnail(url=member.avatar.url)
    embed.add_field(name="🆔 ID", value=member.id, inline=True)
    embed.add_field(name="📛 Tên", value=member.name, inline=True)
    embed.add_field(name="📅 Ngày tham gia", value=member.joined_at.strftime("%d/%m/%Y"), inline=True)
    await interaction.response.send_message(embed=embed)
    embed = discord.Embed(
        title="🔄 LOOP ON IN ONE",
        description="Bot Discord đa năng, tích hợp mọi tính năng quản trị trong một gói duy nhất.",
        color=0x00D4FF
    )
    embed.add_field(name="📌 Phiên bản", value=config.get("version", "1.0.0"), inline=True)
    embed.add_field(name="👨‍💻 Tác giả", value="NoelNguyen01", inline=True)
    embed.add_field(name="💡 Ý tưởng", value="Dyno + Mimu, nhưng trong một bot!", inline=False)
    embed.add_field(
        name="🔗 GitHub",
        value="[NoelNguyen01/loop-on-in-one](https://github.com/NoelNguyen01/loop-on-in-one)",
        inline=False
    )
    embed.set_footer(text="🔄 Loop On In One - Vòng lặp của mọi tính năng")
    await interaction.response.send_message(embed=embed)

# ==== EVENTS ====
@bot.event
async def on_ready():
    print("=" * 60)
    print(f"✅ {config['bot_name']} đã hoạt động!")
    print(f"🤖 Tên: {bot.user.name}")
    print(f"🆔 ID: {bot.user.id}")
    print(f"📊 Prefix: {PREFIX}")
    print(f"📦 Số cog: {len(bot.cogs)}")
    print(f"👥 Số server: {len(bot.guilds)}")
    print("=" * 60)
    
    # ==== ĐỒNG BỘ LỆNH SLASH ====
    try:
        synced = await bot.tree.sync()
        print(f"✅ Đã đồng bộ {len(synced)} lệnh slash!")
        for cmd in synced:
            print(f"   /{cmd.name}")
    except Exception as e:
        print(f"❌ Lỗi đồng bộ lệnh slash: {e}")
    
    # Cập nhật activity
    await bot.change_presence(
        activity=discord.Game(name=f"🔄 LOOP ON IN ONE | {PREFIX}help"),
        status=discord.Status.online
    )
@bot.event
async def on_connect():
    """Sự kiện khi kết nối thành công"""
    await load_cogs()

@bot.event
async def on_command_error(ctx, error):
    """Xử lý lỗi lệnh prefix (!)"""
    if isinstance(error, commands.CommandNotFound):
        embed = discord.Embed(
            title="❌ Lỗi",
            description=f"Lệnh không tồn tại. Gõ `{PREFIX}help` để xem danh sách.",
            color=0xFF0000
        )
        await ctx.send(embed=embed)
    
    elif isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title="❌ Lỗi",
            description="Bạn không có quyền sử dụng lệnh này!",
            color=0xFF0000
        )
        await ctx.send(embed=embed)
    
    elif isinstance(error, commands.BotMissingPermissions):
        embed = discord.Embed(
            title="❌ Lỗi",
            description="Bot không có đủ quyền để thực hiện lệnh này!",
            color=0xFF0000
        )
        await ctx.send(embed=embed)
    
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            title="❌ Lỗi",
            description=f"Thiếu tham số: `{error.param.name}`",
            color=0xFF0000
        )
        await ctx.send(embed=embed)
    
    elif isinstance(error, commands.CommandOnCooldown):
        embed = discord.Embed(
            title="⏰ Chậm lại",
            description=f"Vui lòng đợi {error.retry_after:.1f} giây trước khi dùng lệnh này!",
            color=0xFFA500
        )
        await ctx.send(embed=embed)
    
    else:
        embed = discord.Embed(
            title="❌ Lỗi",
            description=f"Đã xảy ra lỗi: {str(error)}",
            color=0xFF0000
        )
        await ctx.send(embed=embed)
        print(f"Lỗi: {error}")

@bot.event
async def on_member_join(member):
    """Sự kiện khi thành viên mới vào server"""
    guild_data = db.get_guild(member.guild.id)
    if guild_data.get("autorole"):
        role = member.guild.get_role(guild_data["autorole"])
        if role:
            await member.add_roles(role)
    
    channel_name = guild_data.get("welcome_channel", "welcome")
    channel = discord.utils.get(member.guild.text_channels, name=channel_name)
    
    if channel:
        embed = discord.Embed(
            title="👋 Chào mừng!",
            description=f"Chào mừng {member.mention} đến với **{member.guild.name}**!",
            color=0x00FF00
        )
        if member.avatar:
            embed.set_thumbnail(url=member.avatar.url)
        embed.add_field(name="📅 Ngày tham gia", value=member.joined_at.strftime("%d/%m/%Y %H:%M"))
        embed.set_footer(text=f"🎉 Chúng tôi hiện có {member.guild.member_count} thành viên")
        await channel.send(embed=embed)

@bot.event
async def on_member_remove(member):
    """Sự kiện khi thành viên rời server"""
    channel_name = "welcome"
    channel = discord.utils.get(member.guild.text_channels, name=channel_name)
    
    if channel:
        embed = discord.Embed(
            title="👋 Tạm biệt!",
            description=f"{member.mention} đã rời khỏi server.",
            color=0xFF0000
        )
        if member.avatar:
            embed.set_thumbnail(url=member.avatar.url)
        embed.set_footer(text=f"📊 Hiện còn {member.guild.member_count} thành viên")
        await channel.send(embed=embed)

# ==== BASIC COMMANDS (Prefix !) ====
@bot.command(name="ping")
async def ping(ctx):
    """🏓 Kiểm tra độ trễ"""
    latency = round(bot.latency * 1000)
    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"Độ trễ: **{latency}ms**",
        color=0x00D4FF
    )
    embed.set_footer(text="LOOP ON IN ONE")
    await ctx.send(embed=embed)

@bot.command(name="help")
async def help_command(ctx, *, command_name: str = None):
    """📖 Hiển thị danh sách lệnh"""
    embed = discord.Embed(
        title="📖 LOOP ON IN ONE - Hướng dẫn sử dụng",
        description="Dưới đây là danh sách các lệnh có sẵn:",
        color=0x00D4FF
    )
    
    if command_name:
        for cmd in bot.commands:
            if cmd.name == command_name.lower() or command_name.lower() in cmd.aliases:
                embed.add_field(
                    name=f"`{PREFIX}{cmd.name}`",
                    value=cmd.help or "Không có mô tả",
                    inline=False
                )
                break
        else:
            embed.description = f"Không tìm thấy lệnh `{command_name}`"
    else:
        categories = {
            "🛡️ Quản trị": ["kick", "ban", "warn", "clear", "slowmode", "lock", "unlock"],
            "🎯 Tiện ích": ["poll", "giveaway", "remind", "serverinfo", "userinfo"],
            "😂 Giải trí": ["meme", "8ball", "guess", "gay"],
            "💰 Kinh tế": ["balance", "daily", "give", "shop", "work"],
            "🤖 Tự động": ["addbadword", "removebadword", "autorole"],
            "⚙️ Admin": ["reload", "load", "unload", "setprefix", "shutdown"],
            "📖 Thông tin": ["ping", "info", "help"]
        }
        
        for category, commands_list in categories.items():
            cmd_list = []
            for cmd_name in commands_list:
                cmd = bot.get_command(cmd_name)
                if cmd:
                    cmd_list.append(f"`{PREFIX}{cmd_name}`")
            if cmd_list:
                embed.add_field(
                    name=category,
                    value=" ".join(cmd_list),
                    inline=False
                )
    
    embed.set_footer(text=f"🔹 Prefix hiện tại: {PREFIX} | Gõ {PREFIX}help <lệnh> để xem chi tiết")
    await ctx.send(embed=embed)

# ==== RUN BOT ====
if __name__ == "__main__":
    try:
        print("🔄 Đang khởi động LOOP ON IN ONE...")
        bot.run(TOKEN)
    except discord.errors.LoginFailure:
        print("=" * 60)
        print("❌ LỖI ĐĂNG NHẬP: TOKEN KHÔNG HỢP LỆ!")
        print("=" * 60)
        print("📝 Kiểm tra:")
        print("   1. Token đã được copy chính xác chưa?")
        print("   2. Token có còn hiệu lực không?")
        print("   3. Đã bật Privileged Gateway Intents chưa?")
        print("=" * 60)
    except KeyboardInterrupt:
        print("\n🛑 Bot đã dừng bởi người dùng.")
    except Exception as e:
        print(f"❌ Lỗi không xác định: {e}") 
