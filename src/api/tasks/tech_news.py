import json
import asyncio
import feedparser
import traceback
import os
import urllib.request
import re
import html
from urllib.parse import urlparse
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
        os.makedirs(os.path.dirname(TECH_NEWS_FILE), exist_ok=True)
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

def _fetch_meta_summary(url):
    """Fetch domain and rich ~80-100 word preview summary from article content or meta tags."""
    domain = urlparse(url).netloc.replace("www.", "")
    summary = ""
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            content_type = response.headers.get("Content-Type", "")
            if "text/html" in content_type:
                raw = response.read(300000).decode("utf-8", errors="ignore")
                
                # Check meta description
                meta_matches = re.findall(
                    r'<meta\s+(?:name|property)=[\"\'](?:og:description|description)[\"\']\s+content=[\"\'](.*?)[\"\']',
                    raw,
                    re.IGNORECASE
                )
                if not meta_matches:
                    meta_matches = re.findall(
                        r'<meta\s+content=[\"\'](.*?)[\"\']\s+(?:name|property)=[\"\'](?:og:description|description)[\"\']',
                        raw,
                        re.IGNORECASE
                    )
                meta_desc = html.unescape(meta_matches[0].strip()) if meta_matches else ""
                
                # Locate article/main container
                body_html = ""
                body_match = re.search(r'<(?:article|main)[^>]*>(.*?)</(?:article|main)>', raw, flags=re.DOTALL | re.IGNORECASE)
                if body_match:
                    body_html = body_match.group(1)
                else:
                    body_match = re.search(r'<div[^>]*(?:id|class)=[\"\'][^\"\']*(?:article|content|post|entry|story)[^\"\']*[\"\'][^>]*>(.*?)</div>', raw, flags=re.DOTALL | re.IGNORECASE)
                    body_html = body_match.group(1) if body_match else raw
                
                clean = re.sub(r'<(script|style|nav|header|footer|aside)[^>]*>.*?</\1>', '', body_html, flags=re.DOTALL | re.IGNORECASE)
                paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', clean, flags=re.DOTALL | re.IGNORECASE)
                clean_ps = []
                for p in paragraphs:
                    text = re.sub(r'<[^>]+>', '', p)
                    text = html.unescape(' '.join(text.split()))
                    if len(text) > 40 and not any(k in text.lower() for k in ['cookie', 'javascript', 'subscribe', 'terms of', 'all rights reserved', 'sign up', 'member get started']):
                        clean_ps.append(text)
                
                body_text = ' '.join(clean_ps)
                
                if meta_desc and len(meta_desc) > 50:
                    if meta_desc.lower() not in body_text.lower():
                        full_text = meta_desc + ' ' + body_text
                    else:
                        full_text = body_text
                else:
                    full_text = body_text if body_text else meta_desc
                
                words = full_text.split()
                if len(words) > 90:
                    summary = ' '.join(words[:90]) + '...'
                elif len(words) >= 15:
                    summary = ' '.join(words)
                else:
                    summary = meta_desc
    except Exception:
        pass
    return {"domain": domain, "summary": summary}

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
                raw_entries = feed.entries[:10]
                
                # Concurrently extract summaries for the top entries
                loop = asyncio.get_event_loop()
                tasks = [loop.run_in_executor(None, _fetch_meta_summary, entry.link) for entry in raw_entries]
                meta_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                news_items = []
                for entry, meta in zip(raw_entries, meta_results):
                    meta_dict = meta if isinstance(meta, dict) else {"domain": "", "summary": ""}
                    news_items.append({
                        "title": entry.title,
                        "link": entry.link,
                        "published": entry.get("published", ""),
                        "domain": meta_dict.get("domain", ""),
                        "summary": meta_dict.get("summary", "")
                    })
                
                if news_items:
                    # Archive previous batch if it exists
                    if data.get("current_news"):
                        archive_date = data.get("last_fetch", today_str)
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
                    logger.info(f"Successfully fetched Tech News with summaries. Next fetch in ~{FETCH_INTERVAL_HOURS}h.")
                else:
                    logger.warning("Feed returned 0 items, skipping update.")
            else:
                logger.debug("Tech News fetch skipped — interval not yet elapsed.")
                
        except Exception as e:
            logger.error(f"Error in tech news fetch loop: {e}\n{traceback.format_exc()}")
            
        await asyncio.sleep(FETCH_INTERVAL_HOURS * 3600)


