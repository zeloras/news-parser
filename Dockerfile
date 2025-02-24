FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    fonts-liberation \
    fontconfig \
    libfreetype6 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright and browsers as root
RUN playwright install-deps && \
    playwright install && \
    chmod -R 777 /root/.cache

# Create necessary directories and set permissions
RUN mkdir -p logs data/chroma data/cache && \
    chmod -R 777 /app

# Create non-root user and set up Playwright cache
RUN useradd -m -u 1000 appuser && \
    mkdir -p /home/appuser/.cache && \
    cp -r /root/.cache/ms-playwright /home/appuser/.cache/ && \
    chown -R appuser:appuser /home/appuser && \
    chown -R appuser:appuser /app

COPY --chown=appuser:appuser src/ /app/src/
COPY pytest.ini /app/
COPY .coveragerc /app/
# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"] 