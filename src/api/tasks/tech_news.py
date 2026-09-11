import json
import asyncio
import feedparser
import traceback
import os
from datetime import datetime
from api.core.logger import logger
from api.core.config import TECH_NEWS_FILE, TECH_NEWS_URL

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

async def fetch_tech_news_task():
    logger.info("Starting Tech News background fetch loop...")
    while True:
        try:
            today_str = datetime.utcnow().strftime("%Y-%m-%d")
            data = load_tech_news()
            
            if data.get("last_fetch") != today_str:
                logger.info(f"Fetching new Tech News for {today_str}...")
                feed = feedparser.parse(TECH_NEWS_URL)
                news_items = []
                for entry in feed.entries[:10]:
                    news_items.append({
                        "title": entry.title,
                        "link": entry.link,
                        "published": entry.get("published", ""),
                    })
                
                if news_items:
                    if data.get("current_news"):
                        archive_entry = {
                            "date": data.get("last_fetch", "unknown"),
                            "news": data["current_news"]
                        }
                        data.setdefault("archive", []).insert(0, archive_entry)
                        data["archive"] = data["archive"][:10]
                    
                    data["current_news"] = news_items
                    data["last_fetch"] = today_str
                    save_tech_news(data)
                    logger.info("Successfully fetched and archived Tech News.")
                
        except Exception as e:
            logger.error(f"Error in tech news fetch loop: {e}\n{traceback.format_exc()}")
            
        await asyncio.sleep(3600)
