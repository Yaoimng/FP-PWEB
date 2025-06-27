# Migrasi Database dari Lokal ke Railway

## Latar Belakang
Ketika aplikasi diupload ke Railway, database lokal tidak otomatis dimigrasikan ke database Railway. Proses ini membutuhkan langkah manual untuk memastikan semua data buku dan pengguna berpindah dengan benar.

## Persiapan

1. **Pastikan kredensial Railway sudah benar**
   - Dapatkan informasi koneksi database MySQL dari dashboard Railway
   - Isi file `.env.railway` dengan informasi tersebut

2. **Pastikan database lokal dapat diakses**
   - File `.env` sudah berisi kredensial database lokal yang benar
   - Database lokal harus sudah berisi data buku yang ingin dimigrasikan

## Cara Menggunakan Tool Migrasi

### Untuk Pengguna Windows

1. Pastikan kredensial Railway sudah diisi di file `.env.railway`
2. Jalankan `migrate_books.bat` dengan klik dua kali atau melalui Command Prompt
3. Ikuti instruksi yang muncul di layar
4. Tunggu hingga proses migrasi selesai

### Untuk Pengguna Linux/Mac

1. Pastikan kredensial Railway sudah diisi di file `.env.railway`
2. Buka Terminal dan navigasi ke direktori proyek
3. Berikan izin eksekusi: `chmod +x migrate_books.sh`
4. Jalankan script: `./migrate_books.sh`
5. Ikuti instruksi yang muncul di layar
6. Tunggu hingga proses migrasi selesai

## Apa yang Dilakukan Tool Ini?

Tool migrasi ini melakukan:

1. Mengambil data buku dari database lokal
2. Memeriksa apakah buku sudah ada di database Railway (berdasarkan judul dan penulis)
3. Memigrasikan buku yang belum ada ke database Railway
4. Menyesuaikan struktur data agar kompatibel dengan skema database aplikasi terbaru

## Troubleshooting

### Masalah Koneksi ke Database Railway

Jika terjadi masalah koneksi ke database Railway:
- Pastikan informasi koneksi di `.env.railway` sudah benar
- Pastikan IP address Anda diizinkan mengakses database Railway
- Periksa apakah firewall lokal memblokir koneksi keluar

### Buku Tidak Muncul Setelah Migrasi

Jika buku tidak muncul setelah migrasi:
- Periksa apakah status buku diset ke 'tersedia'
- Pastikan kolom 'jumlah_stok' dan 'stok_tersedia' memiliki nilai yang valid
- Verifikasi bahwa gambar cover buku ada di direktori `static/uploads/covers/`

### Struktur Tabel Tidak Kompatibel

Jika terjadi error terkait struktur tabel:
- Jalankan `python migrate.py` terlebih dahulu di Railway untuk memastikan skema tabel sudah benar
- Pastikan database lokal juga menggunakan skema terbaru
