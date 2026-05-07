import csv
import sys
import os
from datetime import datetime

# Add parent directory to path so we can import the config module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config.connection import get_connection, close_connection

CSV_FILE = os.path.join(os.path.dirname(__file__), "..", "india-news-headlines.csv")
BATCH_SIZE = 20000  # Insert 20,000 records at a time

def import_data():
    if not os.path.exists(CSV_FILE):
        print(f"[ERROR] CSV file not found at {CSV_FILE}")
        return

    client, db, collection = get_connection()
    try:
        # We can drop the existing collection to start fresh
        collection.drop()
        print(f"[INFO] Dropped existing '{collection.name}' collection.")
        
        print(f"[INFO] Starting to import data from {CSV_FILE}...")
        
        records = []
        total_inserted = 0
        
        with open(CSV_FILE, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                # Basic mapping
                record = {
                    "publish_date": row.get("publish_date", ""),
                    "headline_category": row.get("headline_category", "unknown"),
                    "headline_text": row.get("headline_text", "")
                }
                records.append(record)
                
                if len(records) >= BATCH_SIZE:
                    collection.insert_many(records)
                    total_inserted += len(records)
                    records = []
                    print(f"[INFO] Inserted {total_inserted:,} records...", end="\r")
            
            # Insert any remaining records
            if records:
                collection.insert_many(records)
                total_inserted += len(records)
                
        print(f"\n[INFO] Successfully inserted {total_inserted:,} records into '{db.name}.{collection.name}'.")
        
    except Exception as e:
        print(f"[ERROR] Failed to import data: {e}")
    finally:
        close_connection(client)

if __name__ == "__main__":
    import_data()
