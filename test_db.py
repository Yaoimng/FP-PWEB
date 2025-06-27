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

# Set API_BASE_URL based on environment variable or default to production
if os.getenv('FLASK_ENV') == 'development':
    API_BASE_URL = 'http://localhost:5000'
else:
    API_BASE_URL = 'https://fp-pweb-production.up.railway.app'