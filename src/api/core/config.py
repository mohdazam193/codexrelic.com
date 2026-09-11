import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = 24
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
AWS_ENDPOINT_URL_S3 = os.getenv("AWS_ENDPOINT_URL_S3")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_DEFAULT_REGION = os.getenv("AWS_DEFAULT_REGION", "ap-hyderabad-1")
AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET")
APP_ENV = os.getenv("APP_ENV", "dev")
TECH_NEWS_FILE = os.path.join(BASE_DIR, "data", "tech_news.json")
TECH_NEWS_URL = "https://news.ycombinator.com/rss"
CVE_FEED_URL = "https://cve.report/cve.rss"
