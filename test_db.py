import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

print("Mencoba menghubungkan ke database...")
try:
    conn = mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )
    if conn.is_connected():
        print(">>> SUKSES! Koneksi ke database berhasil dibuat.")
    else:
        print(">>> GAGAL! Terhubung tapi tidak bisa mendapatkan koneksi aktif.")
    conn.close()
except mysql.connector.Error as err:
    print(f">>> GAGAL! Terjadi error koneksi: {err}")
except Exception as e:
    print(f">>> GAGAL! Terjadi error umum: {e}")