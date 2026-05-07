import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config.connection import get_connection, close_connection

# Common English stop words that add no analytical value
STOP_WORDS = [
    "the", "and", "for", "with", "from", "have", "this", "that", "will",
    "are", "was", "were", "been", "being", "has", "had", "does", "did",
    "but", "not", "you", "all", "can", "her", "his", "its", "our",
    "they", "them", "their", "what", "which", "who", "whom", "when",
    "where", "why", "how", "each", "every", "both", "few", "more",
    "most", "other", "some", "such", "than", "too", "very", "just",
    "about", "above", "after", "again", "also", "any", "because",
    "before", "below", "between", "could", "into", "may", "might",
    "must", "need", "only", "over", "should", "then", "these", "those",
    "through", "under", "until", "upon", "would", "your", "says",
    "said", "news", "year", "years", "day", "days", "time", "like",
    "make", "made", "get", "got", "take", "taken", "come", "came",
    "know", "known", "want", "look", "use", "find", "give", "tell",
    "work", "call", "try", "ask", "seem", "feel", "leave", "keep",
]


def compute_word_frequencies():
    client, db, collection = get_connection()
    try:
        print("Running word frequency aggregation (with stop-word filtering)...")
        pipeline = [
            {"$project": {"words": {"$split": [{"$toLower": "$headline_text"}, " "]}}},
            {"$unwind": "$words"},
            # Filter out short words (3 chars or less)
            {"$match": {"$expr": {"$gt": [{"$strLenCP": "$words"}, 3]}}},
            # Filter out stop words
            {"$match": {"words": {"$nin": STOP_WORDS}}},
            {"$group": {"_id": "$words", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 500},
            {"$out": "word_frequencies"}
        ]
        collection.aggregate(pipeline, allowDiskUse=True)
        print("[INFO] Word frequency aggregation completed and saved to 'word_frequencies'.")
        print(f"[INFO] Filtered out {len(STOP_WORDS)} common stop words for cleaner results.")
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        close_connection(client)

if __name__ == "__main__":
    compute_word_frequencies()
