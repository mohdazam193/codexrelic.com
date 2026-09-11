import time
import feedparser
from fastapi import APIRouter
from api.core.logger import logger
from api.core.config import CVE_FEED_URL
from api.tasks.tech_news import load_tech_news

router = APIRouter(prefix="/api")

cve_cache = {"data": [], "last_updated": 0}
CACHE_TTL = 3600  # 1 hour

@router.get("/cve-news")
def get_cve_news():
    current_time = time.time()
    if cve_cache["data"] and (current_time - cve_cache["last_updated"] < CACHE_TTL):
        return cve_cache["data"]

    try:
        feed = feedparser.parse(CVE_FEED_URL)
        news_items = []
        for entry in feed.entries:
            desc = entry.get("description", entry.get("summary", "")).lower()
            score = 0
            
            if any(k in desc for k in ["remote code execution", "rce", "buffer overflow", "sql injection"]):
                score += 3
            elif any(k in desc for k in ["critical", "authentication bypass", "privilege escalation"]):
                score += 2
            elif any(k in desc for k in ["high", "denial of service", "dos", "cross-site scripting", "xss"]):
                score += 1
                
            snippet = entry.get("description", entry.get("summary", ""))
            first_sentence = snippet.split(". ")[0][:70]
            display_title = f"{entry.title}: {first_sentence}..." if snippet else entry.title
                
            news_items.append({
                "title": display_title,
                "link": entry.link,
                "score": score
            })
            
        news_items.sort(key=lambda x: x.get("score", 0), reverse=True)
        news_items = news_items[:15]
        
        if news_items:
            cve_cache["data"] = news_items
            cve_cache["last_updated"] = current_time
            return news_items
    except Exception as e:
        logger.error(f"Error fetching CVE RSS feed: {e}")
        
    return cve_cache["data"]

@router.get("/tech-news")
def get_tech_news():
    data = load_tech_news()
    return data.get("current_news", [])

@router.get("/tech-news/archive")
def get_tech_news_archive():
    data = load_tech_news()
    return data.get("archive", [])
