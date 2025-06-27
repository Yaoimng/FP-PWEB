#!/bin/bash

# Pastikan direktori upload ada
mkdir -p static/uploads/covers
chmod -R 777 static/uploads/covers

# Mulai aplikasi
python app.py
