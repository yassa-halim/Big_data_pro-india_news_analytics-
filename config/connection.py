# MongoDB connection helper module for the India News Analytics project.

import os
from pymongo import MongoClient

try:
    from dotenv import load_dotenv
    # Load environment variables from .env file if it exists
    load_dotenv()
except ImportError:
    pass

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DATABASE_NAME = os.getenv("DATABASE_NAME", "india_news_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "headlines")


def get_connection():
    """
    Establish and return a connection to the MongoDB server.
    Returns a tuple of (client, database, collection).
    """
    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]
    return client, db, collection


def close_connection(client):
    """Close the MongoDB client connection."""
    if client:
        client.close()
