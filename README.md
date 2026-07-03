<div align="center">

# 🎲 Loop On In One

### Discord Bot đa năng — Kinh tế ảo · Game giải trí · Từ khóa tự động · Quản lý server
![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8%2B-green
)![Discord](https://img.shields.io/badge/discord.py-py-blueviolet)
![Status](https://img.shields.io/badge/status-active-brightgreen)
</div>

<br>

> ⚠️ **Lưu ý:** Toàn bộ tiền tệ trong bot là **tiền ảo trong game**, không có giá trị quy đổi thực tế — chỉ phục vụ mục đích giải trí nội bộ server.

<br>

## 📚 Mục lục

- [✨ Tính năng](#-tính-năng)
- [🚀 Cài đặt](#-hướng-dẫn-cài-đặt)
- [📂 Cấu trúc thư mục](#-cấu-trúc-thư-mục)
- [📋 Danh sách lệnh](#-danh-sách-lệnh-đầy-đủ)
- [🔐 Bảo mật](#-bảo-mật)
- [🗄️ Cơ sở dữ liệu](#️-cơ-sở-dữ-liệu)

<br>

## ✨ Tính năng

<table>
<tr>
<td width="50%" valign="top">

### 💰 Kinh tế
| Lệnh | Mô tả |
|---|---|
| `/daily` | Điểm danh, có streak thưởng thêm |
| `/balance` | Xem số dư |
| `/top` | Bảng xếp hạng |
| `/transfer` | Chuyển tiền |
| `/work` | Làm việc kiếm tiền |
| `/shop` `/buy` | Cửa hàng vật phẩm |

</td>
<td width="50%" valign="top">

### 🎮 Giải trí
| Lệnh | Mô tả |
|---|---|
| `/taixiu` | Tài Xỉu — Modal + Button + đếm ngược |
| `/baucua` | Bầu Cua Tôm Cá — chọn nhiều con |
| `/coinflip` | Tung đồng xu có cược |
| `/rollfun` `/flipfun` | Vui, không cược |

</td>
</tr>
<tr>
<td width="50%" valign="top">

### 🔑 Từ khóa
| Lệnh | Mô tả |
|---|---|
| `/setkeyword` | Tạo từ khóa tự động phản hồi |
| `/delkeyword` | Xóa từ khóa |
| `/listkeyword` | Xem danh sách |

</td>
<td width="50%" valign="top">

### ⚙️ Cài đặt <sub>(Admin)</sub>
| Lệnh | Mô tả |
|---|---|
| `/setwelcome` | Kênh chào mừng |
| `/setgoodbye` | Kênh tạm biệt |
| `/setvoicelog` | Kênh log voice |
| `/setcurrency` | Đổi tên tiền tệ |

</td>
</tr>
</table>

**ℹ️ Thông tin & Tiện ích:** `/serverinfo` · `/userinfo` · `/botinfo` · `/ping` · `/avatar` · `/roll` · `/flip` · `/help`

<br>

## 🚀 Hướng dẫn cài đặt

**1. Clone / tải project về máy**

**2. Cài đặt thư viện phụ thuộc**
```bash
pip install -r requirements.txt
```

**3. Cấu hình biến môi trường** — sao chép `.env.example` thành `.env`:
```env
DISCORD_TOKEN=token_bot_cua_ban
DEV_GUILD_ID=id_server_dung_de_test
```
| Biến | Ghi chú |
|---|---|
| `DISCORD_TOKEN` | Lấy tại [Discord Developer Portal](https://discord.com/developers/applications) |
| `DEV_GUILD_ID` | *(tùy chọn)* ID server test — để trống sẽ đồng bộ lệnh toàn cục (mất tới ~1 giờ) |

**4. Quyền bot (Bot Permissions)** khi mời vào server:

`Send Messages` · `Manage Messages` · `Use Slash Commands` · `Connect` · `Speak` · `View Channels` · `Moderate Members`

**5. Bật Privileged Gateway Intents** trong Developer Portal:

`Server Members Intent` · `Message Content Intent`

**6. Chạy bot**
```bash
python main.py
```

<br>

## 📂 Cấu trúc thư mục

```
loop-on-in-one/
├── cogs/
│   ├── economy.py       # Hệ thống kinh tế
│   ├── fun.py            # Game giải trí / cờ bạc ảo
│   ├── help.py            # Lệnh trợ giúp
│   ├── info.py             # Thông tin server/user/bot
│   ├── keyword.py           # Từ khóa tự động phản hồi
│   ├── settings.py           # Cài đặt server (Admin)
│   └── utility.py              # Tiện ích chung
├── database/
│   ├── __init__.py
│   └── db_manager.py            # Quản lý CSDL SQLite (aiosqlite)
├── utils/
│   └── helpers.py                 # Hàm tiện ích dùng chung
├── .env.example
├── .gitignore
├── config.json                      # Cấu hình mặc định
├── main.py                           # Điểm khởi động bot
├── README.md
└── requirements.txt
```

<br>

## 📋 Danh sách lệnh đầy đủ

<details>
<summary><b>Xem toàn bộ 27 lệnh</b></summary>

| Lệnh | Mô tả |
|------|-------|
| `/daily` | Điểm danh nhận thưởng |
| `/balance [user]` | Xem số dư |
| `/top` | Bảng xếp hạng |
| `/transfer <user> <amount>` | Chuyển tiền |
| `/work` | Làm việc kiếm tiền |
| `/shop` | Xem cửa hàng |
| `/buy <item>` | Mua vật phẩm |
| `/taixiu` | Chơi Tài Xỉu |
| `/baucua` | Chơi Bầu Cua |
| `/coinflip <amount> <choice>` | Tung đồng xu cược |
| `/rollfun` | Xúc xắc vui |
| `/flipfun` | Đồng xu vui |
| `/setkeyword <keyword> <response>` | Tạo từ khóa |
| `/delkeyword <keyword>` | Xóa từ khóa |
| `/listkeyword` | Danh sách từ khóa |
| `/setwelcome <channel>` | [Admin] Kênh chào mừng |
| `/setgoodbye <channel>` | [Admin] Kênh tạm biệt |
| `/setvoicelog <channel>` | [Admin] Kênh log voice |
| `/setcurrency <name>` | [Admin] Đổi tên tiền tệ |
| `/serverinfo` | Thông tin server |
| `/userinfo [user]` | Thông tin user |
| `/botinfo` | Thông tin bot |
| `/ping` | Độ trễ bot |
| `/avatar [user]` | Xem avatar |
| `/roll` | Xúc xắc 1-6 |
| `/flip` | Tung đồng xu |
| `/help` | Danh sách lệnh |

</details>

<br>

## 🔐 Bảo mật

- ✅ Toàn bộ lệnh trong `settings.py` yêu cầu quyền **Administrator**
- ✅ Không có lệnh `exec`/`eval` hay bất kỳ cơ chế thực thi code tùy ý nào
- ✅ Dữ liệu người dùng lưu cục bộ trong SQLite (`bot.db`), không gửi ra ngoài

<br>

## 🗄️ Cơ sở dữ liệu

Bot dùng **SQLite** thông qua `aiosqlite`, tự động tạo file `bot.db` và các bảng cần thiết khi khởi động lần đầu. Không cần cài đặt server database riêng.

<br>

## 📝 Giấy phép

Dự án sử dụng tự do cho mục đích cá nhân/học tập.

<div align="center">

---

Made with Noel Nguyen for the Discord community

</div>
