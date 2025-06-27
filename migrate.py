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
        deskripsi TEXT,
        stok INT DEFAULT 1,
        cover_path VARCHAR(255),
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