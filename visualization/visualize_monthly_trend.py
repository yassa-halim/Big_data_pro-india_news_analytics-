# Monthly Trend Visualization — Line chart showing news volume per month over time.

import sys
import os
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config.connection import get_connection, close_connection


def visualize_monthly_trend():
    client, db, collection = get_connection()
    try:
        # Fetch sorted monthly data
        cursor = db.monthly_counts.find().sort("_id", 1)
        data = list(cursor)

        if not data:
            print("[WARNING] No monthly trend data found. Did you run agg_monthly_trend.py first?")
            return

        labels = [f"{doc['_id'][:4]}-{doc['_id'][4:]}" for doc in data]
        counts = [doc["count"] for doc in data]

        # Create the chart
        plt.figure(figsize=(16, 6))
        plt.plot(range(len(labels)), counts, color='#2196F3', linewidth=0.8, alpha=0.9)
        plt.fill_between(range(len(labels)), counts, color='#2196F3', alpha=0.15)

        # Show only every Nth label to avoid overcrowding
        step = max(1, len(labels) // 20)
        plt.xticks(
            range(0, len(labels), step),
            [labels[i] for i in range(0, len(labels), step)],
            rotation=45, fontsize=8
        )

        plt.xlabel('Month', fontsize=12)
        plt.ylabel('Number of Headlines', fontsize=12)
        plt.title('Monthly Trend of India News Headlines', fontsize=14)
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.tight_layout()

        # Save figure
        out_dir = os.path.join(os.path.dirname(__file__), "..", "output")
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, "monthly_trend.png")
        plt.savefig(out_path, dpi=300)
        print(f"[INFO] Monthly trend visualization saved to {out_path}")

    except Exception as e:
        print(f"[ERROR] Failed to visualize monthly trend: {e}")
    finally:
        close_connection(client)


if __name__ == "__main__":
    visualize_monthly_trend()
