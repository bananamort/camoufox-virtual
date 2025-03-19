import os
import asyncio
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from playwright.async_api import async_playwright
import uuid
import logging
import pathlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI()

# Determine base directory
BASE_DIR = pathlib.Path(__file__).parent.parent

# Set up templates and static files
templates_path = BASE_DIR / "templates"
static_path = BASE_DIR / "static"
screenshots_path = BASE_DIR / "screenshots"

templates = Jinja2Templates(directory=str(templates_path))
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Create screenshots directory if it doesn't exist
os.makedirs(str(screenshots_path), exist_ok=True)

# Mount the screenshots directory
app.mount("/screenshots", StaticFiles(directory=str(screenshots_path)), name="screenshots")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/take-screenshot")
async def take_screenshot(url: str = Form(...)):
    logger.info(f"Taking screenshot of URL: {url}")
    
    try:
        # Generate a unique filename
        filename = f"{uuid.uuid4()}.png"
        filepath = str(screenshots_path / filename)
        
        # Log browser executable paths
        logger.info(f"HOME env: {os.environ.get('HOME')}")
        logger.info(f"Current working directory: {os.getcwd()}")
        
        # Take the screenshot with Playwright
        async with async_playwright() as p:
            # Configuration adaptée pour l'environnement Docker
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--no-first-run',
                    '--no-zygote',
                    '--single-process',
                    '--disable-gpu'
                ],
                executable_path=None  # Utiliser le chemin par défaut
            )
            
            logger.info("Browser launched successfully")
            page = await browser.new_page(viewport={"width": 1280, "height": 720})
            
            try:
                logger.info(f"Navigating to URL: {url}")
                await page.goto(url, wait_until="networkidle", timeout=60000)
                logger.info("Navigation complete, taking screenshot")
                await page.screenshot(path=filepath)
                logger.info(f"Screenshot saved to {filepath}")
            except Exception as e:
                logger.error(f"Error during page navigation or screenshot: {str(e)}")
                raise
            finally:
                await browser.close()
                logger.info("Browser closed")
        
        return JSONResponse({
            "success": True,
            "screenshot_url": f"/screenshots/{filename}"
        })
    
    except Exception as e:
        logger.error(f"Error taking screenshot: {str(e)}")
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)

# Add a health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok"} 