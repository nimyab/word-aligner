FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements-docker.txt .

# Create a virtual environment and install dependencies
RUN python -m venv /venv && \
    /venv/bin/pip install --no-cache-dir --upgrade pip && \
    # Устанавливаем pytorch для CPU
    /venv/bin/pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu && \
    # Устанавливаем transformers без дополнительных зависимостей
    /venv/bin/pip install --no-cache-dir -r requirements-docker.txt && \
    # Принудительно указываем использование CPU для всех модулей
    echo "export CUDA_VISIBLE_DEVICES=-1" >> /venv/bin/activate

# Second stage build - использование более легкого образа
FROM python:3.11-slim AS final

WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    # Отключаем GPU для PyTorch
    CUDA_VISIBLE_DEVICES="-1" \
    # Отключаем JIT-компиляцию PyTorch
    PYTORCH_JIT=0

# Copy virtual environment from builder
COPY --from=builder /venv /venv

# Add the virtual environment to PATH
ENV PATH="/venv/bin:$PATH"

# Copy application code
COPY main.py word_aligner.py ./

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
