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
    
    # Tambahkan indeks
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_id ON borrowings(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_book_id ON borrowings(book_id)')
    
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
    
    cursor.close()
    conn.close()
    print("Migrasi database berhasil")

if __name__ == "__main__":
    migrate()