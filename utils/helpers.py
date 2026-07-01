import discord

def create_embed(title, description, color=0x00D4FF):
    """Tạo embed chuẩn cho bot"""
    embed = discord.Embed(
        title=title,
        description=description,
        color=color
    )
    embed.set_footer(text="🔄 LOOP ON IN ONE")
    return embed

def is_admin(member):
    """Kiểm tra quyền admin"""
    return member.guild_permissions.administrator

def format_time(seconds):
    """Chuyển đổi giây sang phút:giây"""
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    return f"{minutes:02d}:{remaining_seconds:02d}"
