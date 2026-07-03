"""
cogs/wordchain.py
Trò chơi Nối Từ - hỗ trợ Tiếng Anh (nối từ đơn) và Tiếng Việt (nối từ ghép 2 âm tiết)

- Tiếng Anh: chữ cái ĐẦU của từ mới phải trùng chữ cái CUỐI của từ trước.
  VD: apple -> elephant -> train ...
- Tiếng Việt: cụm 2 từ, từ ĐẦU của cụm mới phải trùng từ CUỐI của cụm trước.
  VD: "con mèo" -> "mèo con" -> "con chó" ...

Lưu ý: bot KHÔNG có từ điển để xác minh từ có tồn tại thật hay không (cần
tích hợp API/từ điển ngoài mới làm được điều đó). Bot chỉ kiểm tra: đúng luật
nối, chưa từng dùng trong ván hiện tại, và đúng định dạng theo ngôn ngữ.
"""

# QUAN TRỌNG: cho phép dùng cú pháp type hint mới (str | None, tuple[bool, str]...)
# mà vẫn chạy được trên Python 3.8/3.9 (project khai báo hỗ trợ Python 3.8+ trong
# README) - nếu thiếu dòng này, bot sẽ crash ngay khi load cog trên Python < 3.10.
from __future__ import annotations

import logging
import unicodedata

import discord
from discord import app_commands
from discord.ext import commands

from utils.helpers import make_embed, success_embed, error_embed

logger = logging.getLogger("bot.wordchain")


def _normalize(text: str) -> str:
    """Chuẩn hóa Unicode (gộp dấu tổ hợp) + hạ chữ thường + rút gọn khoảng trắng,
    để so sánh nối từ không bị lệch vì cách gõ dấu khác nhau."""
    text = unicodedata.normalize("NFC", text.strip().lower())
    return " ".join(text.split())


class GameState:
    def __init__(self, lang: str, starter_id: int):
        self.lang = lang  # "en" hoặc "vi"
        self.starter_id = starter_id
        self.current: str | None = None       # cụm/từ hiện tại (đã normalize)
        self.current_display: str | None = None  # để hiển thị đẹp (giữ nguyên chữ hoa/thường gốc)
        self.used: set[str] = set()
        self.last_player_id: int | None = None
        self.players: set[int] = set()
        self.scores: dict[int, int] = {}


class WordChain(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.games: dict[int, GameState] = {}  # channel_id -> GameState

    noitu_group = app_commands.Group(name="noitu", description="Trò chơi nối từ Anh - Việt")

    # -------------------------------------------------------------
    # /noitu start
    # -------------------------------------------------------------
    @noitu_group.command(name="start", description="Bắt đầu ván nối từ trong kênh này")
    @app_commands.describe(
        ngon_ngu="Chọn ngôn ngữ nối từ",
        tu_bat_dau="(Tùy chọn) Từ/cụm từ khởi đầu, để trống thì người chơi đầu tiên sẽ tự đặt",
    )
    @app_commands.choices(ngon_ngu=[
        app_commands.Choice(name="Tiếng Anh", value="en"),
        app_commands.Choice(name="Tiếng Việt", value="vi"),
    ])
    async def noitu_start(
        self,
        interaction: discord.Interaction,
        ngon_ngu: app_commands.Choice[str],
        tu_bat_dau: str = None,
    ):
        channel_id = interaction.channel_id
        if channel_id in self.games:
            await interaction.response.send_message(
                embed=error_embed("Kênh này đang có 1 ván nối từ chưa kết thúc. Dùng `/noitu stop` để dừng trước."),
                ephemeral=True,
            )
            return

        game = GameState(lang=ngon_ngu.value, starter_id=interaction.user.id)

        if tu_bat_dau:
            ok, err = self._validate_format(tu_bat_dau, game.lang)
            if not ok:
                await interaction.response.send_message(embed=error_embed(err), ephemeral=True)
                return
            norm = _normalize(tu_bat_dau)
            game.current = norm
            game.current_display = tu_bat_dau.strip()
            game.used.add(norm)

        self.games[channel_id] = game

        lang_name = "Tiếng Anh 🇬🇧" if game.lang == "en" else "Tiếng Việt 🇻🇳"
        rule = (
            "Chữ cái **đầu** từ mới phải trùng chữ cái **cuối** từ trước. VD: `apple` → `elephant` → `train`"
            if game.lang == "en"
            else "Từ **đầu** của cụm mới phải trùng từ **cuối** của cụm trước. VD: `con mèo` → `mèo con` → `con chó`"
        )
        desc = f"**Ngôn ngữ:** {lang_name}\n**Luật:** {rule}\n\n"
        if game.current_display:
            desc += f"Từ bắt đầu: **{game.current_display}**\nHãy nối tiếp!"
        else:
            desc += "Chưa có từ bắt đầu — người chơi đầu tiên hãy nhắn 1 từ (hoặc cụm) bất kỳ để mở màn!"

        embed = make_embed("🔤 Ván nối từ bắt đầu!", desc)
        await interaction.response.send_message(embed=embed)

    # -------------------------------------------------------------
    # /noitu stop
    # -------------------------------------------------------------
    @noitu_group.command(name="stop", description="Dừng ván nối từ trong kênh này")
    async def noitu_stop(self, interaction: discord.Interaction):
        channel_id = interaction.channel_id
        game = self.games.get(channel_id)

        if game is None:
            await interaction.response.send_message(embed=error_embed("Kênh này chưa có ván nối từ nào đang chạy."), ephemeral=True)
            return

        is_admin = getattr(interaction.user, "guild_permissions", None) and interaction.user.guild_permissions.administrator
        if interaction.user.id != game.starter_id and not is_admin:
            await interaction.response.send_message(
                embed=error_embed("Chỉ người tạo ván hoặc Admin mới có thể dừng ván nối từ."),
                ephemeral=True,
            )
            return

        del self.games[channel_id]
        await interaction.response.send_message(embed=success_embed("Ván nối từ đã kết thúc. Cảm ơn mọi người đã chơi! 🎉"))

    # -------------------------------------------------------------
    # /noitu diem
    # -------------------------------------------------------------
    @noitu_group.command(name="diem", description="Xem bảng điểm ván nối từ hiện tại trong kênh")
    async def noitu_diem(self, interaction: discord.Interaction):
        game = self.games.get(interaction.channel_id)
        if game is None or not game.scores:
            await interaction.response.send_message(embed=error_embed("Chưa có dữ liệu điểm cho kênh này."), ephemeral=True)
            return

        ranking = sorted(game.scores.items(), key=lambda x: x[1], reverse=True)
        lines = []
        for i, (user_id, score) in enumerate(ranking, start=1):
            lines.append(f"**{i}.** <@{user_id}> — {score} từ")

        embed = make_embed("🏆 Bảng điểm nối từ", "\n".join(lines))
        await interaction.response.send_message(embed=embed)

    # -------------------------------------------------------------
    # Validate định dạng theo ngôn ngữ (chưa xét luật nối)
    # -------------------------------------------------------------
    @staticmethod
    def _validate_format(text: str, lang: str) -> tuple[bool, str]:
        text = text.strip()
        if lang == "en":
            if not text.isascii() or not text.replace(" ", "").isalpha() or " " in text:
                return False, "Từ tiếng Anh chỉ được chứa 1 từ, chỉ gồm chữ cái (a-z), không dấu cách."
            if len(text) < 2:
                return False, "Từ phải có ít nhất 2 ký tự."
            return True, ""
        else:  # vi
            parts = text.split()
            if len(parts) != 2:
                return False, "Cụm từ tiếng Việt phải gồm đúng **2 từ**, cách nhau bởi dấu cách. VD: `con mèo`."
            if not all(p.isalpha() for p in parts):
                return False, "Cụm từ chỉ được chứa chữ cái (có dấu), không chứa số hay ký tự đặc biệt."
            return True, ""

    # -------------------------------------------------------------
    # Listener: xử lý các lượt nối từ trong kênh đang có ván chạy
    # -------------------------------------------------------------
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or message.guild is None:
            return

        game = self.games.get(message.channel.id)
        if game is None:
            return

        # Bỏ qua tin nhắn là lệnh slash / prefix khác, chỉ xử lý nội dung thường
        content = message.content.strip()
        if not content or content.startswith("/") or content.startswith("."):
            return

        ok, err = self._validate_format(content, game.lang)
        if not ok:
            # Không phải định dạng nối từ hợp lệ -> có thể chỉ là chat thường, bỏ qua lặng lẽ
            return

        norm = _normalize(content)

        # Không cho phép cùng 1 người nối 2 lượt liên tiếp nếu đã có từ 2 người chơi trở lên
        if game.last_player_id == message.author.id and len(game.players) > 1:
            await message.add_reaction("⏭️")
            await message.reply("Bạn vừa nối rồi, hãy để người khác nối tiếp nhé!", mention_author=False)
            return

        # Chưa có từ hiện tại -> đây là từ mở màn, chấp nhận luôn
        if game.current is None:
            game.current = norm
            game.current_display = content
            game.used.add(norm)
            game.last_player_id = message.author.id
            game.players.add(message.author.id)
            game.scores[message.author.id] = game.scores.get(message.author.id, 0) + 1
            await message.add_reaction("✅")
            return

        # Kiểm tra luật nối
        if game.lang == "en":
            valid_link = norm[0] == game.current[-1]
        else:
            prev_last_word = game.current.split()[-1]
            new_first_word = norm.split()[0]
            valid_link = new_first_word == prev_last_word

        if not valid_link:
            await message.add_reaction("❌")
            return

        if norm in game.used:
            await message.add_reaction("♻️")
            await message.reply("Từ này đã được dùng rồi, hãy nối từ khác!", mention_author=False)
            return

        # Hợp lệ -> cập nhật trạng thái ván chơi
        game.current = norm
        game.current_display = content
        game.used.add(norm)
        game.last_player_id = message.author.id
        game.players.add(message.author.id)
        game.scores[message.author.id] = game.scores.get(message.author.id, 0) + 1
        await message.add_reaction("✅")


async def setup(bot: commands.Bot):
    # app_commands.Group là class attribute (noitu_group) nên discord.py tự
    # đăng ký nhóm lệnh này vào command tree khi add_cog() chạy.
    await bot.add_cog(WordChain(bot))
