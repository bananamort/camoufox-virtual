FROM python:3.10-slim

WORKDIR /app

# Create non-root user
RUN useradd -m -u 1000 user

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    curl \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libx11-6 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    libatspi2.0-0 \
    && pip install --upgrade pip \
    && pip install poetry

# Copy poetry configuration
COPY pyproject.toml poetry.lock* ./

# Install Python dependencies using Poetry
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --only main --no-root

# Install Playwright browsers as root
RUN playwright install chromium && \
    playwright install-deps chromium

# Create directories and set permissions
RUN mkdir -p static templates screenshots /home/user/.cache && \
    chown -R user:user /app /home/user/.cache

# Copy application code
COPY app /app/app
COPY templates /app/templates
COPY static /app/static

# Make sure all files are owned by user
RUN chown -R user:user /app

# Environment variables
ENV PORT=7860 \
    HOST=0.0.0.0 \
    PYTHONPATH=/app \
    HOME=/home/user

# Switch to non-root user for running the app
USER user

# Expose the port
EXPOSE 7860

# Start command
CMD ["uvicorn", "app.server:app", "--host", "0.0.0.0", "--port", "7860"] 