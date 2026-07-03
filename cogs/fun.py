import random
import asyncio
import logging
 
import discord
from discord import app_commands
from discord.ext import commands
 
from utils.helpers import make_embed, success_embed, error_embed, format_number, get_category_color

logger = logging.getLogger("bot.fun")
COLOR_TAIXIU = get_category_color("taixiu")
COLOR_BAUCUA = get_category_color("baucua")
COLOR_COINFLIP = get_category_color("coinflip")
COLOR_FUN = get_category_color("fun")
 
DICE_EMOJIS = ["⚀", "⚁", "⚂", "⚃", "⚄", "⚅"]
BAUCUA_ANIMALS = {
    "bau": "🎃",   # Bầu
    "cua": "🦀",   # Cua
    "tom": "🦐",   # Tôm
    "ca": "🐟",    # Cá
    "ga": "🐓",    # Gà
    "nai": "🦌",   # Nai
}
BAUCUA_NAMES_VI = {
    "bau": "Bầu", "cua": "Cua", "tom": "Tôm",
    "ca": "Cá", "ga": "Gà", "nai": "Nai",
}
 
 
# =====================================================================
# TÀI XỈU
# =====================================================================
class TaiXiuBetModal(discord.ui.Modal, title="Đặt cược Tài Xỉu"):
    amount = discord.ui.TextInput(label="Số tiền cược", placeholder="Nhập số tiền...", required=True)
 
    def __init__(self, cog: "Fun", choice: str):
        super().__init__()
        self.cog = cog
        self.choice = choice  # "tai" hoặc "xiu"
 
    async def on_submit(self, interaction: discord.Interaction):
        try:
            amount = int(self.amount.value)
        except ValueError:
            await interaction.response.send_message(embed=error_embed("Số tiền không hợp lệ."), ephemeral=True)
            return
 
        min_bet = self.cog.config["min_bet"]
        max_bet = self.cog.config["max_bet"]
        if amount < min_bet or amount > max_bet:
            await interaction.response.send_message(
                embed=error_embed(f"Số tiền cược phải từ **{format_number(min_bet)}** đến **{format_number(max_bet)}**."),
                ephemeral=True,
            )
            return
 
        user_row = await self.cog.db.get_user(interaction.user.id, interaction.guild_id)
        if user_row["balance"] < amount:
            await interaction.response.send_message(embed=error_embed("Số dư không đủ để đặt cược."), ephemeral=True)
            return
 
        await self.cog.db.update_balance(interaction.user.id, interaction.guild_id, -amount)
        await self.cog.run_taixiu(interaction, self.choice, amount)
 
 
class TaiXiuView(discord.ui.View):
    def __init__(self, cog: "Fun"):
        super().__init__(timeout=30)
        self.cog = cog
 
    @discord.ui.button(label="TÀI (11-17)", style=discord.ButtonStyle.danger, emoji="🔺")
    async def tai_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(TaiXiuBetModal(self.cog, "tai"))
 
    @discord.ui.button(label="XỈU (4-10)", style=discord.ButtonStyle.primary, emoji="🔻")
    async def xiu_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(TaiXiuBetModal(self.cog, "xiu"))
 
 
# =====================================================================
# BẦU CUA
# =====================================================================
class BauCuaSelect(discord.ui.Select):
    def __init__(self, cog: "Fun"):
        options = [
            discord.SelectOption(label=BAUCUA_NAMES_VI[k], emoji=v, value=k)
            for k, v in BAUCUA_ANIMALS.items()
        ]
        super().__init__(placeholder="Chọn con vật muốn cược (có thể chọn nhiều)", min_values=1, max_values=6, options=options)
        self.cog = cog
 
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(BauCuaBetModal(self.cog, self.values))
 
 
class BauCuaBetModal(discord.ui.Modal, title="Đặt cược Bầu Cua"):
    amount = discord.ui.TextInput(label="Số tiền cược MỖI con", placeholder="Nhập số tiền...", required=True)
 
    def __init__(self, cog: "Fun", choices: list):
        super().__init__()
        self.cog = cog
        self.choices = choices
 
    async def on_submit(self, interaction: discord.Interaction):
        try:
            amount = int(self.amount.value)
        except ValueError:
            await interaction.response.send_message(embed=error_embed("Số tiền không hợp lệ."), ephemeral=True)
            return
 
        min_bet = self.cog.config["min_bet"]
        max_bet = self.cog.config["max_bet"]
        total_cost = amount * len(self.choices)
 
        if amount < min_bet or amount > max_bet:
            await interaction.response.send_message(
                embed=error_embed(f"Số tiền cược mỗi con phải từ **{format_number(min_bet)}** đến **{format_number(max_bet)}**."),
                ephemeral=True,
            )
            return

        # Giới hạn max_bet áp cho TỔNG tiền cược, không chỉ tiền cược mỗi con,
        # để tránh lách luật bằng cách chọn nhiều con cùng lúc.
        if total_cost > max_bet:
            await interaction.response.send_message(
                embed=error_embed(
                    f"Tổng tiền cược (**{format_number(amount)}** × {len(self.choices)} con = "
                    f"**{format_number(total_cost)}**) vượt quá mức cược tối đa **{format_number(max_bet)}**. "
                    f"Hãy chọn ít con hơn hoặc cược ít tiền hơn mỗi con."
                ),
                ephemeral=True,
            )
            return

        user_row = await self.cog.db.get_user(interaction.user.id, interaction.guild_id)
        if user_row["balance"] < total_cost:
            await interaction.response.send_message(
                embed=error_embed(f"Số dư không đủ. Cần **{format_number(total_cost)}** cho {len(self.choices)} con."),
                ephemeral=True,
            )
            return
 
        await self.cog.db.update_balance(interaction.user.id, interaction.guild_id, -total_cost)
        await self.cog.run_baucua(interaction, self.choices, amount)
 
 
class BauCuaView(discord.ui.View):
    def __init__(self, cog: "Fun"):
        super().__init__(timeout=30)
        self.add_item(BauCuaSelect(cog))
 
 
# =====================================================================
# COG CHÍNH
# =====================================================================
class Fun(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = bot.db
        self.config = bot.config
 
    async def get_currency_name(self, guild_id: int) -> str:
        settings = await self.db.get_guild_settings(guild_id)
        return settings["currency_name"] or self.config.get("default_currency", "coins")
 
    # -------------------------------------------------------------
    # /ping /roll /flip cơ bản (không cược)
    # -------------------------------------------------------------
    @app_commands.command(name="rollfun", description="Tung xí ngầu vui (không cược)")
    async def rollfun(self, interaction: discord.Interaction):
        result = random.randint(1, 6)
        embed = make_embed("🎲 Kết quả xúc xắc", f"{DICE_EMOJIS[result - 1]} Bạn đổ ra số **{result}**!", color=COLOR_FUN)
        await interaction.response.send_message(embed=embed)
 
    @app_commands.command(name="flipfun", description="Tung đồng xu vui (không cược)")
    async def flipfun(self, interaction: discord.Interaction):
        result = random.choice(["Sấp", "Ngửa"])
        embed = make_embed("🪙 Kết quả tung đồng xu", f"Đồng xu ra mặt: **{result}**!", color=COLOR_FUN)
        await interaction.response.send_message(embed=embed)
 
    # -------------------------------------------------------------
    # /taixiu
    # -------------------------------------------------------------
    @app_commands.command(name="taixiu", description="Chơi Tài Xỉu - đặt cược và đoán kết quả")
    @app_commands.checks.cooldown(1, 5, key=lambda i: (i.guild_id, i.user.id))
    async def taixiu(self, interaction: discord.Interaction):
        embed = make_embed(
            "🎲 TÀI XỈU",
            "Chọn **TÀI** (tổng 11-17) hoặc **XỈU** (tổng 4-10) rồi nhập số tiền cược.\n"
            f"Mức cược: {format_number(self.config['min_bet'])} - {format_number(self.config['max_bet'])}",
            color=COLOR_TAIXIU,
        )
        await interaction.response.send_message(embed=embed, view=TaiXiuView(self))
 
    async def run_taixiu(self, interaction: discord.Interaction, choice: str, amount: int):
        countdown_embed = make_embed("🎲 Đang lắc xí ngầu...", "🎰 Kết quả sẽ có sau giây lát!", color=COLOR_TAIXIU)
        await interaction.response.send_message(embed=countdown_embed)
        message = await interaction.original_response()
 
        for remaining in [3, 2, 1]:
            await asyncio.sleep(1)
            spin_embed = make_embed(
                "🎲 Đang lắc xí ngầu...",
                f"{'🎲 ' * remaining}\nCòn **{remaining}s**...",
                color=COLOR_TAIXIU,
            )
            await message.edit(embed=spin_embed)
 
        await asyncio.sleep(1)
 
        dice = [random.randint(1, 6) for _ in range(3)]
        total = sum(dice)
        dice_str = " ".join(DICE_EMOJIS[d - 1] for d in dice)
        result = "tai" if total >= 11 else "xiu"
        result_text = "TÀI" if result == "tai" else "XỈU"
 
        currency = await self.get_currency_name(interaction.guild_id)
        won = choice == result
 
        if won:
            payout = amount * 2
            await self.db.update_balance(interaction.user.id, interaction.guild_id, payout)
            await self.db.update_win_loss(interaction.user.id, interaction.guild_id, True)
            result_embed = success_embed(
                f"{dice_str}\nTổng: **{total}** → **{result_text}**\n\n"
                f"🎉 Bạn đã đoán đúng và nhận được **{format_number(payout)} {currency}**!",
                title="🎊 CHIẾN THẮNG!",
            )
        else:
            await self.db.update_win_loss(interaction.user.id, interaction.guild_id, False)
            result_embed = error_embed(
                f"{dice_str}\nTổng: **{total}** → **{result_text}**\n\n"
                f"😢 Bạn đã mất **{format_number(amount)} {currency}**. Chúc may mắn lần sau!",
                title="💥 THUA CUỘC",
            )
 
        await message.edit(embed=result_embed)
 
    # -------------------------------------------------------------
    # /baucua
    # -------------------------------------------------------------
    @app_commands.command(name="baucua", description="Chơi Bầu Cua Tôm Cá")
    @app_commands.checks.cooldown(1, 5, key=lambda i: (i.guild_id, i.user.id))
    async def baucua(self, interaction: discord.Interaction):
        animals_str = "  ".join(f"{v} {BAUCUA_NAMES_VI[k]}" for k, v in BAUCUA_ANIMALS.items())
        embed = make_embed(
            "🎡 BẦU CUA TÔM CÁ",
            f"{animals_str}\n\nChọn 1 hoặc nhiều con vật để cược từ menu bên dưới.\n"
            f"Mức cược mỗi con: {format_number(self.config['min_bet'])} - {format_number(self.config['max_bet'])}",
            color=COLOR_BAUCUA,
        )
        await interaction.response.send_message(embed=embed, view=BauCuaView(self))
 
    async def run_baucua(self, interaction: discord.Interaction, choices: list, amount_per: int):
        countdown_embed = make_embed("🎡 Đang quay Bầu Cua...", "🎰 Kết quả sẽ có sau giây lát!", color=COLOR_BAUCUA)
        await interaction.response.send_message(embed=countdown_embed)
        message = await interaction.original_response()
 
        for remaining in [3, 2, 1]:
            await asyncio.sleep(1)
            spin_embed = make_embed("🎡 Đang quay Bầu Cua...", f"🎡 Còn **{remaining}s**...", color=COLOR_BAUCUA)
            await message.edit(embed=spin_embed)
 
        await asyncio.sleep(1)
 
        keys = list(BAUCUA_ANIMALS.keys())
        rolled = [random.choice(keys) for _ in range(3)]
        rolled_str = "  ".join(f"{BAUCUA_ANIMALS[k]} {BAUCUA_NAMES_VI[k]}" for k in rolled)
 
        currency = await self.get_currency_name(interaction.guild_id)
        total_payout = 0
        total_bet = amount_per * len(choices)
        lines = []
 
        for choice in choices:
            count = rolled.count(choice)
            if count > 0:
                # Thắng: trả lại tiền gốc + thưởng theo số lần trúng (x1 tiền gốc mỗi lần trúng)
                payout = amount_per * (count + 1)
                total_payout += payout
                lines.append(f"{BAUCUA_ANIMALS[choice]} {BAUCUA_NAMES_VI[choice]}: trúng **{count}** lần → +{format_number(payout)}")
            else:
                lines.append(f"{BAUCUA_ANIMALS[choice]} {BAUCUA_NAMES_VI[choice]}: không trúng → -{format_number(amount_per)}")
 
        if total_payout > 0:
            await self.db.update_balance(interaction.user.id, interaction.guild_id, total_payout)
 
        net = total_payout - total_bet
        won_overall = net > 0
        await self.db.update_win_loss(interaction.user.id, interaction.guild_id, won_overall)
 
        embed_color = COLOR_BAUCUA if net >= 0 else 0xED4245  # tím nếu lãi/hòa, đỏ nếu lỗ
        result_embed = make_embed(
            "🎡 Kết quả Bầu Cua",
            f"Kết quả quay: {rolled_str}\n\n" + "\n".join(lines) +
            f"\n\n**Tổng kết:** {'+' if net >= 0 else ''}{format_number(net)} {currency}",
            color=embed_color,
        )
        await message.edit(embed=result_embed)
 
    # -------------------------------------------------------------
    # /coinflip
    # -------------------------------------------------------------
    @app_commands.command(name="coinflip", description="Tung đồng xu có cược")
    @app_commands.describe(amount="Số tiền cược", choice="Chọn sấp hoặc ngửa")
    @app_commands.choices(choice=[
        app_commands.Choice(name="Sấp", value="sap"),
        app_commands.Choice(name="Ngửa", value="ngua"),
    ])
    @app_commands.checks.cooldown(1, 5, key=lambda i: (i.guild_id, i.user.id))
    async def coinflip(self, interaction: discord.Interaction, amount: app_commands.Range[int, 1], choice: app_commands.Choice[str]):
        min_bet = self.config["min_bet"]
        max_bet = self.config["max_bet"]
        if amount < min_bet or amount > max_bet:
            await interaction.response.send_message(
                embed=error_embed(f"Số tiền cược phải từ **{format_number(min_bet)}** đến **{format_number(max_bet)}**."),
                ephemeral=True,
            )
            return
 
        user_row = await self.db.get_user(interaction.user.id, interaction.guild_id)
        if user_row["balance"] < amount:
            await interaction.response.send_message(embed=error_embed("Số dư không đủ để đặt cược."), ephemeral=True)
            return
 
        await self.db.update_balance(interaction.user.id, interaction.guild_id, -amount)
 
        result = random.choice(["sap", "ngua"])
        result_text = "Sấp" if result == "sap" else "Ngửa"
        currency = await self.get_currency_name(interaction.guild_id)
        won = choice.value == result
 
        if won:
            payout = amount * 2
            await self.db.update_balance(interaction.user.id, interaction.guild_id, payout)
            await self.db.update_win_loss(interaction.user.id, interaction.guild_id, True)
            embed = success_embed(
                f"🪙 Đồng xu ra mặt: **{result_text}**\n🎉 Bạn thắng **{format_number(payout)} {currency}**!",
                title="Chiến thắng!",
            )
        else:
            await self.db.update_win_loss(interaction.user.id, interaction.guild_id, False)
            embed = error_embed(
                f"🪙 Đồng xu ra mặt: **{result_text}**\n😢 Bạn mất **{format_number(amount)} {currency}**.",
                title="Thua cuộc",
            )
 
        await interaction.response.send_message(embed=embed)
 
 
async def setup(bot: commands.Bot):
    await bot.add_cog(Fun(bot))
