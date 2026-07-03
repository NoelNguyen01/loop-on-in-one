"""
cogs/economy.py
Hệ thống kinh tế: daily, balance, top, transfer, work, shop, buy, inventory
"""

import time
import random
import logging
from datetime import datetime, timezone

import discord
from discord import app_commands
from discord.ext import commands

from utils.helpers import make_embed, success_embed, error_embed, format_number, get_category_color, progress_bar

logger = logging.getLogger("bot.economy")
CAT_COLOR = get_category_color("economy")

# Cửa hàng mẫu (item_id: {name, price, description, stackable})
# stackable=False: vật phẩm kiểu "danh hiệu" - chỉ sở hữu 1 lần, mua lại sẽ bị chặn
# stackable=True: vật phẩm tiêu hao - có thể mua nhiều lần, cộng dồn số lượng
SHOP_ITEMS = {
    "vip": {"name": "🎖️ Thẻ VIP", "price": 5000, "description": "Danh hiệu VIP trong server", "stackable": False},
    "badge": {"name": "🏅 Huy hiệu đặc biệt", "price": 2000, "description": "Huy hiệu hiển thị trên profile", "stackable": False},
    "luck": {"name": "🍀 Bùa may mắn", "price": 1000, "description": "Tăng may mắn khi chơi game (chỉ mang tính giải trí)", "stackable": True},
}

SECONDS_IN_DAY = 86400


class Economy(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = bot.db
        self.config = bot.config

    def currency_name_sync_default(self):
        return self.config.get("default_currency", "coins")

    async def get_currency_name(self, guild_id: int) -> str:
        settings = await self.db.get_guild_settings(guild_id)
        return settings["currency_name"] or self.currency_name_sync_default()

    # -------------------------------------------------------------
    # /daily
    # -------------------------------------------------------------
    @app_commands.command(name="daily", description="Điểm danh nhận thưởng hằng ngày")
    async def daily(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        guild_id = interaction.guild_id
        user = await self.db.get_user(user_id, guild_id)

        now = int(time.time())
        last_daily = user["last_daily"] or 0
        streak = user["daily_streak"] or 0

        elapsed = now - last_daily

        if elapsed < SECONDS_IN_DAY:
            remaining = SECONDS_IN_DAY - elapsed
            hours = remaining // 3600
            minutes = (remaining % 3600) // 60
            await interaction.response.send_message(
                embed=error_embed(f"⏳ Bạn đã điểm danh hôm nay rồi! Quay lại sau **{hours} giờ {minutes} phút** nhé."),
                ephemeral=True,
            )
            return

        # Nếu điểm danh trong vòng 48h kể từ lần trước -> tăng streak, ngược lại reset
        if elapsed < SECONDS_IN_DAY * 2:
            streak += 1
        else:
            streak = 1

        base = random.randint(self.config["daily_min"], self.config["daily_max"])
        bonus = min(streak * 10, 500)  # thưởng thêm theo streak, tối đa 500
        total = base + bonus

        await self.db.update_balance(user_id, guild_id, total)
        await self.db.update_daily(user_id, guild_id, streak, now)

        currency = await self.get_currency_name(guild_id)
        streak_bar = progress_bar(min(streak, 50), 50)
        embed = success_embed(
            f"🎁 Bạn nhận được **{format_number(total)} {currency}**!\n"
            f"(Cơ bản: {format_number(base)} + Thưởng streak: {format_number(bonus)})\n"
            f"🔥 Chuỗi điểm danh: **{streak} ngày**\n"
            f"{streak_bar} (tối đa thưởng ở streak 50)",
            title="Điểm danh thành công",
        )
        await interaction.response.send_message(embed=embed)

    # -------------------------------------------------------------
    # /balance
    # -------------------------------------------------------------
    @app_commands.command(name="balance", description="Xem số dư của bạn hoặc người khác")
    @app_commands.describe(user="Người muốn xem số dư (bỏ trống để xem của bạn)")
    async def balance(self, interaction: discord.Interaction, user: discord.Member = None):
        target = user or interaction.user
        row = await self.db.get_user(target.id, interaction.guild_id)
        currency = await self.get_currency_name(interaction.guild_id)

        embed = make_embed(
            f"💰 Số dư của {target.display_name}",
            f"**{format_number(row['balance'])} {currency}**",
            color=CAT_COLOR,
        )
        embed.set_thumbnail(url=target.display_avatar.url)
        embed.add_field(name="🏆 Thắng", value=str(row["total_wins"]), inline=True)
        embed.add_field(name="💔 Thua", value=str(row["total_losses"]), inline=True)
        await interaction.response.send_message(embed=embed)

    # -------------------------------------------------------------
    # /top
    # -------------------------------------------------------------
    @app_commands.command(name="top", description="Bảng xếp hạng người giàu nhất server")
    async def top(self, interaction: discord.Interaction):
        rows = await self.db.get_top_balance(interaction.guild_id, limit=10)
        currency = await self.get_currency_name(interaction.guild_id)

        if not rows:
            await interaction.response.send_message(embed=error_embed("Chưa có dữ liệu xếp hạng."))
            return

        medals = ["🥇", "🥈", "🥉"]
        lines = []
        for idx, row in enumerate(rows):
            prefix = medals[idx] if idx < 3 else f"**#{idx + 1}**"
            member = interaction.guild.get_member(int(row["user_id"]))
            name = member.display_name if member else f"User {row['user_id']}"
            lines.append(f"{prefix} {name} — {format_number(row['balance'])} {currency}")

        embed = make_embed("🏆 Bảng xếp hạng", "\n".join(lines), color=CAT_COLOR)
        await interaction.response.send_message(embed=embed)

    # -------------------------------------------------------------
    # /transfer
    # -------------------------------------------------------------
    @app_commands.command(name="transfer", description="Chuyển tiền cho người khác")
    @app_commands.describe(user="Người nhận", amount="Số tiền muốn chuyển")
    @app_commands.checks.cooldown(1, 5, key=lambda i: (i.guild_id, i.user.id))
    async def transfer(self, interaction: discord.Interaction, user: discord.Member, amount: app_commands.Range[int, 1]):
        if user.id == interaction.user.id:
            await interaction.response.send_message(embed=error_embed("Bạn không thể chuyển tiền cho chính mình."), ephemeral=True)
            return
        if user.bot:
            await interaction.response.send_message(embed=error_embed("Không thể chuyển tiền cho bot."), ephemeral=True)
            return

        sender = await self.db.get_user(interaction.user.id, interaction.guild_id)
        if sender["balance"] < amount:
            await interaction.response.send_message(embed=error_embed("Số dư của bạn không đủ."), ephemeral=True)
            return

        await self.db.update_balance(interaction.user.id, interaction.guild_id, -amount)
        await self.db.update_balance(user.id, interaction.guild_id, amount)

        currency = await self.get_currency_name(interaction.guild_id)
        embed = success_embed(
            f"{interaction.user.mention} đã chuyển **{format_number(amount)} {currency}** cho {user.mention}."
        )
        await interaction.response.send_message(embed=embed)

    @transfer.error
    async def transfer_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(
                embed=error_embed(f"⏳ Vui lòng đợi **{error.retry_after:.1f} giây** trước khi chuyển tiền tiếp."),
                ephemeral=True,
            )
        else:
            raise error

    # -------------------------------------------------------------
    # /work
    # -------------------------------------------------------------
    @app_commands.command(name="work", description="Làm việc để kiếm tiền")
    @app_commands.checks.cooldown(1, 60, key=lambda i: (i.guild_id, i.user.id))
    async def work(self, interaction: discord.Interaction):
        jobs = [
            "sửa máy tính", "giao hàng", "dạy học", "viết code",
            "dọn dẹp server", "làm streamer", "bán đồ ăn vặt",
        ]
        job = random.choice(jobs)
        earned = random.randint(50, 300)

        await self.db.update_balance(interaction.user.id, interaction.guild_id, earned)
        currency = await self.get_currency_name(interaction.guild_id)

        embed = success_embed(
            f"Bạn đã làm công việc **{job}** và kiếm được **{format_number(earned)} {currency}**!",
            title="💼 Làm việc thành công",
        )
        await interaction.response.send_message(embed=embed)

    @work.error
    async def work_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(
                embed=error_embed(f"⏳ Bạn cần nghỉ ngơi! Thử lại sau **{error.retry_after:.0f} giây**."),
                ephemeral=True,
            )
        else:
            raise error

    # -------------------------------------------------------------
    # /shop
    # -------------------------------------------------------------
    @app_commands.command(name="shop", description="Xem cửa hàng vật phẩm")
    async def shop(self, interaction: discord.Interaction):
        currency = await self.get_currency_name(interaction.guild_id)
        embed = make_embed("🛒 Cửa hàng", f"Dùng `/buy <item>` để mua. Đơn vị tiền tệ: {currency}", color=CAT_COLOR)
        for item_id, item in SHOP_ITEMS.items():
            type_note = "🔂 Chỉ mua 1 lần" if not item["stackable"] else "🔁 Có thể mua nhiều lần"
            embed.add_field(
                name=f"{item['name']} — `{item_id}`",
                value=f"{item['description']}\nGiá: **{format_number(item['price'])} {currency}** · {type_note}",
                inline=False,
            )
        await interaction.response.send_message(embed=embed)

    # -------------------------------------------------------------
    # /buy
    # -------------------------------------------------------------
    @app_commands.command(name="buy", description="Mua vật phẩm từ cửa hàng")
    @app_commands.describe(item="Mã vật phẩm muốn mua")
    @app_commands.checks.cooldown(1, 5, key=lambda i: (i.guild_id, i.user.id))
    async def buy(self, interaction: discord.Interaction, item: str):
        item = item.lower()
        if item not in SHOP_ITEMS:
            await interaction.response.send_message(
                embed=error_embed("Vật phẩm không tồn tại. Dùng `/shop` để xem danh sách."),
                ephemeral=True,
            )
            return

        shop_item = SHOP_ITEMS[item]

        # Vật phẩm kiểu "danh hiệu" (không stackable) chỉ được sở hữu 1 lần
        if not shop_item["stackable"]:
            existing = await self.db.get_inventory_item(interaction.user.id, interaction.guild_id, item)
            if existing:
                await interaction.response.send_message(
                    embed=error_embed(f"Bạn đã sở hữu **{shop_item['name']}** rồi, không thể mua thêm."),
                    ephemeral=True,
                )
                return

        user_row = await self.db.get_user(interaction.user.id, interaction.guild_id)

        if user_row["balance"] < shop_item["price"]:
            await interaction.response.send_message(embed=error_embed("Số dư không đủ để mua vật phẩm này."), ephemeral=True)
            return

        await self.db.update_balance(interaction.user.id, interaction.guild_id, -shop_item["price"])
        await self.db.add_inventory_item(interaction.user.id, interaction.guild_id, item, 1, int(time.time()))
        currency = await self.get_currency_name(interaction.guild_id)

        embed = success_embed(
            f"Bạn đã mua thành công **{shop_item['name']}** với giá **{format_number(shop_item['price'])} {currency}**!\n"
            f"Dùng `/inventory` để xem túi đồ của bạn.",
            title="🛍️ Mua hàng thành công",
        )
        await interaction.response.send_message(embed=embed)

    @buy.error
    async def buy_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(
                embed=error_embed(f"⏳ Vui lòng đợi **{error.retry_after:.1f} giây** trước khi mua tiếp."),
                ephemeral=True,
            )
        else:
            raise error

    @buy.autocomplete("item")
    async def buy_autocomplete(self, interaction: discord.Interaction, current: str):
        return [
            app_commands.Choice(name=item["name"], value=item_id)
            for item_id, item in SHOP_ITEMS.items()
            if current.lower() in item_id or current.lower() in item["name"].lower()
        ][:25]

    # -------------------------------------------------------------
    # /inventory
    # -------------------------------------------------------------
    @app_commands.command(name="inventory", description="Xem túi đồ vật phẩm đã mua")
    @app_commands.describe(user="Người muốn xem túi đồ (bỏ trống để xem của bạn)")
    async def inventory(self, interaction: discord.Interaction, user: discord.Member = None):
        target = user or interaction.user
        rows = await self.db.get_inventory(target.id, interaction.guild_id)

        embed = make_embed(f"🎒 Túi đồ của {target.display_name}", color=CAT_COLOR)
        embed.set_thumbnail(url=target.display_avatar.url)

        if not rows:
            embed.description = "Chưa sở hữu vật phẩm nào. Dùng `/shop` để xem cửa hàng."
            await interaction.response.send_message(embed=embed)
            return

        for row in rows:
            item = SHOP_ITEMS.get(row["item_id"])
            name = item["name"] if item else f"❓ {row['item_id']} (đã ngừng bán)"
            qty_text = f" ×{row['quantity']}" if row["quantity"] > 1 else ""
            bought_dt = datetime.fromtimestamp(row["purchased_at"], tz=timezone.utc)
            embed.add_field(
                name=f"{name}{qty_text}",
                value=f"Mua lúc: {discord.utils.format_dt(bought_dt, 'R')}",
                inline=False,
            )

        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Economy(bot))
