import os
import re
import time
import base64
import secrets
import bcrypt
import jwt
import logging
import json
import sys
import subprocess
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from datetime import datetime, timedelta
from collections import defaultdict
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from fastapi import FastAPI, HTTPException, Request, Response, Form, UploadFile, File, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pymongo import MongoClient
from dotenv import load_dotenv

# ── Structured JSON Logger Setup ──
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
        }
        if record.exc_info:
            log_record["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(log_record)

logger = logging.getLogger("codexrelic_api")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)

load_dotenv()

app = FastAPI(title="codexrelic API")

# ── Dynamic Workspace Paths ──
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

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

# ── JWT Configuration ──
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = 24

def create_jwt(username: str) -> str:
    """Issue a signed JWT valid for JWT_EXPIRE_HOURS."""
    if not JWT_SECRET:
        raise RuntimeError("JWT_SECRET environment variable is not configured.")
    payload = {
        "sub": username,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRE_HOURS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_jwt(token: str) -> bool:
    """Verify a JWT signature and expiry. Returns True if valid."""
    if not JWT_SECRET:
        return False
    try:
        jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return True
    except jwt.ExpiredSignatureError:
        return False
    except jwt.InvalidTokenError:
        return False

# ── Ed25519 Challenge Store (one-time use, 30-second TTL) ──
# nonce (base64) -> issued_at (unix timestamp)
_challenges: dict[str, float] = {}

# ── Simple In-Memory Rate Limiter for Login ──
class RateLimiter:
    def __init__(self, requests_limit: int, window_seconds: int):
        self.requests_limit = requests_limit
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)

    def is_allowed(self, key: str) -> bool:
        now = time.time()
        self.requests[key] = [t for t in self.requests[key] if now - t < self.window_seconds]
        if len(self.requests[key]) >= self.requests_limit:
            return False
        self.requests[key].append(now)
        return True

login_limiter = RateLimiter(requests_limit=5, window_seconds=60)

# Connect to MongoDB Atlas (fallback to local if URI not provided)
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

# ── Configure S3 Client (OCI Object Storage) ──
s3_client = boto3.client(
    's3',
    endpoint_url=os.getenv("AWS_ENDPOINT_URL_S3"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_DEFAULT_REGION", "ap-hyderabad-1"),
    config=Config(signature_version='s3v4')
)

DB_CONNECTED = False
db = None

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
    client.admin.command('ping')
    db = client.get_database("codexrelic")
    DB_CONNECTED = True
    logger.info("MongoDB Atlas connection verified.")
except Exception as e:
    redacted_uri = MONGO_URI
    if "@" in MONGO_URI:
        parts = MONGO_URI.split("@")
        scheme = parts[0].split("://")
        if len(scheme) == 2:
            redacted_uri = f"{scheme[0]}://****:****@{parts[-1]}"
    logger.error(f"Resiliency Warning: Failed to connect to MongoDB database at '{redacted_uri}'. Error detail: {e}")
    logger.warning("Server starting in resilient mode. Database-dependent endpoints will return default mocks.")

# ── Sessions are now stateless JWTs — no DB session store required ──

# ── Seed Admin User (Securely requiring env values) ──
def seed_admin():
    if not DB_CONNECTED or db is None:
        return
        
    admin_user = os.getenv("ADMIN_USER")
    admin_pass = os.getenv("ADMIN_PASS")
    admin_code = os.getenv("ADMIN_CODE")
    
    if not admin_user or not admin_pass or not admin_code:
        logger.warning("ADMIN_USER, ADMIN_PASS, or ADMIN_CODE environment variables are missing. Default seeds are skipped.")
        return
        
    users_col = db.get_collection("users")
    if users_col.count_documents({}) == 0:
        salt = bcrypt.gensalt()
        hashed_pass = bcrypt.hashpw(admin_pass.encode('utf-8'), salt)
        hashed_code = bcrypt.hashpw(admin_code.encode('utf-8'), salt)
        
        users_col.insert_one({
            "username": admin_user,
            "passkey_hash": hashed_pass.decode('utf-8'),
            "realm_code_hash": hashed_code.decode('utf-8')
        })
        logger.info(f"Seeding administrator user: username='{admin_user}'")

seed_admin()

# ── Authentication Helper Dependency (JWT-based, stateless) ──
def get_current_user(request: Request):
    token = request.cookies.get("session_token")
    if not token or not verify_jwt(token):
        raise HTTPException(status_code=401, detail="Unauthorized session")
    return token

# ── Challenge Endpoint (Ed25519 login, Step 1) ──
@app.get("/api/auth/challenge")
def get_challenge():
    """Issue a fresh one-time 32-byte nonce for Ed25519 challenge-response login."""
    nonce = secrets.token_bytes(32)
    nonce_b64 = base64.b64encode(nonce).decode()
    _challenges[nonce_b64] = time.time()
    # Evict expired challenges (> 30 seconds old)
    expired = [k for k, t in list(_challenges.items()) if time.time() - t > 30]
    for k in expired:
        del _challenges[k]
    return {"challenge": nonce_b64}

# ── Public APIs ──

@app.get("/api/movies")
def get_movies():
    movies = []
    if DB_CONNECTED and db is not None:
        try:
            movies_col = db.get_collection("movies")
            movies = list(movies_col.find({}, {"_id": 0}))
        except Exception as e:
            print(f"[!] Error querying movies collection: {e}")
            
    if not movies:
        movies = [
            {
                "title": "Interstellar (2014)",
                "director": "Christopher Nolan",
                "rating": 10.0,
                "genre": "sci-fi",
                "poster_url": "https://upload.wikimedia.org/wikipedia/en/b/bc/Interstellar_film_poster.jpg",
                "description": "Christopher Nolan's visual masterpiece. Hans Zimmer's organ score adds an almost gothic scale to the void of space.",
                "sre_analogy": {
                    "title": "Time Dilation",
                    "description": "Latency regression: 1 hour on Miller's planet is 7 years in callers' thread. Model your API timeouts!"
                }
            },
            {
                "title": "Inception (2010)",
                "director": "Christopher Nolan",
                "rating": 9.5,
                "genre": "thriller",
                "poster_url": "https://upload.wikimedia.org/wikipedia/en/2/2e/Inception_%282010%29_theatrical_poster.jpg",
                "description": "Architectural logic of dreams defined like code. City folding cinematography is stunning.",
                "sre_analogy": {
                    "title": "Virtualization",
                    "description": "Nested VMs (dream layers). A crash in a lower layer propagates up. Monitor base resources closely."
                }
            },
            {
                "title": "Blade Runner 2049 (2017)",
                "director": "Denis Villeneuve",
                "rating": 9.8,
                "genre": "sci-fi",
                "poster_url": "https://upload.wikimedia.org/wikipedia/en/9/9b/Blade_Runner_2049_poster.png",
                "description": "Denis Villeneuve visual masterpiece. Slow burn detailing memory relics and what makes a soul.",
                "sre_analogy": {
                    "title": "Containers",
                    "description": "Replicants are containers instantiated from a base immutable image. Drift defines their separate lifecycles."
                }
            },
            {
                "title": "2001: A Space Odyssey (1968)",
                "director": "Stanley Kubrick",
                "rating": 10.0,
                "genre": "philosophy",
                "poster_url": "https://upload.wikimedia.org/wikipedia/en/1/1c/2001_A_Space_Odyssey_%281968_theatrical_movie_poster%29.jpg",
                "description": "Kubrick's masterpiece. The monolith acts as a cosmic rulebook. HAL 9000 shows tragedy of system conflict.",
                "sre_analogy": {
                    "title": "Split-Brain",
                    "description": "HAL 9000 conflicting rules nervous breakdown. Partitioned cluster nodes thinking they are both master."
                }
            }
        ]
    return movies

@app.get("/api/blogs")
def get_blogs():
    blogs = []
    if DB_CONNECTED and db is not None:
        try:
            blogs_col = db.get_collection("blogs")
            blogs = list(blogs_col.find({}, {"_id": 0}))
        except Exception as e:
            print(f"[!] Error querying blogs collection: {e}")
            
    if not blogs:
        blogs = [
            {
                "title": "KubeCon India 2026: Key Telemetry and SRE Lessons",
                "slug": "kubecon-india-learnings",
                "category": "Conference Notes",
                "summary": "A comprehensive breakdown of key sessions at KubeCon India detailing eBPF auto-instrumentation and OTel pipelines.",
                "tags": ["Kubernetes", "OpenTelemetry", "eBPF"],
                "read_time": 6,
                "created_at": "2026-08-11"
            },
            {
                "title": "Lessons in Toil Elimination: Reducing Deployments from 50 to 10 Minutes",
                "slug": "automating-toil-mitratech",
                "category": "Case Studies",
                "summary": "Walkthrough of how I identified and removed redundant database loops and sync blockages in Mitratech's TAP deployment pipeline.",
                "tags": ["Automation", "FinOps", "SQL"],
                "read_time": 4,
                "created_at": "2026-07-24"
            }
        ]
    return blogs

# ── Authentication API (Ed25519 Challenge-Response + JWT) ──
@app.post("/api/login")
def login(
    request: Request,
    response: Response,
    username: str = Form(...),
    password: str = Form(...),
    challenge: str = Form(...),
    signature: str = Form(...),
):
    # ── 1. Rate limit by client IP ──
    client_ip = request.client.host if request.client else "unknown"
    if not login_limiter.is_allowed(client_ip):
        logger.warning(f"Login rate limit exceeded for IP: {client_ip}")
        raise HTTPException(status_code=429, detail="Too many login attempts. Please try again in a minute.")

    # ── 2. Validate challenge is fresh and one-time ──
    issued_at = _challenges.get(challenge)
    if issued_at is None or (time.time() - issued_at) > 30:
        raise HTTPException(status_code=401, detail="Authentication credentials invalid")
    del _challenges[challenge]  # One-time use — prevents replay attacks

    # ── 3. Verify Ed25519 signature ──
    pub_key_b64 = os.getenv("ADMIN_ED25519_PUBLIC_KEY")
    if not pub_key_b64:
        raise HTTPException(status_code=500, detail="Server authentication key not configured.")
    try:
        pub_key_bytes = base64.b64decode(pub_key_b64)
        public_key = Ed25519PublicKey.from_public_bytes(pub_key_bytes)
        message = f"{challenge}:{username}".encode()
        public_key.verify(base64.b64decode(signature), message)
    except Exception:
        raise HTTPException(status_code=401, detail="Authentication credentials invalid")

    # ── 4. Verify bcrypt password against DB (or env fallback) ──
    dev_user = os.getenv("ADMIN_USER")
    dev_pass = os.getenv("ADMIN_PASS")

    if DB_CONNECTED and db is not None:
        users_col = db.get_collection("users")
        user = users_col.find_one({"username": username})
        if not user:
            raise HTTPException(status_code=401, detail="Authentication credentials invalid")
        if not bcrypt.checkpw(password.encode('utf-8'), user["passkey_hash"].encode('utf-8')):
            raise HTTPException(status_code=401, detail="Authentication credentials invalid")
    else:
        # Resilient fallback: env-based verification when DB is offline
        if not dev_user or not dev_pass:
            logger.error("Administrative credentials not configured in environment.")
            raise HTTPException(status_code=500, detail="Administrative credentials not configured in environment.")
        if username != dev_user or password != dev_pass:
            logger.warning(f"Failed login attempt for user: {username} from IP: {client_ip} (fallback mode)")
            raise HTTPException(status_code=401, detail="Authentication credentials invalid")

    # ── 5. Issue stateless JWT — no DB write needed ──
    logger.info(f"Successful login for user: {username} from IP: {client_ip}")
    token = create_jwt(username)
    response.set_cookie(
        key="session_token",
        value=token,
        httponly=True,
        secure=True,
        samesite="lax",
        path="/",
        max_age=JWT_EXPIRE_HOURS * 3600,
    )
    return {"status": "authenticated", "redirect": "/admin/dashboard.html"}

# ── Protected Admin CMS APIs ──

@app.post("/api/admin/movies", dependencies=[Depends(get_current_user)])
def add_movie(
    title: str = Form(...),
    director: str = Form(...),
    rating: float = Form(...),
    genre: str = Form(...),
    poster_url: str = Form(...),
    description: str = Form(...),
    sre_title: str = Form(...),
    sre_desc: str = Form(...)
):
    if not DB_CONNECTED or db is None:
        raise HTTPException(status_code=503, detail="Write actions failed: Database is offline. Please configure MONGO_URI in .env")
        
    movies_col = db.get_collection("movies")
    movies_col.insert_one({
        "title": title,
        "director": director,
        "rating": rating,
        "genre": genre,
        "poster_url": poster_url,
        "description": description,
        "sre_analogy": {
            "title": sre_title,
            "description": sre_desc
        },
        "created_at": datetime.utcnow()
    })
    return {"status": "success", "message": "Movie document inserted into MongoDB Atlas!"}

@app.post("/api/admin/blogs", dependencies=[Depends(get_current_user)])
def add_blog(
    title: str = Form(...),
    category: str = Form(...),
    summary: str = Form(...),
    content: str = Form(...),
    tags: str = Form(...),
    read_time: int = Form(...)
):
    if not DB_CONNECTED or db is None:
        raise HTTPException(status_code=503, detail="Write actions failed: Database is offline. Please configure MONGO_URI in .env")

    blogs_col = db.get_collection("blogs")
    
    # ── Collision-Safe Slug Generation ──
    base_slug = re.sub(r'[^a-z0-9\s-]', '', title.lower())
    base_slug = re.sub(r'[\s-]+', '-', base_slug).strip('-')
    slug = base_slug
    counter = 1
    while blogs_col.count_documents({"slug": slug}) > 0:
        slug = f"{base_slug}-{counter}"
        counter += 1

    tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    
    blogs_col.insert_one({
        "title": title,
        "slug": slug,
        "category": category,
        "summary": summary,
        "content": content,
        "tags": tag_list,
        "read_time": read_time,
        "created_at": datetime.utcnow().strftime("%Y-%m-%d")
    })
    return {"status": "success", "message": "Blog post document inserted into MongoDB Atlas!"}

@app.post("/api/admin/resume", dependencies=[Depends(get_current_user)])
async def upload_resume(file: UploadFile = File(...)):
    if not (file.filename.endswith(".tex") or file.filename.endswith(".pdf")):
        raise HTTPException(status_code=400, detail="Invalid file type. Only .tex and .pdf are allowed.")
        
    # File size validation to prevent denial of service (DoS)
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB limit
    contents = await file.read(MAX_FILE_SIZE + 1)
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large. Maximum size is 5MB.")

    bucket_name = os.getenv("AWS_S3_BUCKET")
    if not bucket_name:
        raise HTTPException(status_code=500, detail="S3 Bucket not configured in environment.")
        
    try:
        app_env = os.getenv("APP_ENV", "dev")
        # Determine the key name based on extension (always save as resume.pdf or resume.tex)
        ext = file.filename.split('.')[-1]
        object_name = f"{app_env}/resume/resume.{ext}"
        
        # Upload to OCI Object Storage via S3 API
        s3_client.put_object(
            Bucket=bucket_name,
            Key=object_name,
            Body=contents,
            ContentType="application/pdf" if ext == "pdf" else "application/x-tex"
        )
    except ClientError as e:
        logger.error(f"S3 Upload failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload file to Object Storage.")
        
    return {"status": "success", "message": f"Successfully uploaded {object_name} to OCI Object Storage!"}

@app.get("/content/resume/{filename}")
async def download_resume(filename: str):
    if filename not in ["resume.pdf", "resume.tex"]:
        raise HTTPException(status_code=403, detail="Forbidden")
        
    bucket_name = os.getenv("AWS_S3_BUCKET")
    if not bucket_name:
        raise HTTPException(status_code=500, detail="S3 Bucket not configured.")
        
    try:
        app_env = os.getenv("APP_ENV", "dev")
        object_key = f"{app_env}/resume/{filename}"
        
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        from fastapi.responses import StreamingResponse
        return StreamingResponse(
            response['Body'].iter_chunks(), 
            media_type="application/pdf" if filename.endswith(".pdf") else "application/x-tex",
            headers={"Content-Disposition": f"inline; filename={filename}"}
        )
    except ClientError as e:
        if e.response['Error']['Code'] == "NoSuchKey":
            raise HTTPException(status_code=404, detail="File not found")
        logger.error(f"S3 Download failed: {e}")
        raise HTTPException(status_code=500, detail="Error fetching file from Object Storage.")

# ── Dynamic Redirects for Protected HTML Pages ──
@app.get("/admin/dashboard.html")
def get_dashboard(request: Request):
    token = request.cookies.get("session_token")
    if not token or not verify_jwt(token):
        return RedirectResponse(url="/admin/login.html")
    # Serve the dashboard page from secure templates folder
    dashboard_path = os.path.join(BASE_DIR, "templates", "admin", "dashboard.html")
    with open(dashboard_path, "r") as f:
        return HTMLResponse(content=f.read())

# ── Serve Static Assets ──
app.mount("/assets", StaticFiles(directory=os.path.join(BASE_DIR, "public", "assets")), name="assets")

# Fallback to serve static root HTML files (must be defined LAST)
app.mount("/", StaticFiles(directory=os.path.join(BASE_DIR, "public"), html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    # Serves the app locally on port 8000 with hot-reloading
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
