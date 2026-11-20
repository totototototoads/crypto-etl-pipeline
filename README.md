# Crypto Data ETL Pipeline

Pipeline ETL bằng Python dùng để thu thập và lưu trữ dữ liệu thị trường tiền mã hóa.
Dự án lấy thông tin Top 50 đồng coin theo vốn hóa thị trường từ CoinGecko, biến đổi dữ liệu
bằng Pandas và nạp dữ liệu vào PostgreSQL để phục vụ việc theo dõi lịch sử giá.

## Chức năng chính

- **Extract:** Gọi CoinGecko Markets API để lấy dữ liệu Top 50 đồng coin theo vốn hóa.
- **Transform:** Chọn các trường quan trọng, xử lý giá trị trống, quy đổi giá USD sang VND
  theo tỷ giá cấu hình trong mã nguồn và thêm thời điểm chạy pipeline.
- **Load:** Ghi dữ liệu vào bảng `crypto_prices` trong PostgreSQL bằng chế độ `append`,
  giúp lưu lại lịch sử của nhiều lần chạy.
- **Raw data snapshot:** Lưu dữ liệu API thô vào `data/raw_data.json` để kiểm tra hoặc
  xử lý lại khi cần.

## Công nghệ sử dụng

- Python
- Requests — gọi CoinGecko API
- Pandas — làm sạch và biến đổi dữ liệu
- SQLAlchemy và Psycopg — kết nối, ghi dữ liệu vào PostgreSQL
- PostgreSQL — cơ sở dữ liệu đích

## Luồng dữ liệu

```text
CoinGecko API
      |
      v
data/raw_data.json  -->  Pandas transformation  -->  PostgreSQL.crypto_prices
```

## Cấu trúc dự án

```text
.
├── main.py                 # Mã nguồn pipeline ETL
├── requirements.txt        # Danh sách thư viện Python
├── data/
│   ├── raw_data.json       # Dữ liệu thô lấy từ CoinGecko
│   └── crypto_data.db      # Tệp dữ liệu cục bộ hiện có trong dự án
└── README.md
```

## Yêu cầu

- Python 3.10 trở lên
- PostgreSQL đang chạy tại `localhost:5432`
- Cơ sở dữ liệu `crypto_db`
- Tài khoản PostgreSQL có quyền ghi dữ liệu

## Cài đặt

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
# source .venv/bin/activate

pip install -r requirements.txt
```

Đặt mật khẩu PostgreSQL qua biến môi trường `DB_PASSWORD`:

```powershell
$env:DB_PASSWORD = "your_postgres_password"
```

Nếu không đặt biến môi trường, chương trình sẽ dùng giá trị mặc định
`your_postgres_password` trong mã nguồn; nên thay đổi cách này trước khi triển khai thực tế.

## Chạy pipeline

```bash
python main.py
```

Sau khi chạy thành công:

1. Dữ liệu thô được cập nhật tại `data/raw_data.json`.
2. Dữ liệu đã biến đổi được ghi vào bảng `crypto_prices` trong cơ sở dữ liệu `crypto_db`.

Các cột chính trong bảng gồm `id`, `symbol`, `name`, `current_price`, `market_cap`,
`price_change_percentage_24h`, `price_vnd`, `last_updated` và `extracted_at`.

## Lưu ý

- CoinGecko API có thể giới hạn tần suất gọi hoặc yêu cầu xử lý lỗi mạng khi chạy thường xuyên.
- Tỷ giá USD/VND hiện được đặt cố định trong `main.py`; nên đưa vào biến môi trường hoặc một
  nguồn tỷ giá riêng nếu cần độ chính xác theo thời gian thực.
- Pipeline sử dụng `append`, vì vậy mỗi lần chạy sẽ tạo thêm một bản ghi lịch sử thay vì ghi đè
  dữ liệu cũ.
