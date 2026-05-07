# Sentiment Analysis using VADER — Optimized for news & media text.

import sys
import os
import multiprocessing
from concurrent.futures import ProcessPoolExecutor, as_completed

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
except ImportError:
    print("[ERROR] Please install vaderSentiment first: pip install vaderSentiment")
    sys.exit(1)

# Add parent directory to path so we can import the config module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config.connection import get_connection, close_connection


def analyze_batch(texts):
    """Analyze a batch of texts using VADER sentiment analyzer."""
    analyzer = SentimentIntensityAnalyzer()
    pos = 0
    neg = 0
    neu = 0
    total_compound = 0.0

    for text in texts:
        if not text:
            continue
        scores = analyzer.polarity_scores(text)
        compound = scores['compound']
        total_compound += compound

        if compound >= 0.05:
            pos += 1
        elif compound <= -0.05:
            neg += 1
        else:
            neu += 1

    return pos, neg, neu, total_compound


def perform_sentiment_analysis():
    client, db, collection = get_connection()
    try:
        total_docs = collection.estimated_document_count()
        print(f"[INFO] Fetching all {total_docs:,} headlines for Sentiment Analysis (VADER)...")
        print("[INFO] Utilizing multiprocessing to speed up NLP analysis on the entire dataset.")

        cursor = collection.find({}, {"headline_text": 1, "_id": 0})

        positive = 0
        negative = 0
        neutral = 0
        total_compound = 0.0

        batch_size = 50000
        batch = []

        # Setup multiprocessing pool
        num_cores = max(1, multiprocessing.cpu_count() - 1)

        with ProcessPoolExecutor(max_workers=num_cores) as executor:
            futures = []

            count = 0
            for doc in cursor:
                text = doc.get("headline_text", "")
                if text:
                    batch.append(text)

                count += 1
                if len(batch) >= batch_size:
                    futures.append(executor.submit(analyze_batch, batch))
                    batch = []
                    print(f"       ... Dispatched {count:,} records for processing ...")

            # submit remaining
            if batch:
                futures.append(executor.submit(analyze_batch, batch))
                print(f"       ... Dispatched {count:,} records for processing ...")

            print(f"[INFO] Waiting for all {len(futures)} batches to complete...")

            completed_batches = 0
            for future in as_completed(futures):
                p, n, ne, comp = future.result()
                positive += p
                negative += n
                neutral += ne
                total_compound += comp
                completed_batches += 1
                if completed_batches % 10 == 0:
                    print(f"       ... {completed_batches}/{len(futures)} batches finished ...")

        total_analyzed = positive + negative + neutral
        avg_compound = total_compound / total_analyzed if total_analyzed > 0 else 0

        print(f"[INFO] Sentiment analysis completed (VADER).")
        print(f"       Positive: {positive:,} | Negative: {negative:,} | Neutral: {neutral:,}")
        print(f"       Average Compound Score: {avg_compound:.4f}")

        # Save results to a new collection
        db.sentiment_distribution.drop()
        db.sentiment_distribution.insert_one({
            "positive": positive,
            "negative": negative,
            "neutral": neutral,
            "sample_size": total_docs,
            "avg_compound_score": round(avg_compound, 4),
            "analyzer": "VADER"
        })

        print("[INFO] Results saved to 'sentiment_distribution' collection.")

    except Exception as e:
        print(f"[ERROR] Sentiment analysis failed: {e}")
    finally:
        close_connection(client)


if __name__ == "__main__":
    perform_sentiment_analysis()
