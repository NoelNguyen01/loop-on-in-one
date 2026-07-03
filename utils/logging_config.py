"""
utils/logging_config.py
Cấu hình logging: console có màu + gọn (chỉ giờ:phút:giây), file log giữ
nguyên định dạng đầy đủ, không màu (để mở bằng text editor không bị lẫn mã ANSI).
"""

import sys
import ctypes
import logging


def _enable_windows_ansi_colors():
    """Bật hỗ trợ mã màu ANSI cho Command Prompt / PowerShell cũ trên Windows.
    Windows Terminal / PowerShell 7 hiện đại thường đã bật sẵn, nhưng gọi thêm
    ở đây để chắc chắn hoạt động trên mọi phiên bản Windows."""
    if sys.platform != "win32":
        return
    try:
        kernel32 = ctypes.windll.kernel32
        STD_OUTPUT_HANDLE = -11
        ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
        handle = kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
        mode = ctypes.c_uint32()
        if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            kernel32.SetConsoleMode(handle, mode.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING)
    except Exception:
        # Nếu bật không thành công (ví dụ chạy trong môi trường không phải console
        # thật, như một số IDE), bỏ qua và để text không màu - không làm crash bot.
        pass


class ColorFormatter(logging.Formatter):
    """Formatter cho console: có màu theo mức độ log, timestamp rút gọn HH:MM:SS."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    LEVEL_COLORS = {
        logging.DEBUG: "\033[36m",     # cyan
        logging.INFO: "\033[32m",      # xanh lá
        logging.WARNING: "\033[33m",   # vàng
        logging.ERROR: "\033[31m",     # đỏ
        logging.CRITICAL: "\033[97;41m",  # chữ trắng nền đỏ
    }

    LEVEL_ICONS = {
        logging.DEBUG: "🔍",
        logging.INFO: "✅",
        logging.WARNING: "⚠️ ",
        logging.ERROR: "❌",
        logging.CRITICAL: "💥",
    }

    def format(self, record: logging.LogRecord) -> str:
        color = self.LEVEL_COLORS.get(record.levelno, "")
        icon = self.LEVEL_ICONS.get(record.levelno, "")
        time_str = self.formatTime(record, "%H:%M:%S")

        header = f"{self.DIM}{time_str}{self.RESET} {color}{self.BOLD}{icon} {record.levelname:<8}{self.RESET}"
        source = f"{self.DIM}{record.name}{self.RESET}"
        line = f"{header} {source} › {record.getMessage()}"

        if record.exc_info:
            line += "\n" + self.formatException(record.exc_info)
        return line


class _SuppressNoisyConsoleFilter(logging.Filter):
    """Bớt ồn console: ẩn log INFO/DEBUG từ 'discord.*' (gateway, heartbeat...),
    nhưng vẫn giữ nguyên WARNING/ERROR trở lên. File bot.log không bị ảnh hưởng
    bởi filter này nên vẫn ghi đầy đủ mọi log để debug khi cần."""

    def filter(self, record: logging.LogRecord) -> bool:
        if record.name.startswith("discord") and record.levelno < logging.WARNING:
            return False
        return True


def setup_logging(log_file: str = "bot.log") -> logging.Logger:
    """Thiết lập logging cho toàn bộ bot. Gọi 1 lần duy nhất ở đầu main.py."""
    _enable_windows_ansi_colors()

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(
        logging.Formatter("[%(asctime)s] [%(levelname)s] %(name)s: %(message)s")
    )
    # File giữ nguyên đầy đủ mọi log (kể cả discord.* INFO) để debug khi cần

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(ColorFormatter())
    console_handler.addFilter(_SuppressNoisyConsoleFilter())  # chỉ áp dụng cho console

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    # Xóa handler mặc định (nếu có) để tránh log bị in trùng 2 lần
    root_logger.handlers.clear()
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    return logging.getLogger("bot.main")
