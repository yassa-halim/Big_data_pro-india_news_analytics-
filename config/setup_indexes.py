# MongoDB Index Setup — Run once after data import to speed up all queries.

from config.connection import get_connection, close_connection


def setup_indexes():
    """
    Create indexes on frequently queried fields.
    This dramatically speeds up aggregation pipelines on 3.8M+ documents.
    Safe to run multiple times — MongoDB ignores duplicate index creation.
    """
    client, db, collection = get_connection()
    try:
        print("[INFO] Setting up MongoDB indexes for performance optimization...")

        # Index on category field — speeds up category aggregation
        collection.create_index("headline_category")
        print("  ✔ Index created on 'headline_category'")

        # Index on publish_date — speeds up time-series aggregation
        collection.create_index("publish_date")
        print("  ✔ Index created on 'publish_date'")

        # Full-text search index on headline_text — enables text search
        collection.create_index([("headline_text", "text")])
        print("  ✔ Full-text search index created on 'headline_text'")

        print("[INFO] All indexes created successfully. Queries will now be significantly faster.")

    except Exception as e:
        print(f"[ERROR] Failed to create indexes: {e}")
    finally:
        close_connection(client)


if __name__ == "__main__":
    setup_indexes()
