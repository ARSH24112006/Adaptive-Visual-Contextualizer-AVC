FROM python:3.10-slim

# Install system tools needed for images and processing
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
# Using the CPU-only version makes the download 10x faster
RUN pip install --no-cache-dir --default-timeout=1000 -r requirements.txt

COPY . .

CMD ["python", "main.py"]