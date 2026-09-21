FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system build dependencies for C-extensions (TgCrypto, lxml, Pillow)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    libjpeg-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose default HTTP healthcheck port and MCP server port
EXPOSE 3000 8000

# Docker native container healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD python -c "import urllib.request, os; port = os.environ.get('PORT', '3000'); urllib.request.urlopen(f'http://127.0.0.1:{port}/health')" || exit 1

# Start the Telegram bot
CMD ["python", "main.py"]
