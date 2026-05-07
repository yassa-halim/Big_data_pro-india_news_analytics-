import sys
import os
import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config.connection import get_connection, close_connection

def visualize_top_categories():
    client, db, collection = get_connection()
    try:
        print("Generating category distribution chart...")
        cursor = db.category_counts.find().sort("count", -1).limit(15)
        df = pd.DataFrame(list(cursor))
        if df.empty:
            print("[WARN] No category data found to visualize.")
            return

        # Handle missing or empty category names
        df['_id'] = df['_id'].apply(lambda x: "unknown" if not x else x)

        plt.figure(figsize=(12, 6))
        plt.barh(df['_id'].astype(str), df['count'], color='skyblue')
        plt.gca().invert_yaxis()
        plt.title('Top 15 News Categories')
        plt.xlabel('Number of Headlines')
        plt.ylabel('Category')
        plt.tight_layout()
        
        out_dir = os.path.join(os.path.dirname(__file__), "..", "output")
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, "chart1_category_distribution.png")
        plt.savefig(out_path)
        print(f"[INFO] Category chart saved to {out_path}")
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        close_connection(client)

if __name__ == "__main__":
    visualize_top_categories()
