import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config.connection import get_connection, close_connection

def count_categories():
    client, db, collection = get_connection()
    try:
        print("Running category count aggregation...")
        pipeline = [
            {"$group": {"_id": "$headline_category", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$out": "category_counts"}
        ]
        collection.aggregate(pipeline)
        print("[INFO] Category count aggregation completed and saved to 'category_counts'.")
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        close_connection(client)

if __name__ == "__main__":
    count_categories()
