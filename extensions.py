from flask import Flask, jsonify, request
from flask_bcrypt import Bcrypt
from flask_cors import CORS
import mysql.connector
import os
from dotenv import load_dotenv
from functools import wraps
import jwt
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Initialize Flask app and extensions
app = Flask(__name__)
CORS(app)
bcrypt = Bcrypt(app)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['UPLOAD_FOLDER'] = 'static/uploads/covers'

# Database connection helper
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
