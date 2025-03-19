FROM python:3.10-slim

WORKDIR /app

# Create non-root user
RUN useradd -m -u 1000 user

# Install system dependencies and Chrome for Playwright
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    curl \
    && pip install --upgrade pip \
    && pip install poetry

# Copy poetry configuration and README
COPY pyproject.toml poetry.lock* README.md ./

# Install Python dependencies using Poetry
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --only main

# Install Playwright browsers
RUN playwright install chromium && \
    playwright install-deps chromium

# Create directories
RUN mkdir -p static templates screenshots && \
    chown -R user:user /app

# Copy application code
COPY app /app/app
COPY templates /app/templates
COPY static /app/static

# Environment variables
ENV PORT=7860 \
    HOST=0.0.0.0 \
    PYTHONPATH=/app

# Switch to non-root user
USER user

# Expose the port
EXPOSE 7860

# Start command
CMD ["uvicorn", "app.server:app", "--host", "0.0.0.0", "--port", "7860"] 