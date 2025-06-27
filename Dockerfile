FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Create upload directory if it doesn't exist and set permissions
RUN mkdir -p static/uploads/covers && chmod -R 777 static/uploads

# Make entrypoint.sh executable
RUN chmod +x entrypoint.sh

# Expose the port the app runs on
EXPOSE 7860

# Command to run the application
CMD ["./entrypoint.sh"]