import sys
import os
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config.connection import get_connection, close_connection

def visualize_sentiment_distribution():
    client, db, collection = get_connection()
    try:
        # Fetch data
        doc = db.sentiment_distribution.find_one()
        
        if not doc:
            print("[WARNING] No sentiment data found. Did you run sentiment_analysis.py first?")
            return
            
        positive = doc.get("positive", 0)
        negative = doc.get("negative", 0)
        neutral = doc.get("neutral", 0)
        sample_size = doc.get("sample_size", positive + negative + neutral)
        
        labels = ['Positive', 'Negative', 'Neutral']
        sizes = [positive, negative, neutral]
        colors = ['#66b3ff', '#ff9999', '#99ff99']
        explode = (0.1, 0.1, 0)
        
        # Create a pie chart
        plt.figure(figsize=(8, 8))
        plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
                shadow=True, startangle=140, textprops={'fontsize': 12})
        plt.title(f'Sentiment Distribution (Based on {sample_size:,} random headlines)', fontsize=14)
        
        # Save figure
        out_dir = os.path.join(os.path.dirname(__file__), "..", "output")
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, "sentiment_distribution.png")
        plt.savefig(out_path, dpi=300)
        print(f"[INFO] Sentiment visualization saved to {out_path}")
        
    except Exception as e:
        print(f"[ERROR] Failed to visualize sentiment: {e}")
    finally:
        close_connection(client)

if __name__ == "__main__":
    visualize_sentiment_distribution()
