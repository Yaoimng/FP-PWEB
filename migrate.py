import os
import mysql.connector
from extensions import get_db_connection

def migrate():
    conn = get_db_connection()
    if conn is None:
        print("Koneksi database gagal")
        return
    
    cursor = conn.cursor()
    
    # Membuat tabel users jika belum ada
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nama VARCHAR(100) NOT NULL,
        email VARCHAR(100) NOT NULL UNIQUE,
        password VARCHAR(100) NOT NULL,
        role ENUM('admin', 'anggota') DEFAULT 'anggota'
    )
    ''')
    
    # Membuat tabel books jika belum ada
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS books (
        id INT AUTO_INCREMENT PRIMARY KEY,
        judul VARCHAR(255) NOT NULL,
        penulis VARCHAR(100) NOT NULL,
        penerbit VARCHAR(100) NOT NULL,
        tahun_terbit INT,
        isbn VARCHAR(50),
        sinopsis TEXT,
        jumlah_stok INT DEFAULT 1,
        stok_tersedia INT DEFAULT 1,
        cover_image VARCHAR(255),
        status VARCHAR(20) DEFAULT 'tersedia',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Membuat tabel borrowings jika belum ada
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS borrowings (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        book_id INT NOT NULL,
        tanggal_pinjam DATE NOT NULL,
        tanggal_kembali DATE,
        status ENUM('dipinjam', 'dikembalikan', 'terlambat') DEFAULT 'dipinjam',
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (book_id) REFERENCES books(id)
    )
    ''')
    
    # Membuat indeks untuk user_id jika belum ada
    try:
        cursor.execute("SHOW INDEX FROM borrowings WHERE Key_name = 'idx_user_id'")
        result = cursor.fetchone()
        if not result:
            cursor.execute('CREATE INDEX idx_user_id ON borrowings(user_id)')
            print("Indeks idx_user_id dibuat")
    except Exception as e:
        print(f"Error saat memeriksa/membuat indeks idx_user_id: {e}")
    
    # Membuat indeks untuk book_id jika belum ada
    try:
        cursor.execute("SHOW INDEX FROM borrowings WHERE Key_name = 'idx_book_id'")
        result = cursor.fetchone()
        if not result:
            cursor.execute('CREATE INDEX idx_book_id ON borrowings(book_id)')
            print("Indeks idx_book_id dibuat")
    except Exception as e:
        print(f"Error saat memeriksa/membuat indeks idx_book_id: {e}")
    
    # Add status column to books if it doesn't exist
    try:
        cursor.execute("SHOW COLUMNS FROM books LIKE 'status'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE books ADD COLUMN status VARCHAR(20) DEFAULT 'tersedia'")
            print("Added status column to books table")
    except Exception as e:
        print(f"Error adding status column: {e}")
        
    # Add isbn column to books if it doesn't exist
    try:
        cursor.execute("SHOW COLUMNS FROM books LIKE 'isbn'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE books ADD COLUMN isbn VARCHAR(50)")
            print("Added isbn column to books table")
    except Exception as e:
        print(f"Error adding isbn column: {e}")
        
    # Add sinopsis column to books if it doesn't exist
    try:
        cursor.execute("SHOW COLUMNS FROM books LIKE 'sinopsis'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE books ADD COLUMN sinopsis TEXT")
            print("Added sinopsis column to books table")
    except Exception as e:
        print(f"Error adding sinopsis column: {e}")
        
    # Add jumlah_stok column to books if it doesn't exist
    try:
        cursor.execute("SHOW COLUMNS FROM books LIKE 'jumlah_stok'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE books ADD COLUMN jumlah_stok INT DEFAULT 1")
            print("Added jumlah_stok column to books table")
    except Exception as e:
        print(f"Error adding jumlah_stok column: {e}")
        
    # Add stok_tersedia column to books if it doesn't exist
    try:
        cursor.execute("SHOW COLUMNS FROM books LIKE 'stok_tersedia'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE books ADD COLUMN stok_tersedia INT DEFAULT 1")
            print("Added stok_tersedia column to books table")
    except Exception as e:
        print(f"Error adding stok_tersedia column: {e}")
        
    # Rename cover_path to cover_image if needed
    try:
        cursor.execute("SHOW COLUMNS FROM books LIKE 'cover_path'")
        if cursor.fetchone():
            cursor.execute("SHOW COLUMNS FROM books LIKE 'cover_image'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE books CHANGE COLUMN cover_path cover_image VARCHAR(255)")
                print("Renamed cover_path to cover_image")
    except Exception as e:
        print(f"Error renaming cover_path column: {e}")
    
    # Commit perubahan
    conn.commit()
    
    # Buat user admin default jika belum ada
    cursor.execute("SELECT * FROM users WHERE email = 'admin@perpustakaan.com'")
    if not cursor.fetchone():
        from flask_bcrypt import Bcrypt
        bcrypt = Bcrypt()
        hashed_password = bcrypt.generate_password_hash('admin123').decode('utf-8')
        
        cursor.execute('''
        INSERT INTO users (nama, email, password, role)
        VALUES ('Administrator', 'admin@perpustakaan.com', %s, 'admin')
        ''', (hashed_password,))
        conn.commit()
        print("User admin default dibuat")
    
    cursor.close()
    conn.close()
    print("Migrasi database berhasil")

if __name__ == "__main__":
    migrate()