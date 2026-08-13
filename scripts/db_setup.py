import os
import sys
import bcrypt
from pymongo import MongoClient, ASCENDING
from dotenv import load_dotenv

# Load workspace relative paths
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(base_dir, '.env'))

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI or "localhost" in MONGO_URI:
    print("[!] Error: MONGO_URI in .env is not pointing to your MongoDB Atlas Cloud database.")
    print("    Please ensure your .env contains your Atlas connection string.")
    sys.exit(1)

print("[*] Connecting to MongoDB Atlas Cluster...")
client = MongoClient(MONGO_URI)
db = client.get_database("codexrelic")

# 1. Clear database
print("[!] Dropping existing 'codexrelic' database to clean slate...")
client.drop_database("codexrelic")

# 2. Create collections and define constraints/indexes
print("[*] Initializing collections...")

# Users Collection
users_col = db.get_collection("users")
users_col.create_index([("username", ASCENDING)], unique=True)
print("    -> Created 'users' collection with unique index on 'username'")

# Movies Collection
movies_col = db.get_collection("movies")
movies_col.create_index([("created_at", ASCENDING)])
print("    -> Created 'movies' collection with index on 'created_at'")

# Blogs Collection
blogs_col = db.get_collection("blogs")
blogs_col.create_index([("slug", ASCENDING)], unique=True)
print("    -> Created 'blogs' collection with unique index on 'slug'")

# Events Collection
events_col = db.get_collection("events")
events_col.create_index([("date", ASCENDING)])
print("    -> Created 'events' collection with index on 'date'")

# 3. Seed Admin user
admin_user = os.getenv("ADMIN_USER", "admin")
admin_pass = os.getenv("ADMIN_PASS", "codexrelic")
admin_code = os.getenv("ADMIN_CODE", "123456")

salt = bcrypt.gensalt()
hashed_pass = bcrypt.hashpw(admin_pass.encode('utf-8'), salt)
hashed_code = bcrypt.hashpw(admin_code.encode('utf-8'), salt)

users_col.insert_one({
    "username": admin_user,
    "passkey_hash": hashed_pass.decode('utf-8'),
    "realm_code_hash": hashed_code.decode('utf-8')
})

print("========================================================================")
print("[✅] DATABASE INITIALIZATION COMPLETE")
print("========================================================================")
print(f"    • Database:    codexrelic")
print(f"    • Admin User:  {admin_user}")
print(f"    • passkey:     [Encrypted Argon2/Bcrypt Hash]")
print(f"    • realm code:  [Encrypted Argon2/Bcrypt Hash]")
print("========================================================================")
print("Ready for authentication and CRUD operations.")
