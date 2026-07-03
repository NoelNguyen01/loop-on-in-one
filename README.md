<div align="center">

# 🎲 Loop On In One

### Discord Bot đa năng — Kinh tế ảo · Game giải trí · Tự động hóa · Quản lý server

![Version](https://img.shields.io/badge/Version-1.0.0-5865F2?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python)
![discord.py](https://img.shields.io/badge/discord.py-2.3%2B-5865F2?style=for-the-badge&logo=discord)
![Status](https://img.shields.io/badge/Status-Active-57F287?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-FEE75C?style=for-the-badge)

</div>

---

## 📋 Mục lục
- [🎯 Tổng quan](#-tổng-quan)
- [📊 Test Report](#-test-report)
- [✨ Danh sách lệnh](#-danh-sách-lệnh)
- [🚀 Cài đặt](#-cài-đặt)
- [📂 Cấu trúc](#-cấu-trúc)
- [🗄️ Database](#️-database)
- [🐛 Troubleshooting](#-troubleshooting)

---

## 🎯 Tổng quan

**Loop On In One** là Discord bot đa năng với kiến trúc module hóa, sử dụng SQLite làm cơ sở dữ liệu.

> ⚠️ **Lưu ý:** Tiền tệ trong bot là tiền ảo, chỉ phục vụ giải trí, không có giá trị thực tế.

---

## 📊 Test Report

### ✅ Test Cases

| ID | Test Case | Module | Result | Note |
|----|-----------|--------|--------|------|
| TC-01 | `.ldl` nhận thưởng daily | Economy | ✅ PASS | Streak + bonus đúng |
| TC-02 | `.ldl` không cho nhận lại trong 24h | Economy | ✅ PASS | Hiện time còn lại |
| TC-03 | `.lblc` hiển thị đúng số dư | Economy | ✅ PASS | Có avatar + thống kê |
| TC-04 | `.lt` sắp xếp top đúng | Economy | ✅ PASS | Top 10 người giàu |
| TC-05 | `.lrfr` chuyển tiền thành công | Economy | ✅ PASS | Trừ/cộng đúng |
| TC-06 | `.lrfr` không cho tự chuyển | Economy | ✅ PASS | Báo lỗi |
| TC-07 | `.lrfr` không đủ tiền | Economy | ✅ PASS | Báo insufficient |
| TC-08 | `.lw` nhận 50-300 coins | Economy | ✅ PASS | Random đúng |
| TC-09 | `.lh` hiển thị shop | Economy | ✅ PASS | Đúng format |
| TC-10 | `.lb` mua item thành công | Economy | ✅ PASS | Trừ tiền đúng |
| TC-11 | `.lb` item không tồn tại | Economy | ✅ PASS | Báo lỗi |
| TC-12 | `.ltx` cược Tài đúng | Fun | ✅ PASS | X2 tiền |
| TC-13 | `.ltx` cược Xỉu đúng | Fun | ✅ PASS | X2 tiền |
| TC-14 | `.ltx` cược sai | Fun | ✅ PASS | Mất tiền |
| TC-15 | `.ltx` không đủ tiền | Fun | ✅ PASS | Báo lỗi |
| TC-16 | `.lbc` cược 1 con trúng | Fun | ✅ PASS | Tính thưởng đúng |
| TC-17 | `.lbc` cược nhiều con | Fun | ✅ PASS | Tổng thưởng đúng |
| TC-18 | `.lbc` cược không trúng | Fun | ✅ PASS | Mất tiền |
| TC-19 | `.lcl` cược đúng | Fun | ✅ PASS | X2 tiền |
| TC-20 | `.lcl` cược sai | Fun | ✅ PASS | Mất tiền |
| TC-21 | `.ls` tạo từ khóa mới | Keyword | ✅ PASS | Lưu DB |
| TC-22 | `.ls` từ khóa trùng | Keyword | ✅ PASS | Báo đã tồn tại |
| TC-23 | `.ld` xóa từ khóa của mình | Keyword | ✅ PASS | Xóa thành công |
| TC-24 | `.ld` xóa từ khóa người khác (không admin) | Keyword | ✅ PASS | Từ chối |
| TC-25 | `.llt` hiển thị danh sách | Keyword | ✅ PASS | Đúng thứ tự |
| TC-26 | Auto-response trigger | Keyword | ✅ PASS | Phản hồi đúng |
| TC-27 | `.lswcm` đặt kênh welcome | Settings | ✅ PASS | Lưu DB |
| TC-28 | `.lsgb` đặt kênh goodbye | Settings | ✅ PASS | Lưu DB |
| TC-29 | `.lsvcl` đặt kênh voice log | Settings | ✅ PASS | Lưu DB |
| TC-30 | `.lscrc` đổi tên tiền tệ | Settings | ✅ PASS | Hiển thị đúng |
| TC-31 | Welcome message khi join | Settings | ✅ PASS | Gửi đúng kênh |
| TC-32 | Goodbye message khi leave | Settings | ✅ PASS | Gửi đúng kênh |
| TC-33 | Voice log vào/ra kênh | Settings | ✅ PASS | Ghi log đúng |
| TC-34 | `.lp` ping hiển thị độ trễ | Utility | ✅ PASS | Hiển thị ms |
| TC-35 | `.lvt` hiển thị avatar | Utility | ✅ PASS | Avatar đúng |
| TC-36 | `.lr` random 1-6 | Utility | ✅ PASS | Đúng phạm vi |
| TC-37 | `.llp` random Sấp/Ngửa | Utility | ✅ PASS | Đúng 2 mặt |
| TC-38 | `.lsvrf` hiển thị server info | Info | ✅ PASS | Đúng thông tin |
| TC-39 | `.lsrf` hiển thị user info | Info | ✅ PASS | Đúng thông tin |
| TC-40 | `.lbtf` hiển thị bot info | Info | ✅ PASS | Đúng thông tin |

### 🐛 Bug Report

| ID | Severity | Module | Bug | Status | Fix |
|----|----------|--------|-----|--------|-----|
| BUG-01 | 🟡 Minor | Help | Help hiển thị lệnh với prefix `.l` thay vì `/` | ✅ Won't Fix | Đây là design (tên rút gọn) |
| BUG-02 | 🟢 Low | Fun | `.lrfn` và `.llf` không cooldown | ✅ Won't Fix | Cố ý (game vui) |
| BUG-03 | 🟡 Minor | Economy | `.lh` không lưu item đã mua | ✅ Fixed | Thêm bảng `inventory` + lệnh `/inventory`, `/buy` giờ chặn mua trùng danh hiệu |
| BUG-04 | 🔴 Major | Help | `/help` liệt kê nhóm "Nối từ" (`.ltt`/`.ltp`/`.ldm`) nhưng tính năng này chưa từng được cài đặt — `cogs/wordchain.py` chỉ là bản sao lỗi của `keyword.py`, không được load trong `main.py` | ✅ Đã xây dựng thật | Viết lại `wordchain.py` với game Nối Từ hoạt động thật (VI/EN), đăng ký cog trong `main.py` |
| BUG-05 | 🟢 Low | Config | `config.json["embed_color"]` được khai báo nhưng không nơi nào đọc, đổi màu không có tác dụng | ✅ Fixed | `helpers.py` giờ đọc màu này làm `COLOR_DEFAULT` |
| BUG-06 | 🟢 Low | Logging | `utils/logging_config.py` (log có màu/icon) được viết sẵn nhưng `main.py` không gọi tới, dùng `basicConfig` thô thay thế | ✅ Fixed | `main.py` giờ gọi `setup_logging()` |

### 📈 Performance

| Metric | Value | Status |
|--------|-------|--------|
| Response Time | < 500ms | 🟢 Good |
| DB Query | < 100ms | 🟢 Good |
| Memory | ~50MB | 🟢 Optimal |
| CPU | ~5% | 🟢 Optimal |

---

## ✨ Danh sách lệnh

> 💡 **Lưu ý:** Các lệnh hiển thị là tên rút gọn, vẫn gõ bằng slash command (`/`) như bình thường trên Discord.

### 💰 Kinh tế (`economy.py`)

| Lệnh | Tên đầy đủ | Mô tả | Cooldown |
|------|-----------|-------|----------|
| `.ldl` | `/daily` | Điểm danh nhận thưởng + streak | 24h |
| `.lblc` | `/balance` | Xem số dư + thống kê | - |
| `.lt` | `/top` | Bảng xếp hạng top 10 | - |
| `.lrfr` | `/transfer` | Chuyển tiền cho người khác | 5s |
| `.lw` | `/work` | Làm việc kiếm 50-300 coins | 60s |
| `.lh` | `/shop` | Xem cửa hàng vật phẩm | - |
| `.lb` | `/buy` | Mua vật phẩm từ shop | 5s |
| `.lkho` | `/inventory` | Xem túi đồ vật phẩm đã mua | - |

### 🎮 Game & Giải trí (`fun.py`)

| Lệnh | Tên đầy đủ | Mô tả | Cooldown |
|------|-----------|-------|----------|
| `.ltx` | `/taixiu` | Tài Xỉu có cược | 5s |
| `.lbc` | `/baucua` | Bầu Cua Tôm Cá | 5s |
| `.lcl` | `/coinflip` | Tung đồng xu có cược | 5s |
| `.lrfn` | `/rollfun` | Tung xí ngầu vui | - |
| `.llf` | `/flipfun` | Tung đồng xu vui | - |

### 🔑 Từ khóa (`keyword.py`)

| Lệnh | Tên đầy đủ | Mô tả | Quyền |
|------|-----------|-------|-------|
| `.ls` | `/keyword set` | Tạo từ khóa phản hồi | Admin |
| `.ld` | `/keyword del` | Xóa từ khóa | Creator/Admin |
| `.llt` | `/keyword list` | Xem danh sách từ khóa | Everyone |

### ⚙️ Cài đặt (`settings.py`)

| Lệnh | Tên đầy đủ | Mô tả | Quyền |
|------|-----------|-------|-------|
| `.lswcm` | `/setwelcome` | Kênh chào mừng | Admin |
| `.lsgb` | `/setgoodbye` | Kênh tạm biệt | Admin |
| `.lsvcl` | `/setvoicelog` | Kênh log voice | Admin |
| `.lscrc` | `/setcurrency` | Đổi tên tiền tệ | Admin |

### ℹ️ Thông tin (`info.py`)

| Lệnh | Tên đầy đủ | Mô tả |
|------|-----------|-------|
| `.lsvrf` | `/serverinfo` | Thông tin server |
| `.lsrf` | `/userinfo` | Thông tin user |
| `.lbtf` | `/botinfo` | Thông tin bot |

### 🔤 Nối từ (`wordchain.py`)

| Lệnh | Tên đầy đủ | Mô tả | Ghi chú |
|------|-----------|-------|---------|
| `.ltt` | `/noitu start` | Bắt đầu ván nối từ (chọn Tiếng Việt/English) | Chơi bằng cách gõ từ thẳng vào kênh |
| `.ltp` | `/noitu stop` | Dừng ván nối từ trong kênh | Chỉ người tạo ván hoặc Admin |
| `.ldm` | `/noitu score` | Xem bảng điểm ván nối từ hiện tại | Điểm reset khi ván kết thúc |

### 🛠️ Tiện ích (`utility.py`)

| Lệnh | Tên đầy đủ | Mô tả |
|------|-----------|-------|
| `.lp` | `/ping` | Kiểm tra độ trễ |
| `.lvt` | `/avatar` | Xem avatar |
| `.lr` | `/roll` | Tung xí ngầu 1-6 |
| `.llp` | `/flip` | Tung đồng xu |
| `.lhlp` | `/help` | Danh sách lệnh |

---

## 🚀 Cài đặt

### Yêu cầu hệ thống
- Python >= 3.8
- pip >= 21.0

### Bước 1: Clone và cài dependencies
```bash
git clone <repo-url>
cd loop-on-in-one
pip install -r requirements.txt
```

### Bước 2: Cấu hình .env
```bash
cp .env.example .env
```

Mở file `.env` và điền:
```env
DISCORD_TOKEN=token_của_bạn
DEV_GUILD_ID=id_server_test  # Để trống nếu muốn global
```

### Bước 3: Chạy bot
```bash
python main.py
```

### Quyền cần thiết
| Permission | Mục đích |
|------------|----------|
| Send Messages | Gửi tin nhắn |
| Embed Links | Hiển thị embed |
| Use Slash Commands | Sử dụng lệnh slash |
| Connect | Voice features |
| Speak | Voice features |
| View Channels | Xem kênh |

### Intents cần bật
- ✅ Server Members Intent
- ✅ Message Content Intent

---

## 📂 Cấu trúc

```
loop-on-in-one/
├── cogs/
│   ├── economy.py       # 💰 Kinh tế
│   ├── fun.py           # 🎮 Game
│   ├── keyword.py       # 🔑 Từ khóa
│   ├── settings.py      # ⚙️ Cài đặt
│   ├── info.py          # ℹ️ Thông tin
│   ├── utility.py       # 🛠️ Tiện ích
│   ├── wordchain.py     # 🔤 Nối từ
│   └── help.py          # 📖 Trợ giúp
├── database/
│   └── db_manager.py    # SQLite handler
├── utils/
│   ├── helpers.py       # Helper functions
│   └── logging_config.py # Logging
├── config.json          # Cấu hình
├── .env.example         # Env mẫu
├── main.py              # Entry point
└── requirements.txt     # Dependencies
```

---

## 🗄️ Database

### users
| Column | Type | Description |
|--------|------|-------------|
| user_id | TEXT | Discord user ID |
| guild_id | TEXT | Server ID |
| balance | INTEGER | Số dư |
| daily_streak | INTEGER | Streak điểm danh |
| last_daily | INTEGER | Timestamp cuối |
| total_wins | INTEGER | Số lần thắng |
| total_losses | INTEGER | Số lần thua |

### keywords
| Column | Type | Description |
|--------|------|-------------|
| guild_id | TEXT | Server ID |
| keyword | TEXT | Từ khóa |
| response | TEXT | Phản hồi |
| created_by | TEXT | Người tạo |
| usage_count | INTEGER | Số lần dùng |

### guild_settings
| Column | Type | Description |
|--------|------|-------------|
| guild_id | TEXT | Server ID (PK) |
| welcome_channel | TEXT | Kênh welcome |
| goodbye_channel | TEXT | Kênh goodbye |
| voicelog_channel | TEXT | Kênh voice log |
| currency_name | TEXT | Tên tiền tệ |

### voice_logs
| Column | Type | Description |
|--------|------|-------------|
| user_id | TEXT | User ID |
| guild_id | TEXT | Server ID |
| channel_name | TEXT | Tên kênh voice |
| join_time | INTEGER | Thời gian vào |
| leave_time | INTEGER | Thời gian rời |
| duration | INTEGER | Thời gian ở lại |

### inventory
| Column | Type | Description |
|--------|------|-------------|
| user_id | TEXT | Discord user ID |
| guild_id | TEXT | Server ID |
| item_id | TEXT | Mã vật phẩm (khớp với `SHOP_ITEMS` trong `economy.py`) |
| quantity | INTEGER | Số lượng sở hữu |
| purchased_at | INTEGER | Timestamp lần mua gần nhất |

---

## 🐛 Troubleshooting

### Lỗi: Không tìm thấy .env
```bash
cp .env.example .env
```

### Lỗi: Slash command không hiển thị
- Kiểm tra bot có quyền `Use Slash Commands`
- Đợi 1-2h nếu chạy global
- Bật Privileged Intents

### Lỗi: Token không hợp lệ
- Kiểm tra token trong `.env`
- Regenerate token nếu cần

---

## 🔐 Security

- ✅ Admin commands yêu cầu quyền Administrator
- ✅ Không có lệnh exec/eval
- ✅ Dữ liệu lưu local SQLite
- ✅ Token trong .env (không commit)

---

<div align="center">
Made with ❤️ by Noel Nguyen
</div>
