# Aplikasi Perpustakaan

Aplikasi pengelolaan perpustakaan berbasis web menggunakan Flask dan MySQL.

## Prasyarat

- Python 3.8 atau lebih tinggi
- MySQL Database

## Cara Menjalankan Aplikasi

### 1. Siapkan Virtual Environment

```bash
# Buat virtual environment
python -m venv venv

# Aktifkan virtual environment
# Windows
.\venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 2. Instal Dependensi

```bash
pip install -r requirements.txt
```

### 3. Siapkan Database

Pastikan database MySQL sudah berjalan dan siapkan file `.env` dengan konfigurasi berikut:

```
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=password_anda
DB_NAME=db_perpustakaan
JWT_SECRET_KEY=kunci_rahasia_anda
```

### 4. Jalankan Aplikasi

```bash
python app.py
```

Aplikasi akan berjalan di http://localhost:5000

## Struktur Aplikasi

```
PWEB/
├── app.py               # Aplikasi utama (route dan blueprint)
├── extensions.py        # Inisialisasi Flask, ekstensi, dan fungsi bantu
├── requirements.txt     # Dependensi
├── Dockerfile           # Konfigurasi Docker
└── src/
    ├── books/           # Modul untuk pengelolaan buku
    │   ├── controllers.py
    │   └── routes.py
    └── borrowings/      # Modul untuk pengelolaan peminjaman
        ├── controllers.py
        └── routes.py
```

## Menggunakan Docker

Untuk menjalankan aplikasi dengan Docker:

```bash
# Build image
docker build -t perpustakaan-app .

# Jalankan container
docker run -p 5000:5000 perpustakaan-app
```

## Deployment ke Hugging Face Spaces

Aplikasi ini sudah dikonfigurasi untuk deployment ke Hugging Face Spaces menggunakan GitHub Actions.
