---
title: minimal-browser-screenshot-experiment
emoji: 💻
colorFrom: blue
colorTo: red
sdk: docker
app_file: app/server.py
pinned: false
---

# Minimal Browser Screenshot Experiment

This web application allows taking screenshots of websites using a headless browser and displaying them directly in the user interface.

## Features

- Simple and responsive web interface
- URL input with default value pointing to Open LLM Leaderboard
- Screenshot capture via Playwright (Chromium browser)
- Display of results in the interface

## Technologies Used

- **Backend**: FastAPI, Playwright
- **Frontend**: HTML/JS with Tailwind CSS
- **Dependency Management**: Poetry
- **Deployment**: Docker, Hugging Face Spaces

## Local Installation

### Prerequisites

- Python 3.10+
- Poetry
- Docker (optional)

### Installation with Poetry

```bash
# Clone the repository
git clone [repo-url]
cd minimal-browser-screenshot-experiment

# Install dependencies
poetry install

# Install Playwright browsers
poetry run playwright install chromium
poetry run playwright install-deps chromium

# Launch the application
poetry run uvicorn app.server:app --host 0.0.0.0 --port 7860
```

### Using Docker

```bash
# Build the Docker image
docker build -t minimal-browser-screenshot .

# Run the container
docker run -p 7860:7860 minimal-browser-screenshot
```

## Deployment on Hugging Face Spaces

This application is designed to be easily deployed on a Hugging Face Space.

1. Create a new Docker-type Space
2. Associate this GitHub repository with your Space
3. The Space will automatically use the provided Dockerfile to build and deploy the application

## Usage

1. Access the application through your browser
2. Enter the URL of the site you want to screenshot (default: Open LLM Leaderboard)
3. Click "Take a screenshot"
4. Wait a few seconds for the headless browser to load the page and take the screenshot
5. The screenshot appears in the interface
