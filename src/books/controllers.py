import os
from flask import request, jsonify
from werkzeug.utils import secure_filename
from uuid import uuid4

# Impor dari extensions bukan dari app
from extensions import app, get_db_connection
import mysql.connector

# --- KONFIGURASI UNTUK UPLOAD ---
# Mendefinisikan lokasi folder untuk menyimpan gambar sampul
UPLOAD_FOLDER = 'static/uploads/covers'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Jenis file gambar yang diizinkan
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Fungsi bantu untuk memeriksa apakah ekstensi file diizinkan
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- FUNGSI-FUNGSI CONTROLLER ---

# Ganti fungsi get_all_books Anda dengan ini
def get_all_books():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        # Query ini hanya mengambil buku yang statusnya 'tersedia'
        cursor.execute("SELECT * FROM books WHERE status = 'tersedia' ORDER BY id DESC")
        books = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({"status": "sukses", "data": books})
    except Exception as e:
        return jsonify({"status": "error", "message": "Gagal mengambil data buku: " + str(e)}), 500
def get_book_by_id(book_id):
    # Fungsi ini tidak kita ubah, sudah bekerja dengan baik
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM books WHERE id = %s", (book_id,))
        book = cursor.fetchone()
        cursor.close()
        conn.close()
        if book:
            return jsonify({"status": "sukses", "data": book})
        else:
            return jsonify({"status": "error", "message": "Buku tidak ditemukan"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": "Gagal mengambil data buku: " + str(e)}), 500


# --- FUNGSI INI DIGANTI TOTAL DENGAN VERSI BARU UNTUK UPLOAD GAMBAR ---
# Di dalam file src/books/controllers.py
def add_new_book():
    if 'cover_image' not in request.files:
        return jsonify({'status': 'error', 'message': 'Bagian file gambar sampul tidak ditemukan'}), 400
    
    file = request.files['cover_image']

    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'Tidak ada file gambar yang dipilih'}), 400

    if file and allowed_file(file.filename):
        try:
            # --- LOGIKA BARU UNTUK NAMA FILE YANG LEBIH AMAN ---
            # Ambil ekstensi file, contoh: 'jpg'
            extension = file.filename.rsplit('.', 1)[1].lower()
            # Buat nama file baru yang bersih menggunakan UUID dan ekstensi
            unique_filename = str(uuid4()) + '.' + extension
            # ----------------------------------------------------

            # Simpan file dengan nama baru yang bersih
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
            
            # Ambil data form lainnya
            judul = request.form['judul']
            penulis = request.form['penulis']
            penerbit = request.form['penerbit']
            tahun_terbit = int(request.form['tahun_terbit'])
            jumlah_stok = int(request.form['jumlah_stok'])
            isbn = request.form.get('isbn', '')
            sinopsis = request.form.get('sinopsis', '')
            
            # Simpan nama file yang bersih ini ke database
            conn = get_db_connection()
            cursor = conn.cursor()
            sql_query = """
                INSERT INTO books (judul, penulis, penerbit, tahun_terbit, isbn, sinopsis, jumlah_stok, stok_tersedia, cover_image) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            book_data = (judul, penulis, penerbit, tahun_terbit, isbn, sinopsis, jumlah_stok, jumlah_stok, unique_filename)
            cursor.execute(sql_query, book_data)
            conn.commit()
            cursor.close()
            conn.close()
            
            return jsonify({"status": "sukses", "message": "Buku baru berhasil ditambahkan!"}), 201
        
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    else:
        return jsonify({'status': 'error', 'message': 'Jenis file tidak diizinkan'}), 400
    
# Ganti fungsi delete_book_by_id Anda dengan ini
def delete_book_by_id(book_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Perintah ini MENGUBAH STATUS, bukan menghapus baris. Ini adalah kuncinya.
        query = "UPDATE books SET status = 'diarsipkan' WHERE id = %s"
        cursor.execute(query, (book_id,))
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"status": "error", "message": "Buku dengan ID tersebut tidak ditemukan."}), 404

        cursor.close()
        conn.close()
        return jsonify({"status": "sukses", "message": f"Buku berhasil diarsipkan."}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

def update_book_by_id(book_id):
    # Fungsi ini tidak kita ubah agar fitur edit yang sudah ada tidak rusak
    # (Update gambar akan menjadi fitur terpisah nanti)
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "Request body tidak boleh kosong"}), 400
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT jumlah_stok, stok_tersedia FROM books WHERE id = %s", (book_id,))
        old_book_data = cursor.fetchone()
        if not old_book_data:
            cursor.close()
            conn.close()
            return jsonify({"status": "error", "message": "Buku tidak ditemukan"}), 404
        old_total_stock = old_book_data['jumlah_stok']
        old_available_stock = old_book_data['stok_tersedia']
        books_on_loan = old_total_stock - old_available_stock
        new_total_stock = int(data.get('jumlah_stok'))
        new_available_stock = new_total_stock - books_on_loan
        if new_available_stock < 0:
            cursor.close()
            conn.close()
            return jsonify({"status": "error", "message": f"Update gagal. Ada {books_on_loan} buku yang sedang dipinjam."}), 400
        judul = data.get('judul')
        penulis = data.get('penulis')
        penerbit = data.get('penerbit')
        tahun_terbit = data.get('tahun_terbit')
        isbn = data.get('isbn')
        sinopsis = data.get('sinopsis')
        query = "UPDATE books SET judul = %s, penulis = %s, penerbit = %s, tahun_terbit = %s, jumlah_stok = %s, stok_tersedia = %s, isbn = %s, sinopsis = %s WHERE id = %s"
        values = (judul, penulis, penerbit, tahun_terbit, new_total_stock, new_available_stock, isbn, sinopsis, book_id)
        cursor.execute(query, values)
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"status": "sukses", "message": "Buku berhasil diupdate!"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
