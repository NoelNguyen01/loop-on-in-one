# loop-on-in-one 🎲

Discord bot kết hợp nhiều hệ thống: **kinh tế, level/XP, moderation, auto-mod,
role tự động, thống kê, và cả hệ thống kết hôn** — tất cả dùng slash command (`/`)
chuẩn Discord, dữ liệu lưu bằng SQLite (không cần setup database server).

## ✨ Tính năng

| Nhóm | Mô tả |
|---|---|
| 🪙 Kinh tế | balance, daily (có streak), work, shop/buy/sell, give, rob, gamble, leaderboard, pay_all |
| 📊 Level/XP | tự cộng XP qua tin nhắn / voice / reaction, rank, leaderboard, role theo level, double XP |
| 🛡️ Moderation | warn/warnings, mute (timeout), kick, ban, unban, clear, slowmode, log đầy đủ |
| 🎮 Giải trí | avatar, server/user info, ping, roll, flip, 8ball, quote, suggest, poll |
| 🎁 Role | give/remove role, autorole khi join, welcome/goodbye |
| 🔧 Auto-Mod | chống spam, chống link, chống ping hàng loạt, log xóa/sửa tin nhắn |
| 🎨 Cài đặt | đổi tên tiền tệ, kênh welcome/goodbye/rank/log, reset dữ liệu |
| 📈 Thống kê | server_stats, user_stats, top_activity, bot_info |
| 🔐 Admin | backup/restore dữ liệu ra JSON, blacklist/whitelist |
| 🧠 Đặc biệt | hệ thống kết hôn `/marry /divorce /profile` |

> Lệnh `/exec` (chạy code tùy ý) **cố tình không được triển khai** vì đây là một
> lỗ hổng bảo mật nghiêm trọng (RCE) — xem giải thích trong `GHI_CHU_TICH_HOP.md`.

## 📦 Cấu trúc dự án

```
loop-on-in-one/
├── main.py                # Điểm khởi chạy, load cogs, sync slash command
├── config.json             # Cấu hình mặc định (prefix, đường dẫn DB, màu embed)
├── requirements.txt
├── .env.example             # Mẫu biến môi trường (DISCORD_TOKEN, DEV_GUILD_ID)
├── database/
│   └── db.py                 # Lớp Database (SQLite qua aiosqlite) — toàn bộ schema & query
├── utils/
│   └── helpers.py             # Embed helper, parse thời gian, check quyền admin...
└── cogs/
    ├── economy.py
    ├── leveling.py
    ├── moderation.py
    ├── fun.py
    ├── roles.py
    ├── automod.py
    ├── settings.py
    ├── stats.py
    ├── admin.py
    ├── social.py             # Hệ thống kết hôn + /profile
    └── help.py                # /help liệt kê toàn bộ lệnh
```

## 🚀 Cài đặt

1. Tạo bot tại [Discord Developer Portal](https://discord.com/developers/applications),
   lấy **Token** trong tab *Bot*.
2. Bật 2 **Privileged Gateway Intents** (bắt buộc): `SERVER MEMBERS INTENT` và
   `MESSAGE CONTENT INTENT`.
3. Mời bot vào server với quyền tối thiểu: `Manage Roles`, `Manage Messages`,
   `Kick Members`, `Ban Members`, `Moderate Members`, `Send Messages`, `Embed Links`.
4. Clone & cài đặt:

```bash
git clone https://github.com/NoelNguyen01/loop-on-in-one.git
cd loop-on-in-one
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Mở .env, điền DISCORD_TOKEN=...
python main.py
```

Muốn test lệnh **ngay lập tức** thay vì chờ Discord đồng bộ global (~1 giờ), điền
thêm `DEV_GUILD_ID=<id server test>` trong `.env`.

## 🗄️ Dữ liệu

Toàn bộ dữ liệu (số dư, XP, cảnh cáo, cài đặt server...) lưu trong file `bot.db`
(SQLite, tự tạo khi chạy lần đầu). Dùng `/backup` để xuất dữ liệu server ra JSON,
`/restore` để nhập lại.

## 🔒 Bảo mật

- Toàn bộ lệnh admin đều kiểm tra quyền `Administrator` hoặc `Moderate Members`
  trước khi thực thi.
- Người dùng bị `/blacklist` sẽ bị chặn ở **mọi** slash command (kiểm tra ở tầng
  `CommandTree`, không thể bypass bằng cách gọi cog khác).
- Không có lệnh chạy code tùy ý (`exec`, `eval`...).

## 🤝 Đóng góp

Pull request luôn được chào đón! Khi thêm cog mới, nhớ:
1. Đăng ký cog trong `INITIAL_COGS` ở `main.py`.
2. Thêm nhóm lệnh mới vào `cogs/help.py` để `/help` hiển thị đầy đủ.
3. Dùng `utils/helpers.py` (`make_embed`, `success_embed`, `error_embed`) để đồng
   bộ giao diện.


![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8%2B-green)
![Discord](https://img.shields.io/badge/discord.py-py-blueviolet)
![Status](https://img.shields.io/badge/status-active-brightgreen)
