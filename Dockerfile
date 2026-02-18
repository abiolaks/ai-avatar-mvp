FROM python:3.10-slim

# Install system dependencies
# portaudio19-dev is for sounddevice
# ffmpeg is for audio/video processing
# libgl1-mesa-glx, libsm6, libxext6, libxrender-dev are for opencv and SadTalker
RUN apt-get update && apt-get install -y \
    build-essential \
    portaudio19-dev \
    ffmpeg \
    libgl1-mesa-glx \
    libsm6 \
    libxext6 \
    libxrender-dev \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first to leverage cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories for outputs
RUN mkdir -p outputs/videos

# Environment variables
ENV PYTHONUNBUFFERED=1

# Command to run the application
CMD ["python", "main.py"]
