@echo off
echo === MIGRASI DATA BUKU KE RAILWAY ===
echo.
echo Script ini akan memigrasikan data buku dari database lokal ke database Railway.
echo Pastikan Anda sudah mengisi kredensial Railway di file .env.railway
echo.

REM Cek apakah file .env.railway ada
if not exist .env.railway (
    echo File .env.railway tidak ditemukan!
    echo Mohon buat file tersebut dengan kredensial Railway Anda.
    echo Anda dapat menggunakan template dari .env.railway.example
    pause
    exit /b 1
)

REM Cek apakah .env.railway sudah diisi
findstr /C:"RAILWAY_DB_HOST=" .env.railway | findstr /V /C:"RAILWAY_DB_HOST=$" /C:"RAILWAY_DB_HOST=" > nul
if errorlevel 1 (
    echo Kredensial Railway belum diisi di file .env.railway!
    echo Mohon isi kredensial Railway Anda terlebih dahulu.
    pause
    exit /b 1
)

REM Salin .env.railway ke .env.temp
copy /Y .env.railway .env.temp > nul

REM Salin .env asli (jika ada)
if exist .env (
    copy /Y .env .env.backup > nul
    echo File .env di-backup ke .env.backup
)

REM Gunakan .env.railway sebagai .env
copy /Y .env.railway .env > nul
echo Menggunakan kredensial Railway untuk migrasi...

REM Jalankan skrip migrasi
echo.
echo Menjalankan migrasi...
echo.
python migrate_books.py

REM Kembalikan .env asli
if exist .env.backup (
    copy /Y .env.backup .env > nul
    echo.
    echo File .env asli dikembalikan.
    del .env.backup > nul
)

REM Hapus file .env.temp
if exist .env.temp (
    del .env.temp > nul
)

echo.
echo Migrasi selesai!
echo.
pause
