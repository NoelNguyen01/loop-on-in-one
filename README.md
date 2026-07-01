# 🔄 LOOP ON IN ONE

**Discord bot đa năng, tích hợp mọi tính năng quản trị mạnh mẽ trong một giải pháp duy nhất.**

> *"Loop On In One" - Vòng lặp của mọi tính năng, gói gọn trong một bot Discord hoàn hảo.*

Lấy cảm hứng từ Dyno và Mimu, LOOP ON IN ONE mang đến trải nghiệm quản trị server toàn diện, 
dễ tùy chỉnh và hoàn toàn miễn phí cho cộng đồng Việt Nam.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8%2B-green)
![Discord](https://img.shields.io/badge/discord.py-py-blueviolet)
![Status](https://img.shields.io/badge/status-active-brightgreen)

---

## 🎯 Tại sao tên là "LOOP ON IN ONE"?

- **LOOP** - Bot hoạt động liên tục, xử lý lệnh không ngừng nghỉ.
- **ON** - Luôn bật, luôn sẵn sàng phục vụ cộng đồng.
- **IN ONE** - Mọi tính năng cần thiết đều được tích hợp trong một bot duy nhất.

> Bạn không cần cài nhiều bot khác nhau. LOOP ON IN ONE là tất cả những gì bạn cần.

---

## ✨ Tính năng nổi bật

- 🛡️ **Quản trị viên**: Xóa tin nhắn hàng loạt, cảnh báo, cấm/kick thành viên (có log)
- 📊 **Tự động hóa**: Gửi tin nhắn chào mừng, thiết lập vai trò tự động
- 🛠️ **Tiện ích**: Tra cứu thông tin thành viên, máy chủ, tạo bình chọn nhanh
- 🇻🇳 **Hoàn toàn bằng tiếng Việt**: Giao diện và phản hồi thân thiện

---

## ⚙️ Cài đặt và chạy bot

### Yêu cầu
- Python 3.8 trở lên
- Tài khoản Discord (tạo bot tại [Discord Developer Portal](https://discord.com/developers/applications))

### Các bước thực hiện

```bash
# 1. Clone dự án
git clone https://github.com/NoelNguyen01/loop-on-in-one.git
cd loop-on-in-one

# 2. Tạo môi trường ảo (khuyến nghị)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Cài đặt thư viện
pip install -r requirements.txt

# 4. Cấu hình biến môi trường
cp .env.example .env
# Mở file .env và điền DISCORD_TOKEN của bạn

# 5. Chạy bot
python main.py
