# Monthly Trend Aggregation — Discovers seasonal patterns in news publishing.

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config.connection import get_connection, close_connection


def compute_monthly_counts():
    """
    Aggregation pipeline that groups headlines by Year-Month (YYYYMM).
    Reveals seasonal patterns and spikes tied to specific events.
    """
    client, db, collection = get_connection()
    try:
        pipeline = [
            # 1. Ensure publish_date is a valid 8-digit string
            {"$match": {"publish_date": {"$type": "string", "$regex": "^[0-9]{8}$"}}},

            # 2. Extract Year-Month (first 6 chars: YYYYMM)
            {"$project": {
                "year_month": {"$substr": ["$publish_date", 0, 6]},
                "year": {"$substr": ["$publish_date", 0, 4]},
                "month": {"$substr": ["$publish_date", 4, 2]}
            }},

            # 3. Group by year_month and count
            {"$group": {
                "_id": "$year_month",
                "year": {"$first": "$year"},
                "month": {"$first": "$month"},
                "count": {"$sum": 1}
            }},

            # 4. Sort chronologically
            {"$sort": {"_id": 1}},

            # 5. Output to new collection
            {"$out": "monthly_counts"}
        ]

        print("[INFO] Running Aggregation Pipeline for Monthly Trend Analysis...")
        collection.aggregate(pipeline, allowDiskUse=True)

        print("[INFO] Monthly trend aggregation completed successfully.")

        # Display top 10 busiest months
        print("[INFO] Top 10 busiest months:")
        top_months = db.monthly_counts.find().sort("count", -1).limit(10)
        for doc in top_months:
            year = doc.get("year", doc["_id"][:4])
            month = doc.get("month", doc["_id"][4:6])
            print(f"  - {year}-{month}: {doc['count']:,} headlines")

    except Exception as e:
        print(f"[ERROR] Monthly trend aggregation failed: {e}")
    finally:
        close_connection(client)


if __name__ == "__main__":
    compute_monthly_counts()
