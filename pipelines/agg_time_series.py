import sys
import os

# Add parent directory to path so we can import the config module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config.connection import get_connection, close_connection

def compute_yearly_counts():
    client, db, collection = get_connection()
    try:
        # publish_date is formatted as YYYYMMDD string (e.g., "20010102")
        # We will extract the first 4 characters to get the Year
        pipeline = [
            # 1. Ensure publish_date is a string of length 8
            {"$match": {"publish_date": {"$type": "string", "$regex": "^[0-9]{8}$"}}},
            
            # 2. Extract the year
            {"$project": {
                "year": {"$substr": ["$publish_date", 0, 4]}
            }},
            
            # 3. Group by year and count
            {"$group": {"_id": "$year", "count": {"$sum": 1}}},
            
            # 4. Sort by year chronologically (ascending)
            {"$sort": {"_id": 1}},
            
            # 5. Output to a new collection
            {"$out": "yearly_counts"}
        ]
        
        print("[INFO] Running Aggregation Pipeline for Time-Series Analysis...")
        collection.aggregate(pipeline)
        
        print("[INFO] Time-Series aggregation completed successfully.")
        
        # Display results as a sanity check
        print("[INFO] Yearly headline counts:")
        for doc in db.yearly_counts.find():
            print(f" - {doc['_id']}: {doc['count']:,} headlines")
            
    except Exception as e:
        print(f"[ERROR] Time-Series aggregation failed: {e}")
    finally:
        close_connection(client)

if __name__ == "__main__":
    compute_yearly_counts()
