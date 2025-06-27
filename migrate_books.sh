#!/bin/bash

echo "=== MIGRASI DATA BUKU KE RAILWAY ==="
echo ""
echo "Script ini akan memigrasikan data buku dari database lokal ke database Railway."
echo "Pastikan Anda sudah mengisi kredensial Railway di file .env.railway"
echo ""

# Cek apakah file .env.railway ada
if [ ! -f .env.railway ]; then
    echo "File .env.railway tidak ditemukan!"
    echo "Mohon buat file tersebut dengan kredensial Railway Anda."
    echo "Anda dapat menggunakan template dari .env.railway.example"
    exit 1
fi

# Cek apakah .env.railway sudah diisi
if ! grep -q "RAILWAY_DB_HOST=" .env.railway || grep -q "RAILWAY_DB_HOST=$" .env.railway; then
    echo "Kredensial Railway belum diisi di file .env.railway!"
    echo "Mohon isi kredensial Railway Anda terlebih dahulu."
    exit 1
fi

# Salin .env asli (jika ada)
if [ -f .env ]; then
    cp .env .env.backup
    echo "File .env di-backup ke .env.backup"
fi

# Gunakan .env.railway sebagai .env
cp .env.railway .env
echo "Menggunakan kredensial Railway untuk migrasi..."

# Jalankan skrip migrasi
echo ""
echo "Menjalankan migrasi..."
echo ""
python migrate_books.py

# Kembalikan .env asli
if [ -f .env.backup ]; then
    cp .env.backup .env
    echo ""
    echo "File .env asli dikembalikan."
    rm .env.backup
fi

echo ""
echo "Migrasi selesai!"
echo ""
