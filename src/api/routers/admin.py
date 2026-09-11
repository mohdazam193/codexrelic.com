import os
import re
import bcrypt
from datetime import datetime
from fastapi import APIRouter, Depends, Form, Request, Response, HTTPException, UploadFile, File
from fastapi.responses import RedirectResponse, HTMLResponse, StreamingResponse
from botocore.exceptions import ClientError
from api.core.logger import logger
from api.core.config import BASE_DIR, APP_ENV, AWS_S3_BUCKET
from api.core.database import db, DB_CONNECTED
from api.core.security import get_current_user, login_limiter, create_jwt, JWT_EXPIRE_HOURS
from api.core.storage import s3_client

router = APIRouter()

@router.post("/api/login")
def login(
    request: Request,
    response: Response,
    username: str = Form(...),
    password: str = Form(...),
    private_key: str = Form(...)
):
    client_ip = request.client.host if request.client else "unknown"
    if not login_limiter.is_allowed(client_ip):
        logger.warning(f"Login rate limit exceeded for IP: {client_ip}")
        raise HTTPException(status_code=429, detail="Too many login attempts. Please try again in a minute.")

    if not DB_CONNECTED or db is None:
        raise HTTPException(status_code=500, detail="Database is unreachable. Cannot authenticate.")
    
    users_col = db.get_collection("admin_users")
    user = users_col.find_one({"username": username})
    
    if not user:
        raise HTTPException(status_code=401, detail="Authentication credentials invalid")
        
    if not bcrypt.checkpw(password.encode('utf-8'), user["passkey_hash"].encode('utf-8')):
        raise HTTPException(status_code=401, detail="Authentication credentials invalid")
        
    if not bcrypt.checkpw(private_key.encode('utf-8'), user["private_key_hash"].encode('utf-8')):
        raise HTTPException(status_code=401, detail="Authentication credentials invalid")

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

@router.post("/api/admin/movies", dependencies=[Depends(get_current_user)])
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
        raise HTTPException(status_code=503, detail="Write actions failed: Database is offline.")
        
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

@router.post("/api/admin/blogs", dependencies=[Depends(get_current_user)])
def add_blog(
    title: str = Form(...),
    category: str = Form(...),
    summary: str = Form(...),
    content: str = Form(...),
    tags: str = Form(...),
    read_time: int = Form(...)
):
    if not DB_CONNECTED or db is None:
        raise HTTPException(status_code=503, detail="Write actions failed: Database is offline.")

    blogs_col = db.get_collection("blogs")
    
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

@router.post("/api/admin/resume", dependencies=[Depends(get_current_user)])
async def upload_resume(file: UploadFile = File(...)):
    if not (file.filename.endswith(".tex") or file.filename.endswith(".pdf")):
        raise HTTPException(status_code=400, detail="Invalid file type. Only .tex and .pdf are allowed.")
        
    MAX_FILE_SIZE = 5 * 1024 * 1024
    contents = await file.read(MAX_FILE_SIZE + 1)
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large. Maximum size is 5MB.")

    if not AWS_S3_BUCKET:
        raise HTTPException(status_code=500, detail="S3 Bucket not configured in environment.")
        
    try:
        ext = file.filename.split('.')[-1]
        object_name = f"{APP_ENV}/resume/resume.{ext}"
        
        s3_client.put_object(
            Bucket=AWS_S3_BUCKET,
            Key=object_name,
            Body=contents,
            ContentType="application/pdf" if ext == "pdf" else "application/x-tex"
        )
    except ClientError as e:
        logger.error(f"S3 Upload failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload file to Object Storage.")
        
    return {"status": "success", "message": f"Successfully uploaded {object_name} to OCI Object Storage!"}

@router.get("/content/resume/{filename}")
async def download_resume(filename: str):
    if filename not in ["resume.pdf", "resume.tex"]:
        raise HTTPException(status_code=403, detail="Forbidden")
        
    if not AWS_S3_BUCKET:
        raise HTTPException(status_code=500, detail="S3 Bucket not configured.")
        
    try:
        object_key = f"{APP_ENV}/resume/{filename}"
        response = s3_client.get_object(Bucket=AWS_S3_BUCKET, Key=object_key)
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

@router.get("/admin/dashboard.html")
def get_dashboard(request: Request):
    token = request.cookies.get("session_token")
    if not token or not get_current_user(request):
        return RedirectResponse(url="/admin/login.html")
    dashboard_path = os.path.join(BASE_DIR, "templates", "admin", "dashboard.html")
    with open(dashboard_path, "r") as f:
        return HTMLResponse(content=f.read())
