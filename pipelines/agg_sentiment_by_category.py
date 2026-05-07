# Sentiment Analysis by Category — Which news categories are most positive/negative?

import sys
import os

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
except ImportError:
    print("[ERROR] Please install vaderSentiment first: pip install vaderSentiment")
    sys.exit(1)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config.connection import get_connection, close_connection


def compute_sentiment_by_category():
    """
    For each headline category, compute the average VADER compound score.
    This reveals which news topics tend to be positive vs negative.
    """
    client, db, collection = get_connection()
    try:
        print("[INFO] Computing sentiment scores per category...")
        print("[INFO] This analyzes a sample of headlines from each category using VADER.")

        analyzer = SentimentIntensityAnalyzer()

        # Get top categories first
        top_categories = list(db.category_counts.find().sort("count", -1).limit(20))

        if not top_categories:
            print("[WARN] No category data found. Run agg_category_count.py first.")
            return

        results = []
        SAMPLE_SIZE = 5000

        for i, cat_doc in enumerate(top_categories):
            category = cat_doc["_id"]
            total_in_cat = cat_doc["count"]

            if not category:
                continue

            cursor = collection.find(
                {"headline_category": category},
                {"headline_text": 1, "_id": 0}
            ).limit(SAMPLE_SIZE)

            compound_sum = 0.0
            pos_count = 0
            neg_count = 0
            neu_count = 0
            analyzed = 0

            for doc in cursor:
                text = doc.get("headline_text", "")
                if not text:
                    continue
                scores = analyzer.polarity_scores(text)
                compound = scores["compound"]
                compound_sum += compound
                analyzed += 1

                if compound >= 0.05:
                    pos_count += 1
                elif compound <= -0.05:
                    neg_count += 1
                else:
                    neu_count += 1

            if analyzed == 0:
                continue

            avg_compound = compound_sum / analyzed

            results.append({
                "category": category,
                "avg_compound": round(avg_compound, 4),
                "positive_pct": round(pos_count / analyzed * 100, 1),
                "negative_pct": round(neg_count / analyzed * 100, 1),
                "neutral_pct": round(neu_count / analyzed * 100, 1),
                "sample_size": analyzed,
                "total_headlines": total_in_cat
            })

            label = "🟢" if avg_compound > 0.05 else "🔴" if avg_compound < -0.05 else "⚪"
            print(f"  {label} {category:25s} → avg: {avg_compound:+.4f}  "
                  f"(+{pos_count} / -{neg_count} / ~{neu_count})  [{i+1}/{len(top_categories)}]")

        # Save to MongoDB
        db.sentiment_by_category.drop()
        if results:
            db.sentiment_by_category.insert_many(results)
            print(f"\n[INFO] Sentiment by category saved to 'sentiment_by_category' ({len(results)} categories).")
        else:
            print("[WARN] No results to save.")

    except Exception as e:
        print(f"[ERROR] Sentiment by category failed: {e}")
    finally:
        close_connection(client)


if __name__ == "__main__":
    compute_sentiment_by_category()
