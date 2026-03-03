FROM python:3.10-slim

WORKDIR /app

# Install system dependencies including libGL
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgl1-mesa-glx \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Expose port
EXPOSE 7860

# Start server
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "7860"]