from pymongo import MongoClient
from api.core.config import MONGO_URI, APP_ENV
from api.core.logger import logger

DB_CONNECTED = False
db = None
client = None

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
    client.admin.command('ping')
    db_name = f"codexrelic_{APP_ENV}" if APP_ENV else "codexrelic"
    db = client.get_database(db_name)
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
