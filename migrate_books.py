import os
import mysql.connector
from dotenv import load_dotenv
import shutil
from datetime import datetime

# Load environment variables
load_dotenv()

def get_local_db_connection():
    """Membuat koneksi ke database lokal"""
    return mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        database=os.getenv('DB_NAME', 'db_perpustakaan')
    )

def get_railway_db_connection():
    """Membuat koneksi ke database Railway"""
    # Prioritaskan variabel Railway jika tersedia
    host = os.environ.get('MYSQLHOST') or os.environ.get('RAILWAY_DB_HOST')
    user = os.environ.get('MYSQLUSER') or os.environ.get('RAILWAY_DB_USER')
    password = os.environ.get('MYSQLPASSWORD') or os.environ.get('RAILWAY_DB_PASSWORD')
    database = os.environ.get('MYSQL_DATABASE') or os.environ.get('MYSQLDATABASE') or os.environ.get('RAILWAY_DB_NAME')
    
    # Pastikan kita memiliki kredensial yang diperlukan
    if not all([host, user, password, database]):
        print("WARNING: Variabel lingkungan Railway tidak ditemukan.")
        print("Silakan atur variabel lingkungan berikut untuk database Railway:")
        print("RAILWAY_DB_HOST, RAILWAY_DB_USER, RAILWAY_DB_PASSWORD, RAILWAY_DB_NAME")
        print("\nAtau variabel lingkungan Railway asli:")
        print("MYSQLHOST, MYSQLUSER, MYSQLPASSWORD, MYSQLDATABASE")
        return None
    
    return mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )

def check_books_schema(conn):
    """Memeriksa skema tabel books"""
    try:
        cursor = conn.cursor()
        cursor.execute("DESCRIBE books")
        columns = cursor.fetchall()
        cursor.close()
        
        column_names = [col[0] for col in columns]
        required_columns = ['id', 'judul', 'penulis', 'penerbit', 'tahun_terbit', 'isbn', 
                           'sinopsis', 'jumlah_stok', 'stok_tersedia', 'cover_image', 'status']
        
        missing_columns = [col for col in required_columns if col not in column_names]
        
        if missing_columns:
            print(f"WARNING: Kolom yang hilang di tabel books: {', '.join(missing_columns)}")
            return False
        return True
    except Exception as e:
        print(f"Error saat memeriksa skema books: {e}")
        return False

def migrate_books_data():
    """Memigrasikan data buku dari database lokal ke Railway"""
    # Koneksi ke database lokal
    local_conn = get_local_db_connection()
    if not local_conn:
        print("Gagal terhubung ke database lokal.")
        return False
    
    # Koneksi ke database Railway
    railway_conn = get_railway_db_connection()
    if not railway_conn:
        print("Gagal terhubung ke database Railway.")
        local_conn.close()
        return False
    
    try:
        # Periksa skema di kedua database
        if not check_books_schema(local_conn) or not check_books_schema(railway_conn):
            print("Skema tabel books tidak sesuai. Pastikan kedua database memiliki struktur yang sama.")
            print("Coba jalankan migrate.py terlebih dahulu untuk membuat skema yang diperlukan.")
            return False
        
        # Ambil data dari database lokal
        local_cursor = local_conn.cursor(dictionary=True)
        local_cursor.execute("SELECT * FROM books WHERE status != 'diarsipkan' OR status IS NULL")
        books = local_cursor.fetchall()
        
        if not books:
            print("Tidak ada data buku yang ditemukan di database lokal.")
            return False
        
        print(f"Ditemukan {len(books)} buku untuk migrasi.")
        
        # Siapkan insert untuk database Railway
        railway_cursor = railway_conn.cursor()
        
        # Periksa apakah buku sudah ada di database Railway
        for book in books:
            railway_cursor.execute("SELECT id FROM books WHERE judul = %s AND penulis = %s", 
                                  (book['judul'], book['penulis']))
            existing_book = railway_cursor.fetchone()
            
            if existing_book:
                print(f"Buku sudah ada di Railway: {book['judul']} oleh {book['penulis']}")
                continue
            
            # Siapkan data untuk insert
            # Pastikan status default untuk buku yang dimigrasikan
            if 'status' not in book or book['status'] is None:
                book['status'] = 'tersedia'
            
            # Periksa apakah stok_tersedia ada
            if 'stok_tersedia' not in book or book['stok_tersedia'] is None:
                book['stok_tersedia'] = book['jumlah_stok'] if 'jumlah_stok' in book else 1
            
            # Periksa cover_image
            cover_image = book.get('cover_image', '') or book.get('cover_path', '')
            
            # Siapkan query insert
            sql = """
                INSERT INTO books 
                (judul, penulis, penerbit, tahun_terbit, isbn, sinopsis, jumlah_stok, stok_tersedia, cover_image, status) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            # Data untuk query
            data = (
                book['judul'],
                book['penulis'],
                book['penerbit'],
                book['tahun_terbit'],
                book.get('isbn', ''),
                book.get('sinopsis', '') or book.get('deskripsi', ''),
                book.get('jumlah_stok', 1),
                book.get('stok_tersedia', book.get('jumlah_stok', 1)),
                cover_image,
                book['status']
            )
            
            # Execute query
            try:
                railway_cursor.execute(sql, data)
                railway_conn.commit()
                print(f"Berhasil memigrasikan: {book['judul']} oleh {book['penulis']}")
                
                # Copy file gambar cover jika ada
                if cover_image and os.path.exists(f"static/uploads/covers/{cover_image}"):
                    print(f"Cover image found: {cover_image}")
                else:
                    print(f"Cover image tidak ditemukan: {cover_image}")
            except Exception as e:
                print(f"Gagal memigrasikan buku {book['judul']}: {str(e)}")
        
        print("\nMigrasi selesai!")
        return True
    
    except Exception as e:
        print(f"Error saat migrasi: {str(e)}")
        return False
    
    finally:
        # Tutup koneksi
        if local_conn:
            local_conn.close()
        if railway_conn:
            railway_conn.close()

if __name__ == "__main__":
    print("=== MULAI MIGRASI DATA BUKU ===")
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 30)
    
    success = migrate_books_data()
    
    if success:
        print("\n✅ MIGRASI BERHASIL")
    else:
        print("\n❌ MIGRASI GAGAL")
    
    print("=" * 30)
