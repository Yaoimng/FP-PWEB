@echo off
rem Memastikan dependensi dan aplikasi terpasang dengan benar
echo Memeriksa dependensi...
pip install -r requirements.txt

rem Menjalankan aplikasi Flask
echo Menjalankan aplikasi...
set FLASK_APP=app.py
set FLASK_ENV=development
python app.py
