import os
import secrets
import bcrypt
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request, Response, Form, UploadFile, File, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="codexrelic API")

# Connect to MongoDB Atlas (fallback to local if URI not provided)
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)
db = client.get_database("codexrelic")

# Hardcoded session token in-memory check (reboot clears sessions)
ACTIVE_SESSIONS = set()

# ── Seed Admin User (Makes Setup Simple) ──
def seed_admin():
    admin_user = os.getenv("ADMIN_USER", "admin")
    admin_pass = os.getenv("ADMIN_PASS", "codexrelic")
    admin_code = os.getenv("ADMIN_CODE", "123456")
    
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
        print(f"[*] Seeding default administrator user: username='{admin_user}'")

seed_admin()

# ── Authentication Helper Dependency ──
def get_current_user(request: Request):
    token = request.cookies.get("session_token")
    if not token or token not in ACTIVE_SESSIONS:
        raise HTTPException(status_code=401, detail="Unauthorized session")
    return token

# ── Public APIs ──

# Movies List API (with static fallbacks)
@app.get("/api/movies")
def get_movies():
    movies_col = db.get_collection("movies")
    movies = list(movies_col.find({}, {"_id": 0}))
    
    # Static fallbacks if DB is completely empty
    if not movies:
        movies = [
            {
                "title": "Interstellar (2014)",
                "director": "Christopher Nolan",
                "rating": 10.0,
                "genre": "sci-fi",
                "poster_url": "https://m.media-amazon.com/images/M/MV5BYzdjMDAxZGUtNzI2My00NTQ1LWIwNDctYmQxODIwMDM3YmRlXkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg",
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
                "poster_url": "https://m.media-amazon.com/images/M/MV5BMjAxMzY3NjcxNF5BMl5BanBnXkFtZTcwNTI5OTM0Mw@@._V1_FMjpg_UX1000_.jpg",
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
                "poster_url": "https://m.media-amazon.com/images/M/MV5BYzg0NGM2NjAtN2VjNy00MjY0LWIyM2UtYzg4M2M1YjkyMGU2XkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg",
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
                "poster_url": "https://m.media-amazon.com/images/M/MV5BYmQyNTA1ZGItNjZjMi00NzFlLWIyNDUtYjlhYjM0MWRmYTMyXkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg",
                "description": "Kubrick's masterpiece. The monolith acts as a cosmic rulebook. HAL 9000 shows tragedy of system conflict.",
                "sre_analogy": {
                    "title": "Split-Brain",
                    "description": "HAL 9000 conflicting rules nervous breakdown. Partitioned cluster nodes thinking they are both master."
                }
            }
        ]
    return movies

# Blogs List API (with static fallbacks)
@app.get("/api/blogs")
def get_blogs():
    blogs_col = db.get_collection("blogs")
    blogs = list(blogs_col.find({}, {"_id": 0}))
    
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

# ── Authentication API ──
@app.post("/api/login")
def login(response: Response, username: str = Form(...), password: str = Form(...), quantum_key: str = Form(...)):
    users_col = db.get_collection("users")
    user = users_col.find_one({"username": username})
    
    if not user:
        raise HTTPException(status_code=401, detail="Authentication failed")
    
    # Validate passkey
    pass_valid = bcrypt.checkpw(password.encode('utf-8'), user["passkey_hash"].encode('utf-8'))
    # Validate realm code
    code_valid = bcrypt.checkpw(quantum_key.encode('utf-8'), user["realm_code_hash"].encode('utf-8'))
    
    if not (pass_valid and code_valid):
        raise HTTPException(status_code=401, detail="Authentication credentials invalid")
        
    session_token = secrets.token_hex(32)
    ACTIVE_SESSIONS.add(session_token)
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        samesite="lax",
        path="/"
    )
    return {"status": "authenticated", "redirect": "/admin/dashboard.html"}

# ── Protected Admin CMS APIs ──

# Add Movie Endpoint
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
    return {"status": "success", "message": "Movie inserted into MongoDB Atlas"}

# Add Blog Endpoint
@app.post("/api/admin/blogs", dependencies=[Depends(get_current_user)])
def add_blog(
    title: str = Form(...),
    category: str = Form(...),
    summary: str = Form(...),
    content: str = Form(...),
    tags: str = Form(...),
    read_time: int = Form(...)
):
    blogs_col = db.get_collection("blogs")
    slug = title.lower().replace(" ", "-").replace(":", "").replace("?", "")
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
    return {"status": "success", "message": "Blog post inserted into MongoDB Atlas"}

# Upload Resume Endpoint
@app.post("/api/admin/resume", dependencies=[Depends(get_current_user)])
async def upload_resume(file: UploadFile = File(...)):
    if not file.filename.endswith(".tex"):
        raise HTTPException(status_code=400, detail="Invalid file type. LaTeX (.tex) required.")
        
    save_path = "/Users/azam.mohd/Desktop/codexrelic.com/codexrelic.com/content/resume/resume.tex"
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    with open(save_path, "wb") as f:
        f.write(await file.read())
        
    return {"status": "success", "message": "LaTeX source file overwritten successfully"}

# ── Dynamic Redirects for Protected HTML Pages ──
@app.get("/admin/dashboard.html")
def get_dashboard(request: Request):
    token = request.cookies.get("session_token")
    if not token or token not in ACTIVE_SESSIONS:
        return RedirectResponse(url="/admin/login.html")
    # Serve the dashboard page from file
    with open("/Users/azam.mohd/Desktop/codexrelic.com/codexrelic.com/admin/dashboard.html", "r") as f:
        return HTMLResponse(content=f.read())

# ── Serve Static Assets ──
app.mount("/assets", StaticFiles(directory="/Users/azam.mohd/Desktop/codexrelic.com/codexrelic.com/assets"), name="assets")

# Fallback to serve static root HTML files (must be defined LAST)
app.mount("/", StaticFiles(directory="/Users/azam.mohd/Desktop/codexrelic.com/codexrelic.com", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    # Serves the app locally on port 8000
    uvicorn.run(app, host="127.0.0.1", port=8000)
