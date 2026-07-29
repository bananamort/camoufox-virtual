# Minimal Camoufox Interactive Instance (Docker)

A standalone Docker application running a manually controllable Camoufox browser instance over the `/instance` URL path.

## Features

- **Interactive Remote Control**: Real-time VNC-over-WebSocket desktop streaming (mouse, keyboard, scrolling).
- **Simple UI**: Single-page web UI at `/instance` with Start and Stop buttons to control browser lifecycle on demand.
- **Camoufox Engine**: Anti-detect browser engine preconfigured with extensions support.

## Docker Usage

### Build the Image
```bash
docker build -t minimal-camoufox-experiment .
```

### Run the Container
```bash
docker run -d -p 7860:7860 --name camoufox-app minimal-camoufox-experiment
```

Access the interface at `http://localhost:7860/instance`.

## Local Setup (without Docker)

```bash
pip install -r requirements.txt
python -m camoufox fetch
uvicorn app.server:app --host 0.0.0.0 --port 7860
```