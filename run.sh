#!/bin/bash

# Memastikan dependensi dan aplikasi terpasang dengan benar
echo "Memeriksa dependensi..."
pip install -r requirements.txt

# Menjalankan aplikasi Flask
echo "Menjalankan aplikasi..."
export FLASK_APP=app.py
export FLASK_ENV=production
python app.py
