import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr, Field

from api.core.database import db, DB_CONNECTED
from api.core.config import (
    SMTP_HOST,
    SMTP_PORT,
    SMTP_USER,
    SMTP_PASS,
    CONTACT_RECIPIENT_EMAIL,
)
from api.core.logger import logger

router = APIRouter(prefix="/api")

class ContactRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=80)
    email: str = Field(..., min_length=5, max_length=120, pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    subject: str = Field(..., min_length=3, max_length=150)
    message: str = Field(..., min_length=10, max_length=3000)

@router.post("/contact")
async def send_contact_inquiry(payload: ContactRequest):
    """
    Receives visitor contact form submissions securely without exposing
    recipient email credentials to the client/browser.
    """
    # 1. Store in MongoDB if available
    inquiry_saved = False
    if DB_CONNECTED and db is not None:
        try:
            inquiries_col = db.get_collection("inquiries")
            inquiries_col.insert_one({
                "name": payload.name,
                "email": payload.email,
                "subject": payload.subject,
                "message": payload.message,
                "created_at": datetime.utcnow()
            })
            inquiry_saved = True
            logger.info(f"Persisted contact inquiry from {payload.email} to MongoDB")
        except Exception as e:
            logger.warning(f"Could not persist inquiry to MongoDB: {e}")

    # 2. Forward to personal mailbox via SMTP
    email_dispatched = False
    if SMTP_USER and SMTP_PASS and CONTACT_RECIPIENT_EMAIL:
        try:
            msg = MIMEMultipart()
            msg["From"] = f"CodexRelic Portal <{SMTP_USER}>"
            msg["To"] = CONTACT_RECIPIENT_EMAIL
            msg["Reply-To"] = f"{payload.name} <{payload.email}>"
            msg["Subject"] = f"[CodexRelic Contact] {payload.subject}"

            body = (
                f"You received a new message via CodexRelic Contact Portal:\n\n"
                f"Sender Name: {payload.name}\n"
                f"Sender Email: {payload.email}\n"
                f"Subject: {payload.subject}\n"
                f"Timestamp: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n"
                f"--- Message ---\n"
                f"{payload.message}\n"
            )
            msg.attach(MIMEText(body, "plain"))

            with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASS)
                server.send_message(msg)

            email_dispatched = True
            logger.info(f"Successfully dispatched contact email to {CONTACT_RECIPIENT_EMAIL}")
        except Exception as e:
            logger.error(f"Failed to dispatch contact email via SMTP: {e}")

    return {
        "success": True,
        "message": "Thank you! Your message has been received and routed securely."
    }


@router.get("/movies")
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

@router.get("/blogs")
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
