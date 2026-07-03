"""
cogs/wordchain.py
Trò chơi Nối Từ (Tiếng Việt / English) chơi theo từng kênh.

Luật:
- Tiếng Việt: mỗi từ gồm 2 âm tiết, âm tiết ĐẦU phải trùng âm tiết CUỐI của từ
  trước đó. VD: "con mèo" -> "mèo con" -> "con chó" -> ...
- English: mỗi từ nối bắt đầu bằng chữ cái CUỐI của từ trước đó.
  VD: "apple" -> "elephant" -> "tiger" -> ...

Người chơi gõ từ tiếp theo THẲNG vào kênh chat (không cần dùng lệnh) - giống
cách chơi nối từ truyền thống. Bot không dùng từ điển ngoài (không có mạng để
tải), nên chỉ kiểm tra ĐÚNG LUẬT NỐI + CHƯA TỪNG DÙNG, không kiểm tra từ đó có
thật sự "có nghĩa" hay không - để cả nhóm bạn bè tự thống nhất luật chơi.
"""

from __future__ import annotations

import asyncio
import logging
import random
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from utils.helpers import make_embed, success_embed, error_embed, get_category_color

logger = logging.getLogger("bot.wordchain")
CAT_COLOR = get_category_color("wordchain")

TURN_TIMEOUT_SECONDS = 60  # Không ai nối từ trong khoảng này -> tự kết thúc ván

VI_STARTERS = ["con mèo", "bàn ghế", "học sinh", "hoa hồng", "máy tính", "sách vở", "bạn bè", "yêu thương"]
EN_STARTERS = ["apple", "tiger", "orange", "dragon", "planet", "guitar", "yellow", "window"]


class WordChainGame:
    """Trạng thái của 1 ván nối từ đang diễn ra trong 1 kênh."""

    def __init__(self, mode: str, starter_word: str, started_by: int):
        self.mode = mode  # "vi" hoặc "en"
        self.current_word = starter_word.lower().strip()
        self.used_words = {self.current_word}
        self.scores: dict[int, int] = {}
        self.started_by = started_by
        self.turn_task: Optional[asyncio.Task] = None

    def _tail(self) -> str:
        """Phần người chơi TIẾP THEO cần nối vào: âm tiết cuối (VI) / chữ cái cuối (EN)."""
        if self.mode == "vi":
            return self.current_word.split()[-1]
        return self.current_word[-1]

    def _head(self, word: str) -> str:
        if self.mode == "vi":
            return word.split()[0]
        return word[0]

    def _is_valid_format(self, word: str) -> bool:
        if self.mode == "vi":
            parts = word.split()
            return len(parts) == 2 and all(p.isalpha() for p in parts)
        return word.isalpha() and len(word) >= 2

    def try_play(self, raw_word: str, user_id: int) -> tuple[bool, str]:
        """Thử nối từ. Trả về (thành_công, lý_do).
        lý do: "ok" | "format" (sai định dạng, bỏ qua) | "used" (đã dùng) | "chain" (không nối đúng)"""
        word = raw_word.lower().strip()
        if not self._is_valid_format(word):
            return False, "format"
        if word in self.used_words:
            return False, "used"
        if self._head(word) != self._tail():
            return False, "chain"

        self.current_word = word
        self.used_words.add(word)
        self.scores[user_id] = self.scores.get(user_id, 0) + 1
        return True, "ok"


class WordChain(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.games: dict[int, WordChainGame] = {}  # channel_id -> ván đang chơi

    def cog_unload(self):
        for game in self.games.values():
            if game.turn_task and not game.turn_task.done():
                game.turn_task.cancel()

    # -------------------------------------------------------------
    # Nhóm lệnh /noitu
    # -------------------------------------------------------------
    noitu_group = app_commands.Group(name="noitu", description="Trò chơi Nối Từ trong kênh")

    # -------------------------------------------------------------
    # /noitu start
    # -------------------------------------------------------------
    @noitu_group.command(name="start", description="Bắt đầu ván nối từ (Anh/Việt) trong kênh")
    @app_commands.describe(mode="Chọn ngôn ngữ chơi")
    @app_commands.choices(mode=[
        app_commands.Choice(name="Tiếng Việt", value="vi"),
        app_commands.Choice(name="English", value="en"),
    ])
    async def start(self, interaction: discord.Interaction, mode: app_commands.Choice[str]):
        channel_id = interaction.channel_id
        if channel_id in self.games:
            await interaction.response.send_message(
                embed=error_embed("Kênh này đang có ván nối từ diễn ra. Dùng `/noitu stop` để dừng trước."),
                ephemeral=True,
            )
            return

        starter = random.choice(VI_STARTERS if mode.value == "vi" else EN_STARTERS)
        game = WordChainGame(mode.value, starter, interaction.user.id)
        self.games[channel_id] = game
        self._reset_timeout(interaction.channel)

        if mode.value == "vi":
            rule_text = (
                "Mỗi từ nối gồm **2 âm tiết**, âm tiết đầu phải trùng âm tiết cuối của từ trước.\n"
                "VD: `con mèo` → `mèo con` → `con chó` ..."
            )
        else:
            rule_text = (
                "Mỗi từ nối bắt đầu bằng **chữ cái cuối** của từ trước.\n"
                "VD: `apple` → `elephant` → `tiger` ..."
            )

        embed = make_embed(
            "🔤 Ván Nối Từ bắt đầu!",
            f"{rule_text}\n\n"
            f"🟢 Từ đầu tiên: **{starter}**\n"
            f"👉 Ai cũng có thể gõ từ tiếp theo thẳng vào kênh (không cần gõ lệnh).\n"
            f"⏳ Nếu không ai nối trong **{TURN_TIMEOUT_SECONDS}s**, ván sẽ tự kết thúc.",
            color=CAT_COLOR,
        )
        await interaction.response.send_message(embed=embed)

    # -------------------------------------------------------------
    # /noitu stop
    # -------------------------------------------------------------
    @noitu_group.command(name="stop", description="Dừng ván nối từ trong kênh")
    async def stop(self, interaction: discord.Interaction):
        game = self.games.get(interaction.channel_id)
        if not game:
            await interaction.response.send_message(
                embed=error_embed("Kênh này không có ván nối từ nào đang diễn ra."), ephemeral=True
            )
            return

        is_admin = isinstance(interaction.user, discord.Member) and interaction.user.guild_permissions.administrator
        if interaction.user.id != game.started_by and not is_admin:
            await interaction.response.send_message(
                embed=error_embed("Chỉ người đã bắt đầu ván hoặc Admin mới được dừng."), ephemeral=True
            )
            return

        await self._end_game(interaction.channel, reason="⏹️ Ván đã bị dừng thủ công.")
        await interaction.response.send_message(embed=success_embed("Đã dừng ván nối từ."))

    # -------------------------------------------------------------
    # /noitu score
    # -------------------------------------------------------------
    @noitu_group.command(name="score", description="Xem bảng điểm ván nối từ hiện tại")
    async def score(self, interaction: discord.Interaction):
        game = self.games.get(interaction.channel_id)
        if not game:
            await interaction.response.send_message(
                embed=error_embed("Kênh này không có ván nối từ nào đang diễn ra."), ephemeral=True
            )
            return

        if not game.scores:
            embed = make_embed(
                "📊 Bảng điểm Nối Từ",
                f"Chưa có ai nối được từ nào.\n🔤 Từ hiện tại: **{game.current_word}**",
                color=CAT_COLOR,
            )
            await interaction.response.send_message(embed=embed)
            return

        ranked = sorted(game.scores.items(), key=lambda x: x[1], reverse=True)
        medals = ["🥇", "🥈", "🥉"]
        lines = []
        for idx, (uid, score) in enumerate(ranked):
            member = interaction.guild.get_member(uid)
            name = member.display_name if member else f"User {uid}"
            prefix = medals[idx] if idx < 3 else f"**#{idx + 1}**"
            lines.append(f"{prefix} {name} — **{score}** từ")

        embed = make_embed(
            "📊 Bảng điểm Nối Từ",
            "\n".join(lines) + f"\n\n🔤 Từ hiện tại: **{game.current_word}**",
            color=CAT_COLOR,
        )
        await interaction.response.send_message(embed=embed)

    # -------------------------------------------------------------
    # Người chơi gõ từ trực tiếp vào kênh (không cần lệnh)
    # -------------------------------------------------------------
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or message.guild is None:
            return
        game = self.games.get(message.channel.id)
        if not game:
            return

        content = message.content.strip()
        if not content:
            return

        ok, reason = game.try_play(content, message.author.id)
        if ok:
            self._reset_timeout(message.channel)
            try:
                await message.add_reaction("✅")
            except discord.HTTPException:
                pass
        elif reason in ("used", "chain"):
            # Chỉ react ❌ khi tin nhắn ĐÚNG ĐỊNH DẠNG từ nối (2 âm tiết / 1 từ Anh)
            # nhưng sai luật (trùng hoặc không nối được) - tránh spam ❌ vào MỌI
            # tin nhắn chat bình thường không liên quan đến ván chơi.
            try:
                await message.add_reaction("❌")
            except discord.HTTPException:
                pass

    # -------------------------------------------------------------
    # Tự động kết thúc ván khi hết giờ
    # -------------------------------------------------------------
    def _reset_timeout(self, channel: discord.abc.Messageable):
        game = self.games.get(channel.id)
        if not game:
            return
        if game.turn_task and not game.turn_task.done():
            game.turn_task.cancel()
        game.turn_task = asyncio.create_task(self._timeout_watch(channel))

    async def _timeout_watch(self, channel: discord.abc.Messageable):
        try:
            await asyncio.sleep(TURN_TIMEOUT_SECONDS)
        except asyncio.CancelledError:
            return
        await self._end_game(channel, reason=f"⏰ Hết giờ! Không ai nối từ trong {TURN_TIMEOUT_SECONDS} giây.")

    async def _end_game(self, channel: discord.abc.Messageable, reason: str):
        game = self.games.pop(channel.id, None)
        if not game:
            return
        if game.turn_task and not game.turn_task.done():
            game.turn_task.cancel()

        if game.scores:
            winner_id = max(game.scores, key=game.scores.get)
            member = channel.guild.get_member(winner_id) if isinstance(channel, discord.TextChannel) else None
            winner_name = member.display_name if member else f"User {winner_id}"
            desc = (
                f"{reason}\n\n"
                f"🏆 Người thắng: **{winner_name}** ({game.scores[winner_id]} từ)\n"
                f"📝 Tổng số từ đã nối: **{len(game.used_words) - 1}**"
            )
        else:
            desc = f"{reason}\n\nChưa có ai nối được từ nào trong ván này."

        embed = make_embed("🏁 Ván Nối Từ kết thúc", desc, color=CAT_COLOR)
        try:
            await channel.send(embed=embed)
        except discord.HTTPException:
            pass


async def setup(bot: commands.Bot):
    await bot.add_cog(WordChain(bot))
