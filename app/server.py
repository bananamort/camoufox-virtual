import os
import asyncio
import logging
import pathlib
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.browser import start_instance, stop_instance, is_instance_running

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Camoufox Interactive Browser Instance")

BASE_DIR = pathlib.Path(__file__).parent.parent
templates_path = BASE_DIR / "templates"
static_path = BASE_DIR / "static"

templates = Jinja2Templates(directory=str(templates_path))
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")


@app.api_route("/", methods=["GET", "HEAD"], response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(request=request, name="instance.html")


@app.api_route("/instance", methods=["GET", "HEAD"], response_class=HTMLResponse)
async def read_instance(request: Request):
    return templates.TemplateResponse(request=request, name="instance.html")


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/api/instance/status")
async def get_status():
    status = "running" if is_instance_running() else "stopped"
    return {"status": status}


@app.post("/api/instance/start")
async def api_start():
    return start_instance()


@app.post("/api/instance/stop")
async def api_stop():
    return stop_instance()


@app.websocket("/instance/websockify")
async def websocket_vnc_proxy(websocket: WebSocket):
    if not is_instance_running():
        await websocket.close(code=1000, reason="Browser not running")
        return

    subprotocols = websocket.headers.get("sec-websocket-protocol", "").split(",")
    subprotocol = "binary" if "binary" in [s.strip() for s in subprotocols] else None
    
    await websocket.accept(subprotocol=subprotocol)

    try:
        reader, writer = await asyncio.open_connection("127.0.0.1", 5900)
    except Exception as e:
        logger.error("Failed to connect to local VNC port 5900: %s", e)
        await websocket.close()
        return

    async def client_to_vnc():
        try:
            while True:
                data = await websocket.receive_bytes()
                writer.write(data)
                await writer.drain()
        except Exception:
            pass

    async def vnc_to_client():
        try:
            while True:
                data = await reader.read(8192)
                if not data:
                    break
                await websocket.send_bytes(data)
        except Exception:
            pass

    try:
        await asyncio.gather(client_to_vnc(), vnc_to_client())
    except Exception:
        pass
    finally:
        writer.close()
        try:
            await writer.wait_closed()
        except Exception:
            pass
        try:
            await websocket.close()
        except Exception:
            pass