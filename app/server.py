import os
import asyncio
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from playwright.async_api import async_playwright
import uuid
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI()

# Set up templates and static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
os.makedirs("screenshots", exist_ok=True)

# Mount the screenshots directory
app.mount("/screenshots", StaticFiles(directory="screenshots"), name="screenshots")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/take-screenshot")
async def take_screenshot(url: str = Form(...)):
    logger.info(f"Taking screenshot of URL: {url}")
    
    try:
        # Generate a unique filename
        filename = f"{uuid.uuid4()}.png"
        filepath = f"screenshots/{filename}"
        
        # Take the screenshot with Playwright
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(url, wait_until="networkidle")
            await page.screenshot(path=filepath)
            await browser.close()
        
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