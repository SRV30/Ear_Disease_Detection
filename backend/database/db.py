from pymongo import MongoClient
from config import MONGO_URI

client = MongoClient(MONGO_URI)
db = client["ear"]

users_collection = db["users"]
history_collection = db["history"]
blacklist_collection = db["blacklist"]