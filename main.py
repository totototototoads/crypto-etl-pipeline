import requests
import json
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine
import os
# Dùng biến môi trường hoặc placeholder an toàn khi đẩy lên GitHub


# --- BƯỚC 1: EXTRACT (Trích xuất Top 50 đồng coin từ API) ---
def extract():
    print("1. Đang gọi API lấy dữ liệu Top 50 đồng coin...")
    url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=50&page=1"
    response = requests.get(url)
    response.raise_for_status() # Báo lỗi ngay nếu API sập hoặc chặn
    du_lieu = response.json()

    # Lưu bản gốc vào thư mục data/
    with open("data/raw_data.json", "w", encoding="utf-8") as f:
        json.dump(du_lieu, f, indent=4)
    print(f"   -> Đã lưu {len(du_lieu)} đồng coin vào data/raw_data.json")
    return du_lieu

# --- BƯỚC 2: TRANSFORM (Làm sạch & Biến đổi dữ liệu) ---
def transform(du_lieu):
    print("2. Đang làm sạch và biến đổi dữ liệu bằng Pandas...")
    df = pd.DataFrame(du_lieu)

    # Chọn các cột quan trọng
    cac_cot = ["id", "symbol", "name", "current_price", "market_cap", "price_change_percentage_24h", "last_updated"]
    df_sach = df[cac_cot].copy()

    # Xử lý dữ liệu trống
    df_sach = df_sach.fillna(0)

    # Tạo cột giá VND và cột ghi nhận thời điểm chạy pipeline
    df_sach["price_vnd"] = df_sach["current_price"] * 25400
    df_sach["extracted_at"] = datetime.now()

    print("   -> Đã làm sạch dữ liệu xong!")
    return df_sach

# --- BƯỚC 3: LOAD (Đẩy vào PostgreSQL) ---
def load(df_sach):
    print("3. Đang nạp dữ liệu vào PostgreSQL...")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "your_postgres_password")
    ket_noi = create_engine(f"postgresql+psycopg://postgres:{DB_PASSWORD}@localhost:5432/crypto_db")

    # Dùng append để tích lũy lịch sử biến động giá sau mỗi lần chạy
    df_sach.to_sql("crypto_prices", ket_noi, if_exists="append", index=False)
    print("   -> THÀNH CÔNG! Dữ liệu đã được nạp vào bảng 'crypto_prices' trên PostgreSQL!")

# --- CHẠY TOÀN BỘ PIPELINE ---
if __name__ == "__main__":
    raw_data = extract()
    clean_df = transform(raw_data)
    load(clean_df)