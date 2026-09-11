import json
import asyncio
import feedparser
import traceback
import os
from datetime import datetime, timedelta
from api.core.logger import logger
from api.core.config import TECH_NEWS_FILE, TECH_NEWS_URL

FETCH_INTERVAL_HOURS = 3  # 24h / 3h = 8 fetches per day

def load_tech_news():
    if not os.path.exists(TECH_NEWS_FILE):
        return {"last_fetch": None, "current_news": [], "archive": []}
    try:
        with open(TECH_NEWS_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading tech news JSON: {e}")
        return {"last_fetch": None, "current_news": [], "archive": []}

def save_tech_news(data):
    try:
        with open(TECH_NEWS_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving tech news JSON: {e}")

def _should_fetch(data):
    """Check if enough time has passed since the last fetch."""
    last = data.get("last_fetch")
    if not last:
        return True
    try:
        last_dt = datetime.fromisoformat(last)
        return datetime.utcnow() - last_dt >= timedelta(hours=FETCH_INTERVAL_HOURS)
    except (ValueError, TypeError):
        return True

def _cleanup_old_archives(data, max_days=10):
    """Remove archive entries older than max_days."""
    cutoff = (datetime.utcnow() - timedelta(days=max_days)).strftime("%Y-%m-%d")
    data["archive"] = [
        entry for entry in data.get("archive", [])
        if entry.get("date", "9999-99-99") >= cutoff
    ]

async def fetch_tech_news_task():
    logger.info(f"Starting Tech News background fetch loop (every {FETCH_INTERVAL_HOURS}h)...")
    while True:
        try:
            data = load_tech_news()
            
            if _should_fetch(data):
                now = datetime.utcnow()
                today_str = now.strftime("%Y-%m-%d")
                logger.info(f"Fetching Tech News at {now.isoformat()}...")
                feed = feedparser.parse(TECH_NEWS_URL)
                news_items = []
                for entry in feed.entries[:10]:
                    news_items.append({
                        "title": entry.title,
                        "link": entry.link,
                        "published": entry.get("published", ""),
                    })
                
                if news_items:
                    # Archive previous batch if it exists
                    if data.get("current_news"):
                        archive_date = data.get("last_fetch", today_str)
                        # Normalize archive date to just the date portion
                        try:
                            archive_date = datetime.fromisoformat(archive_date).strftime("%Y-%m-%d")
                        except (ValueError, TypeError):
                            archive_date = today_str
                        archive_entry = {
                            "date": archive_date,
                            "news": data["current_news"]
                        }
                        data.setdefault("archive", []).insert(0, archive_entry)
                    
                    # Prune archives older than 10 days
                    _cleanup_old_archives(data, max_days=10)
                    
                    data["current_news"] = news_items
                    data["last_fetch"] = now.isoformat()
                    save_tech_news(data)
                    logger.info(f"Successfully fetched Tech News. Next fetch in ~{FETCH_INTERVAL_HOURS}h.")
                else:
                    logger.warning("Feed returned 0 items, skipping update.")
            else:
                logger.debug("Tech News fetch skipped — interval not yet elapsed.")
                
        except Exception as e:
            logger.error(f"Error in tech news fetch loop: {e}\n{traceback.format_exc()}")
            
        await asyncio.sleep(FETCH_INTERVAL_HOURS * 3600)

