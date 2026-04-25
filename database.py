from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

# Global database reference
database = None

def startup_db_client():
    """Initialize MongoDB connection on startup"""
    global database
    mongo_uri = os.getenv("MONGO_URI")
    db_name = os.getenv("DB_NAME")
    
    if not mongo_uri:
        raise ValueError("MONGO_URI environment variable not set")
    if not db_name:
        raise ValueError("DB_NAME environment variable not set")
    
    mongodb_client = MongoClient(mongo_uri)
    database = mongodb_client[db_name]
    print("Connected to the MongoDB database!")
    return database

# Initialize database on module load
startup_db_client()

# Collections
tours_and_reviews = database["tours_and_reviews"]

def find_tours_for_destination(destination):
    """Find all tours for a destination, excluding the _id field"""
    docs = list(tours_and_reviews.find(
        {"destination": destination},
        {"_id": 0}
    ))
    return docs

def save_tours(destination, start_date, end_date, reviews):
    """Save tour results to the database"""
    return tours_and_reviews.insert_one({
        "destination": destination,
        "start_date": start_date,
        "end_date": end_date,
        "reviews": reviews
    })
