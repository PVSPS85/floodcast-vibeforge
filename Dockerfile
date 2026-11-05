FROM python:3.11-slim

WORKDIR /app

# Install system dependencies required for LightGBM, CatBoost, and compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy repository source code
COPY . /app

# Default execution entrypoint
CMD ["python", "solution.py"]
