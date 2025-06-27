import os
from flask import Flask, jsonify, request, send_from_directory, send_file
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta
import jwt
import mysql.connector

# Import extensions
from extensions import app, bcrypt, get_db_connection, token_required

# --- ROUTE UTAMA ---
@app.route('/')
def index():
    return send_file('src/frontend/index.html')

# --- ROUTE UNTUK FILE FRONTEND ---
@app.route('/<path:path>')
def serve_frontend(path):
    # Mencoba mengirim file dari folder frontend
    try:
        return send_file(f'src/frontend/{path}')
    except:
        return "File tidak ditemukan", 404

# --- ROUTE UNTUK FILE STATIS (CSS, JS, dll) ---
@app.route('/css/<path:filename>')
def serve_css(filename):
    return send_from_directory('src/frontend/css', filename)

@app.route('/js/<path:filename>')
def serve_js(filename):
    return send_from_directory('src/frontend/js', filename)

# --- ROUTE UNTUK MENYAJIKAN GAMBAR ---
@app.route('/uploads/covers/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# --- API UNTUK PENGGUNA (USERS) ---
@app.route('/api/register', methods=['POST'])
def register_user():
    data = request.get_json()
    nama = data.get('nama')
    email = data.get('email')
    password = data.get('password')
    if not nama or not email or not password:
        return jsonify({"status": "error", "message": "Data tidak lengkap"}), 400
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    conn = get_db_connection()
    if conn is None: return jsonify({"status": "error", "message": "Koneksi database gagal"}), 500
    try:
        cursor = conn.cursor()
        # Saat registrasi, kita tidak perlu memasukkan 'role' karena sudah ada nilai default di DB
        sql_query = "INSERT INTO users (nama, email, password) VALUES (%s, %s, %s)"
        cursor.execute(sql_query, (nama, email, hashed_password))
        conn.commit()
        cursor.close()
        return jsonify({"status": "sukses", "message": "Registrasi pengguna berhasil!"}), 201
    except mysql.connector.Error as err:
        if err.errno == 1062: return jsonify({"status": "error", "message": "Email sudah terdaftar."}), 409
        else: return jsonify({"status": "error", "message": str(err)}), 500
    finally:
        if conn and conn.is_connected(): conn.close()
    
@app.route('/api/login', methods=['POST'])
def login_user():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({"status": "error", "message": "Email dan password harus diisi"}), 400
    conn = get_db_connection()
    if conn is None: return jsonify({"status": "error", "message": "Koneksi database gagal"}), 500
    try:
        cursor = conn.cursor(dictionary=True) 
        sql_query = "SELECT * FROM users WHERE email = %s"
        cursor.execute(sql_query, (email,))
        user = cursor.fetchone()
        cursor.close()
        
        if user and bcrypt.check_password_hash(user['password'], password):
            # Pastikan kolom 'role' ada sebelum membuat token
            user_role = user.get('role', 'anggota') # Default ke 'anggota' jika tidak ada
            token = jwt.encode({
                'sub': user['id'],
                'role': user_role,
                'iat': datetime.utcnow(),
                'exp': datetime.utcnow() + timedelta(minutes=60)
            }, app.config['JWT_SECRET_KEY'], algorithm="HS256")
            return jsonify({"status": "sukses", "message": "Login berhasil!", "token": token})
        else:
            return jsonify({"status": "error", "message": "Email atau password salah"}), 401
    except Exception as e: # Tangkap semua jenis error untuk debugging
        print(f"Error di /api/login: {e}")
        return jsonify({"status": "error", "message": "Terjadi error di server."}), 500
    finally:
        if conn and conn.is_connected(): conn.close()

@app.route('/api/profile', methods=['GET'])
@token_required()
def get_user_profile(current_user):
    return jsonify({"status": "sukses", "user": current_user})


# --- MENDAFTARKAN SEMUA BLUEPRINT ---
# Impor blueprint setelah semua definisi
from src.books.routes import books_bp
from src.borrowings.routes import borrowings_bp

# Mendaftarkan blueprint
app.register_blueprint(books_bp)
app.register_blueprint(borrowings_bp)


# --- MENJALANKAN APLIKASI ---
if __name__ == '__main__':
    # Jalankan migrasi database
    from migrate import migrate
    migrate()
    
    # Jalankan aplikasi
    port = int(os.environ.get('PORT', 7860))
    app.run(host='0.0.0.0', port=port, debug=False)