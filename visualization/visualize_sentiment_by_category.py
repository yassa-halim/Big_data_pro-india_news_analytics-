# Visualization: Sentiment by Category — Horizontal bar chart with color gradient.

import sys
import os
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config.connection import get_connection, close_connection


def visualize_sentiment_by_category():
    client, db, collection = get_connection()
    try:
        cursor = db.sentiment_by_category.find().sort("avg_compound", 1)
        data = list(cursor)

        if not data:
            print("[WARNING] No sentiment-by-category data found. Run agg_sentiment_by_category.py first.")
            return

        categories = [doc["category"] for doc in data]
        scores = [doc["avg_compound"] for doc in data]

        # Create diverging color map: Red (negative) → White → Green (positive)
        norm = mcolors.TwoSlopeNorm(vmin=min(scores), vcenter=0, vmax=max(scores))
        cmap = plt.cm.RdYlGn
        colors = [cmap(norm(s)) for s in scores]

        plt.figure(figsize=(12, 8))
        bars = plt.barh(categories, scores, color=colors, edgecolor='gray', linewidth=0.5)

        # Add score labels on each bar
        for bar, score in zip(bars, scores):
            x_pos = bar.get_width()
            offset = 0.005 if score >= 0 else -0.005
            ha = 'left' if score >= 0 else 'right'
            plt.text(x_pos + offset, bar.get_y() + bar.get_height() / 2,
                     f'{score:+.3f}', ha=ha, va='center', fontsize=9, fontweight='bold')

        plt.axvline(x=0, color='black', linewidth=0.8, linestyle='-')
        plt.xlabel('Average Sentiment Score (VADER Compound)', fontsize=12)
        plt.ylabel('News Category', fontsize=12)
        plt.title('Sentiment Analysis by News Category', fontsize=14)
        plt.tight_layout()

        # Save figure
        out_dir = os.path.join(os.path.dirname(__file__), "..", "output")
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, "sentiment_by_category.png")
        plt.savefig(out_path, dpi=300)
        print(f"[INFO] Sentiment by category chart saved to {out_path}")

    except Exception as e:
        print(f"[ERROR] Failed to visualize sentiment by category: {e}")
    finally:
        close_connection(client)


if __name__ == "__main__":
    visualize_sentiment_by_category()
