import io
import json
import discord
from discord import app_commands
from discord.ext import commands
 
from utils.helpers import make_embed, error_embed, success_embed, is_admin
 
 
class Admin(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
 
    @app_commands.command(name="backup", description="[Admin] Backup toàn bộ dữ liệu server ra file JSON")
    @is_admin()
    async def backup(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        gid = interaction.guild_id
        db = self.bot.db
 
        settings = dict(await db.get_guild_settings(gid))
 
        cur = await db.conn.execute("SELECT * FROM users WHERE guild_id=?", (gid,))
        users = [dict(r) for r in await cur.fetchall()]
 
        cur = await db.conn.execute("SELECT * FROM warnings WHERE guild_id=?", (gid,))
        warnings = [dict(r) for r in await cur.fetchall()]
 
        cur = await db.conn.execute("SELECT * FROM shop_items WHERE guild_id=?", (gid,))
        shop = [dict(r) for r in await cur.fetchall()]
 
        cur = await db.conn.execute("SELECT * FROM level_roles WHERE guild_id=?", (gid,))
        level_roles = [dict(r) for r in await cur.fetchall()]
 
        payload = {
            "guild_id": gid,
            "settings": settings,
            "users": users,
            "warnings": warnings,
            "shop_items": shop,
            "level_roles": level_roles,
        }
 
        buffer = io.BytesIO(json.dumps(payload, indent=2, ensure_ascii=False).encode("utf-8"))
        file = discord.File(buffer, filename=f"backup_{gid}.json")
        await interaction.followup.send(
            embed=success_embed("Đây là file backup dữ liệu server của bạn."),
            file=file,
            ephemeral=True,
        )
 
    @app_commands.command(name="restore", description="[Admin] Restore dữ liệu server từ file backup JSON")
    @is_admin()
    async def restore(self, interaction: discord.Interaction, file: discord.Attachment):
        if not file.filename.endswith(".json"):
            await interaction.response.send_message(embed=error_embed("Vui lòng đính kèm file .json hợp lệ."), ephemeral=True)
            return
 
        await interaction.response.defer(ephemeral=True)
        try:
            raw = await file.read()
            payload = json.loads(raw.decode("utf-8"))
        except Exception:
            await interaction.followup.send(embed=error_embed("File backup không hợp lệ hoặc bị hỏng."), ephemeral=True)
            return
 
        gid = interaction.guild_id
        db = self.bot.db
 
        # Xóa dữ liệu cũ của server trước khi restore
        await db.reset_guild(gid)
 
        settings = payload.get("settings", {})
        settings["guild_id"] = gid
        cols = ", ".join(settings.keys())
        placeholders = ", ".join(["?"] * len(settings))
        await db.conn.execute(
            f"INSERT INTO guild_settings ({cols}) VALUES ({placeholders})",
            tuple(settings.values()),
        )
 
        for user in payload.get("users", []):
            user["guild_id"] = gid
            cols = ", ".join(user.keys())
            placeholders = ", ".join(["?"] * len(user))
            await db.conn.execute(
                f"INSERT INTO users ({cols}) VALUES ({placeholders})", tuple(user.values())
            )
 
        for w in payload.get("warnings", []):
            w["guild_id"] = gid
            w.pop("id", None)
            cols = ", ".join(w.keys())
            placeholders = ", ".join(["?"] * len(w))
            await db.conn.execute(
                f"INSERT INTO warnings ({cols}) VALUES ({placeholders})", tuple(w.values())
            )
 
        for s in payload.get("shop_items", []):
            s["guild_id"] = gid
            cols = ", ".join(s.keys())
            placeholders = ", ".join(["?"] * len(s))
            await db.conn.execute(
                f"INSERT INTO shop_items ({cols}) VALUES ({placeholders})", tuple(s.values())
            )
 
        for lr in payload.get("level_roles", []):
            lr["guild_id"] = gid
            cols = ", ".join(lr.keys())
            placeholders = ", ".join(["?"] * len(lr))
            await db.conn.execute(
                f"INSERT INTO level_roles ({cols}) VALUES ({placeholders})", tuple(lr.values())
            )
 
        await db.conn.commit()
        await interaction.followup.send(embed=success_embed("Đã restore dữ liệu server thành công."), ephemeral=True)
 
    @app_commands.command(name="blacklist", description="[Admin] Cấm một người dùng sử dụng bot trong server này")
    @is_admin()
    async def blacklist(self, interaction: discord.Interaction, member: discord.Member):
        await self.bot.db.set_blacklist(interaction.guild_id, member.id, True)
        await interaction.response.send_message(embed=success_embed(f"Đã blacklist {member.mention}."))
 
    @app_commands.command(name="whitelist", description="[Admin] Gỡ blacklist cho một người dùng")
    @is_admin()
    async def whitelist(self, interaction: discord.Interaction, member: discord.Member):
        await self.bot.db.set_blacklist(interaction.guild_id, member.id, False)
        await interaction.response.send_message(embed=success_embed(f"Đã gỡ blacklist cho {member.mention}."))
 
 
async def setup(bot: commands.Bot):
    await bot.add_cog(Admin(bot))
