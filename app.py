import os
from flask import Flask, jsonify, request, send_from_directory
from dotenv import load_dotenv
from flask_bcrypt import Bcrypt
from flask_cors import CORS

# Import lain yang mungkin Anda butuhkan
from functools import wraps
import jwt
from datetime import datetime, timedelta
import mysql.connector

# --- INISIALISASI APLIKASI ---
load_dotenv()
app = Flask(__name__)
CORS(app)
bcrypt = Bcrypt(app)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')


# --- FUNGSI BANTU UNTUK KONEKSI DATABASE ---
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
            
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None


# --- DECORATOR UNTUK PROTEKSI TOKEN ---
def token_required(allowed_roles=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = None
            if 'x-access-token' in request.headers:
                token = request.headers['x-access-token']
            
            if not token:
                return jsonify({'message' : 'Token tidak ditemukan!'}), 401
            
            try: 
                data = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=["HS256"])
                
                conn = get_db_connection()
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT * FROM users WHERE id = %s", (data['sub'],))
                current_user = cursor.fetchone()
                cursor.close()
                conn.close()

                if not current_user:
                    return jsonify({'message' : 'Token tidak valid!'}), 401

                # Pastikan kolom 'role' ada sebelum mengaksesnya
                if 'role' in current_user and allowed_roles and current_user['role'] not in allowed_roles:
                    return jsonify({'message' : 'Tidak memiliki izin untuk mengakses sumber daya ini!'}), 403

            except jwt.ExpiredSignatureError:
                return jsonify({'message' : 'Token sudah kedaluwarsa!'}), 401
            except jwt.InvalidTokenError:
                return jsonify({'message' : 'Token tidak valid!'}), 401
            
            return f(current_user, *args, **kwargs)
        
        return decorated_function
    return decorator


# --- ROUTE UTAMA ---
@app.route('/')
def index():
    return "Halo! Server Flask untuk Perpustakaan sedang berjalan."

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
from src.books.routes import books_bp
from src.borrowings.routes import borrowings_bp

# PERBAIKAN FINAL: Menambahkan 'url_prefix' untuk konsistensi
app.register_blueprint(books_bp)
app.register_blueprint(borrowings_bp)


# --- MENJALANKAN APLIKASI ---
if __name__ == '__main__':
    app.run(debug=True)