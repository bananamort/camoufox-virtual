FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for X11, VNC, Openbox, wmctrl, xdotool, and Firefox/Camoufox
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    gnupg \
    curl \
    unzip \
    xvfb \
    openbox \
    x11vnc \
    wmctrl \
    xdotool \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    dbus-x11 \
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
    libgtk-3-0 \
    libdbus-glib-1-2 \
    libxt6 \
    libpci3 \
    fonts-noto-color-emoji \
    fonts-freefont-ttf \
    libharfbuzz-icu0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Fetch Camoufox browser
RUN python -m camoufox fetch

# Copy application files
COPY . .

EXPOSE 7860

# Shell form allows reading Railway's $PORT env var dynamically (defaults to 7860)
CMD ["sh", "-c", "uvicorn app.server:app --host 0.0.0.0 --port ${PORT:-7860}"]
