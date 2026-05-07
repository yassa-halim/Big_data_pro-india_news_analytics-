import sys
import os
import matplotlib.pyplot as plt
from wordcloud import WordCloud

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config.connection import get_connection, close_connection
import pandas as pd

def visualize_word_frequencies():
    client, db, collection = get_connection()
    try:
        print("Generating word cloud from word frequencies...")
        cursor = db.word_frequencies.find().sort("count", -1).limit(200)
        data = list(cursor)
        if not data:
            print("[WARN] No word frequency data found.")
            return

        # Create a dictionary of {word: count} for WordCloud
        word_freq = {doc['_id']: doc['count'] for doc in data}

        # Generate Word Cloud
        wc = WordCloud(width=800, height=400, background_color="white", colormap="viridis", max_words=200)
        wc.generate_from_frequencies(word_freq)

        plt.figure(figsize=(10, 5))
        plt.imshow(wc, interpolation='bilinear')
        plt.axis('off')
        plt.title('Top Words in India News Headlines')
        plt.tight_layout()

        out_dir = os.path.join(os.path.dirname(__file__), "..", "output")
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, "wordcloud.png")
        plt.savefig(out_path)
        print(f"[INFO] WordCloud saved to {out_path}")
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        close_connection(client)

if __name__ == "__main__":
    visualize_word_frequencies()
