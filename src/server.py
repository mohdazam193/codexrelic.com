import os
import asyncio
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles

# Core imports
from api.core.config import BASE_DIR
from api.core.logger import logger

# Routers
from api.routers import public, admin, news, telemetry
from api.tasks.tech_news import fetch_tech_news_task

app = FastAPI(title="codexrelic API (Modular)")

# ── HTTP Security Headers Middleware ──
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data: https:; "
        "connect-src 'self';"
    )
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

# ── Cache Control for Development ──
@app.middleware("http")
async def disable_cache_for_development(request: Request, call_next):
    response = await call_next(request)
    path = request.url.path.lower()
    if path.endswith((".html", ".css", ".js", ".png", ".jpg", ".svg")) or path == "/" or path == "/index.html":
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

# ── Include Modular Routers ──
app.include_router(public.router)
app.include_router(news.router)
app.include_router(telemetry.router)
app.include_router(admin.router)

# ── Startup Events ──
@app.on_event("startup")
async def startup_event():
    logger.info("Server starting up...")
    asyncio.create_task(fetch_tech_news_task())

# ── Serve Static Assets ──
app.mount("/assets", StaticFiles(directory=os.path.join(BASE_DIR, "public", "assets")), name="assets")

# Fallback to serve static root HTML files (must be defined LAST)
app.mount("/", StaticFiles(directory=os.path.join(BASE_DIR, "public"), html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
