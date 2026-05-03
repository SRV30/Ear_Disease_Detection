from pymongo import MongoClient, ASCENDING
from config import MONGO_URI

client = MongoClient(MONGO_URI)
db = client["ear"]

users_collection = db["users"]
history_collection = db["history"]
blacklist_collection = db["blacklist"]
password_reset_collection = db["password_resets"]
connections_collection = db["connections"]

users_collection.create_index([("email", ASCENDING)], unique=True)
password_reset_collection.create_index("expires_at", expireAfterSeconds=0)
connections_collection.create_index([("from_user", ASCENDING), ("to_user", ASCENDING)], unique=True)
