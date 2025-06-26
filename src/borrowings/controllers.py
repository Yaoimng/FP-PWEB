# Isi file: src/borrowings/controllers.py

from flask import jsonify
from app import get_db_connection
from datetime import date, timedelta
import mysql.connector

def borrow_a_book(current_user, book_id):
    # ... (kode dari sesi sebelumnya, tidak perlu diubah)
    conn = get_db_connection()
    if not conn:
        return jsonify({"status": "error", "message": "Koneksi database gagal"}), 500
    
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT stok_tersedia FROM books WHERE id = %s", (book_id,))
        book = cursor.fetchone()
        if not book:
            return jsonify({"status": "error", "message": "Buku tidak ditemukan."}), 404
        if book['stok_tersedia'] <= 0:
            return jsonify({"status": "error", "message": "Stok buku habis."}), 400

        update_stock_query = "UPDATE books SET stok_tersedia = stok_tersedia - 1 WHERE id = %s"
        cursor.execute(update_stock_query, (book_id,))
        
        id_anggota = current_user['id']
        tanggal_pinjam = date.today()
        tanggal_kembali = tanggal_pinjam + timedelta(days=7)

        add_borrowing_query = "INSERT INTO peminjaman (id_buku, id_anggota, tanggal_pinjam, tanggal_kembali) VALUES (%s, %s, %s, %s)"
        cursor.execute(add_borrowing_query, (book_id, id_anggota, tanggal_pinjam, tanggal_kembali))

        conn.commit()
        return jsonify({"status": "sukses", "message": "Buku berhasil dipinjam."}), 201
    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({"status": "error", "message": str(err)}), 500
    finally:
        cursor.close()
        conn.close()

# === FUNGSI BARU 1: Mengambil Peminjaman Saya ===
def get_my_borrowings(current_user):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Query JOIN untuk mengambil data dari tabel peminjaman dan tabel buku sekaligus
    query = """
        SELECT 
            p.id, 
            p.tanggal_pinjam, 
            p.tanggal_kembali, 
            b.judul, 
            b.penulis
        FROM peminjaman p
        JOIN books b ON p.id_buku = b.id
        WHERE p.id_anggota = %s AND p.status = 'Dipinjam'
    """
    cursor.execute(query, (current_user['id'],))
    borrowings = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return jsonify({"status": "sukses", "data": borrowings})

# === FUNGSI BARU 2: Mengembalikan Buku ===
def return_a_book(current_user, borrow_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Cek dulu apakah peminjaman ini milik pengguna yang sedang login
        cursor.execute("SELECT * FROM peminjaman WHERE id = %s AND id_anggota = %s", (borrow_id, current_user['id']))
        borrowing = cursor.fetchone()

        if not borrowing:
            return jsonify({"status": "error", "message": "Data peminjaman tidak ditemukan atau bukan milik Anda."}), 404

        # Update status peminjaman
        update_borrow_query = "UPDATE peminjaman SET status = 'Selesai', tanggal_pengembalian_aktual = %s WHERE id = %s"
        cursor.execute(update_borrow_query, (date.today(), borrow_id))

        # Tambah kembali stok buku
        update_stock_query = "UPDATE books SET stok_tersedia = stok_tersedia + 1 WHERE id = %s"
        cursor.execute(update_stock_query, (borrowing['id_buku'],))

        conn.commit()
        return jsonify({"status": "sukses", "message": "Buku berhasil dikembalikan."})

    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({"status": "error", "message": str(err)}), 500
    finally:
        cursor.close()
        conn.close()
