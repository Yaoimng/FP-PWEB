---
title: FP PWEB
emoji: 🐨
colorFrom: purple
colorTo: yellow
sdk: docker
pinned: false
---
<<<<<<< HEAD

# Aplikasi Perpustakaan

Aplikasi REST API perpustakaan menggunakan Flask dan MySQL.

## API Endpoints

### Autentikasi
- **POST /api/register** - Mendaftar pengguna baru
- **POST /api/login** - Login untuk mendapatkan token
- **GET /api/profile** - Mendapatkan profil pengguna

### Buku
- **GET /api/books** - Mendapatkan semua buku
- **GET /api/books/{id}** - Mendapatkan detail buku berdasarkan ID
- **POST /api/books** - Menambah buku baru (admin)
- **PUT /api/books/{id}** - Memperbarui buku (admin)
- **DELETE /api/books/{id}** - Menghapus buku (admin)

### Peminjaman
- **POST /api/borrow/{book_id}** - Meminjam buku
- **GET /api/my-borrowings** - Melihat peminjaman sendiri
- **POST /api/return/{borrow_id}** - Mengembalikan buku

## Teknologi

- Flask
- MySQL
- JWT Authentication
- Flask-CORS
- Flask-Bcrypt
=======
>>>>>>> dc3b6bff6e39bfd99d9e96debfd1d0fcafef6417
