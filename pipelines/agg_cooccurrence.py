# Co-occurrence Analysis — Discovers word pairs that frequently appear together.

import sys
import os
from collections import Counter
from itertools import combinations

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config.connection import get_connection, close_connection

# Same stop words as word frequency analysis
STOP_WORDS = {
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
}

SAMPLE_SIZE = 50000


def compute_cooccurrence():
    """
    For each headline, extract cleaned word pairs (bigrams via combinations)
    and count which pairs appear together most frequently.
    """
    client, db, collection = get_connection()
    try:
        print(f"[INFO] Computing word co-occurrence from a sample of {SAMPLE_SIZE:,} headlines...")

        cursor = collection.find(
            {},
            {"headline_text": 1, "_id": 0}
        ).limit(SAMPLE_SIZE)

        pair_counter = Counter()

        processed = 0
        for doc in cursor:
            text = doc.get("headline_text", "")
            if not text:
                continue

            # Clean and tokenize
            words = text.lower().split()
            words = [w for w in words if len(w) > 3 and w not in STOP_WORDS]

            # Get unique words to avoid self-pairs and duplicates
            unique_words = list(set(words))

            if len(unique_words) < 2:
                continue

            for pair in combinations(sorted(unique_words[:8]), 2):
                pair_counter[pair] += 1

            processed += 1
            if processed % 10000 == 0:
                print(f"       ... Processed {processed:,} headlines ...")

        print(f"[INFO] Processed {processed:,} headlines. Found {len(pair_counter):,} unique word pairs.")

        # Get top 200 pairs
        top_pairs = pair_counter.most_common(200)

        # Save to MongoDB
        db.word_cooccurrence.drop()
        docs = []
        for (w1, w2), count in top_pairs:
            docs.append({
                "word1": w1,
                "word2": w2,
                "pair": f"{w1} + {w2}",
                "count": count
            })

        if docs:
            db.word_cooccurrence.insert_many(docs)

        print(f"[INFO] Top 200 word co-occurrences saved to 'word_cooccurrence' collection.")
        print("[INFO] Top 15 most frequent word pairs:")
        for (w1, w2), count in top_pairs[:15]:
            print(f"  - '{w1}' + '{w2}': {count:,} times")

    except Exception as e:
        print(f"[ERROR] Co-occurrence analysis failed: {e}")
    finally:
        close_connection(client)


if __name__ == "__main__":
    compute_cooccurrence()
