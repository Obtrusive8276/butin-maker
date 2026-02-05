FROM python:3.11-slim

WORKDIR /app

# Install MediaInfo
RUN apt-get update && apt-get install -y \
    mediainfo \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create directories
RUN mkdir -p /app/data /app/output /data /config

EXPOSE 8000

CMD ["python", "run.py"]
