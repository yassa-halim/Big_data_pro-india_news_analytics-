import sys
import os
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config.connection import get_connection, close_connection

def visualize_time_series():
    client, db, collection = get_connection()
    try:
        # Fetch sorted yearly data
        cursor = db.yearly_counts.find().sort("_id", 1)
        
        years = []
        counts = []
        for doc in cursor:
            years.append(doc["_id"])
            counts.append(doc["count"])
            
        if not years:
            print("[WARNING] No time-series data found. Did you run agg_time_series.py first?")
            return
            
        # Create a line chart
        plt.figure(figsize=(12, 6))
        plt.plot(years, counts, marker='o', linestyle='-', color='b', linewidth=2)
        plt.fill_between(years, counts, color='b', alpha=0.1)
        
        plt.xlabel('Year', fontsize=12)
        plt.ylabel('Number of Headlines', fontsize=12)
        plt.title('Trend of India News Headlines Over Time', fontsize=14)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Save figure
        os.makedirs(os.path.join(os.path.dirname(__file__), "..", "output"), exist_ok=True)
        out_path = os.path.join(os.path.dirname(__file__), "..", "output", "time_series.png")
        plt.savefig(out_path, dpi=300)
        print(f"[INFO] Time-Series visualization saved to {out_path}")
        
    except Exception as e:
        print(f"[ERROR] Failed to visualize time-series: {e}")
    finally:
        close_connection(client)

if __name__ == "__main__":
    visualize_time_series()
