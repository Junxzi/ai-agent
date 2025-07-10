# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirement files and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Default command
CMD ["python", "main.py"]
