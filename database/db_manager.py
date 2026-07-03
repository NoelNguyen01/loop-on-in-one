"""
db_manager.py
Quản lý toàn bộ thao tác với cơ sở dữ liệu SQLite (dùng aiosqlite - bất đồng bộ)
"""

import aiosqlite
import logging
import time
from typing import Optional, List, Tuple, Any

logger = logging.getLogger("bot.database")


class DBManager:
    def __init__(self, db_path: str = "bot.db"):
        self.db_path = db_path
        self._conn: Optional[aiosqlite.Connection] = None

    async def connect(self):
        """Kết nối tới database và tạo bảng nếu chưa có"""
        self._conn = await aiosqlite.connect(self.db_path)
        self._conn.row_factory = aiosqlite.Row
        await self._create_tables()
        logger.info(f"Đã kết nối database: {self.db_path}")

    async def close(self):
        """Đóng kết nối database"""
        if self._conn:
            await self._conn.close()
            logger.info("Đã đóng kết nối database")

    async def _create_tables(self):
        """Tạo các bảng cần thiết nếu chưa tồn tại"""
        await self._conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                guild_id TEXT NOT NULL,
                balance INTEGER DEFAULT 0,
                daily_streak INTEGER DEFAULT 0,
                last_daily INTEGER DEFAULT 0,
                total_wins INTEGER DEFAULT 0,
                total_losses INTEGER DEFAULT 0,
                UNIQUE(user_id, guild_id)
            );

            CREATE TABLE IF NOT EXISTS keywords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id TEXT NOT NULL,
                keyword TEXT NOT NULL,
                response TEXT NOT NULL,
                created_by TEXT NOT NULL,
                usage_count INTEGER DEFAULT 0,
                created_at INTEGER DEFAULT 0,
                UNIQUE(guild_id, keyword)
            );

            CREATE TABLE IF NOT EXISTS guild_settings (
                guild_id TEXT PRIMARY KEY,
                welcome_channel TEXT,
                goodbye_channel TEXT,
                voicelog_channel TEXT,
                currency_name TEXT DEFAULT 'coins'
            );

            CREATE TABLE IF NOT EXISTS voice_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                guild_id TEXT NOT NULL,
                channel_name TEXT,
                join_time INTEGER,
                leave_time INTEGER,
                duration INTEGER
            );
            """
        )
        await self._conn.commit()

    # ---------------------------------------------------------------
    # USERS
    # ---------------------------------------------------------------
    async def get_user(self, user_id: str, guild_id: str) -> aiosqlite.Row:
        """Lấy thông tin user, tự tạo mới nếu chưa tồn tại"""
        cursor = await self._conn.execute(
            "SELECT * FROM users WHERE user_id = ? AND guild_id = ?",
            (str(user_id), str(guild_id)),
        )
        row = await cursor.fetchone()
        if row is None:
            await self._conn.execute(
                "INSERT INTO users (user_id, guild_id, balance) VALUES (?, ?, 0)",
                (str(user_id), str(guild_id)),
            )
            await self._conn.commit()
            cursor = await self._conn.execute(
                "SELECT * FROM users WHERE user_id = ? AND guild_id = ?",
                (str(user_id), str(guild_id)),
            )
            row = await cursor.fetchone()
        return row

    async def update_balance(self, user_id: str, guild_id: str, amount: int) -> int:
        """Cộng/trừ số dư (amount có thể âm). Trả về số dư mới"""
        await self.get_user(user_id, guild_id)  # đảm bảo tồn tại
        await self._conn.execute(
            "UPDATE users SET balance = balance + ? WHERE user_id = ? AND guild_id = ?",
            (amount, str(user_id), str(guild_id)),
        )
        await self._conn.commit()
        row = await self.get_user(user_id, guild_id)
        return row["balance"]

    async def set_balance(self, user_id: str, guild_id: str, amount: int):
        """Đặt số dư cụ thể"""
        await self.get_user(user_id, guild_id)
        await self._conn.execute(
            "UPDATE users SET balance = ? WHERE user_id = ? AND guild_id = ?",
            (amount, str(user_id), str(guild_id)),
        )
        await self._conn.commit()

    async def get_top_balance(self, guild_id: str, limit: int = 10) -> List[aiosqlite.Row]:
        """Lấy bảng xếp hạng số dư"""
        cursor = await self._conn.execute(
            "SELECT * FROM users WHERE guild_id = ? ORDER BY balance DESC LIMIT ?",
            (str(guild_id), limit),
        )
        return await cursor.fetchall()

    async def update_daily(self, user_id: str, guild_id: str, streak: int, timestamp: int):
        """Cập nhật streak điểm danh và thời gian điểm danh gần nhất"""
        await self.get_user(user_id, guild_id)
        await self._conn.execute(
            "UPDATE users SET daily_streak = ?, last_daily = ? WHERE user_id = ? AND guild_id = ?",
            (streak, timestamp, str(user_id), str(guild_id)),
        )
        await self._conn.commit()

    async def update_win_loss(self, user_id: str, guild_id: str, win: bool):
        """Cộng thêm 1 vào total_wins hoặc total_losses"""
        await self.get_user(user_id, guild_id)
        col = "total_wins" if win else "total_losses"
        await self._conn.execute(
            f"UPDATE users SET {col} = {col} + 1 WHERE user_id = ? AND guild_id = ?",
            (str(user_id), str(guild_id)),
        )
        await self._conn.commit()

    # ---------------------------------------------------------------
    # KEYWORDS
    # ---------------------------------------------------------------
    async def add_keyword(self, guild_id: str, keyword: str, response: str, created_by: str) -> bool:
        """Thêm từ khóa mới. Trả về False nếu đã tồn tại"""
        try:
            await self._conn.execute(
                "INSERT INTO keywords (guild_id, keyword, response, created_by, usage_count, created_at) "
                "VALUES (?, ?, ?, ?, 0, ?)",
                (str(guild_id), keyword.lower(), response, str(created_by), int(time.time())),
            )
            await self._conn.commit()
            return True
        except aiosqlite.IntegrityError:
            return False

    async def delete_keyword(self, guild_id: str, keyword: str) -> bool:
        """Xóa từ khóa, trả về True nếu xóa thành công"""
        cursor = await self._conn.execute(
            "DELETE FROM keywords WHERE guild_id = ? AND keyword = ?",
            (str(guild_id), keyword.lower()),
        )
        await self._conn.commit()
        return cursor.rowcount > 0

    async def get_keyword(self, guild_id: str, keyword: str) -> Optional[aiosqlite.Row]:
        cursor = await self._conn.execute(
            "SELECT * FROM keywords WHERE guild_id = ? AND keyword = ?",
            (str(guild_id), keyword.lower()),
        )
        return await cursor.fetchone()

    async def get_all_keywords(self, guild_id: str) -> List[aiosqlite.Row]:
        cursor = await self._conn.execute(
            "SELECT * FROM keywords WHERE guild_id = ? ORDER BY keyword ASC",
            (str(guild_id),),
        )
        return await cursor.fetchall()

    async def increment_keyword_usage(self, guild_id: str, keyword: str):
        await self._conn.execute(
            "UPDATE keywords SET usage_count = usage_count + 1 WHERE guild_id = ? AND keyword = ?",
            (str(guild_id), keyword.lower()),
        )
        await self._conn.commit()

    # ---------------------------------------------------------------
    # GUILD SETTINGS
    # ---------------------------------------------------------------
    async def get_guild_settings(self, guild_id: str) -> aiosqlite.Row:
        cursor = await self._conn.execute(
            "SELECT * FROM guild_settings WHERE guild_id = ?", (str(guild_id),)
        )
        row = await cursor.fetchone()
        if row is None:
            await self._conn.execute(
                "INSERT INTO guild_settings (guild_id, currency_name) VALUES (?, 'coins')",
                (str(guild_id),),
            )
            await self._conn.commit()
            cursor = await self._conn.execute(
                "SELECT * FROM guild_settings WHERE guild_id = ?", (str(guild_id),)
            )
            row = await cursor.fetchone()
        return row

    async def set_guild_setting(self, guild_id: str, column: str, value: Any):
        """Cập nhật một cột cụ thể trong guild_settings"""
        await self.get_guild_settings(guild_id)
        allowed_columns = {
            "welcome_channel",
            "goodbye_channel",
            "voicelog_channel",
            "currency_name",
        }
        if column not in allowed_columns:
            raise ValueError(f"Cột không hợp lệ: {column}")
        await self._conn.execute(
            f"UPDATE guild_settings SET {column} = ? WHERE guild_id = ?",
            (value, str(guild_id)),
        )
        await self._conn.commit()

    # ---------------------------------------------------------------
    # VOICE LOGS
    # ---------------------------------------------------------------
    async def add_voice_join(self, user_id: str, guild_id: str, channel_name: str, join_time: int) -> int:
        """Ghi log khi user vào voice, trả về id bản ghi"""
        cursor = await self._conn.execute(
            "INSERT INTO voice_logs (user_id, guild_id, channel_name, join_time) VALUES (?, ?, ?, ?)",
            (str(user_id), str(guild_id), channel_name, join_time),
        )
        await self._conn.commit()
        return cursor.lastrowid

    async def update_voice_leave(self, log_id: int, leave_time: int, duration: int):
        """Cập nhật thời gian rời voice"""
        await self._conn.execute(
            "UPDATE voice_logs SET leave_time = ?, duration = ? WHERE id = ?",
            (leave_time, duration, log_id),
        )
        await self._conn.commit()
