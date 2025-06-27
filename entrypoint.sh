#!/bin/bash

# Pastikan direktori upload ada
mkdir -p static/uploads/covers
chmod -R 777 static/uploads/covers

echo "Running database migrations..."
python migrate.py
echo "Starting the application..."
python app.py
