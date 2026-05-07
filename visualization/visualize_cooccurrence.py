# Visualization: Word Co-occurrence Network Graph

import sys
import os
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config.connection import get_connection, close_connection

try:
    import networkx as nx
except ImportError:
    print("[ERROR] Please install networkx: pip install networkx")
    sys.exit(1)


def visualize_cooccurrence():
    client, db, collection = get_connection()
    try:
        cursor = db.word_cooccurrence.find().sort("count", -1).limit(60)
        data = list(cursor)

        if not data:
            print("[WARNING] No co-occurrence data found. Run agg_cooccurrence.py first.")
            return

        # Build network graph
        G = nx.Graph()

        max_count = data[0]["count"] if data else 1

        for doc in data:
            w1 = doc["word1"]
            w2 = doc["word2"]
            count = doc["count"]
            weight = count / max_count

            G.add_edge(w1, w2, weight=weight, count=count)

        # Calculate node sizes based on degree (connections)
        degrees = dict(G.degree())
        node_sizes = [degrees[n] * 150 + 100 for n in G.nodes()]

        # Calculate edge widths based on weight
        edge_weights = [G[u][v]['weight'] * 4 + 0.5 for u, v in G.edges()]
        edge_colors = [plt.cm.Blues(G[u][v]['weight'] * 0.8 + 0.2) for u, v in G.edges()]

        # Layout
        plt.figure(figsize=(16, 12))
        pos = nx.spring_layout(G, k=2.5, iterations=50, seed=42)

        # Draw edges
        nx.draw_networkx_edges(G, pos, width=edge_weights, edge_color=edge_colors, alpha=0.6)

        # Draw nodes
        nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color='#FF6B6B',
                               edgecolors='#333', linewidths=0.8, alpha=0.85)

        # Draw labels
        nx.draw_networkx_labels(G, pos, font_size=8, font_weight='bold', font_color='#1a1a2e')

        plt.title('Word Co-occurrence Network\n(Top 60 word pairs from news headlines)',
                  fontsize=14, fontweight='bold')
        plt.axis('off')
        plt.tight_layout()

        # Save figure
        out_dir = os.path.join(os.path.dirname(__file__), "..", "output")
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, "cooccurrence_network.png")
        plt.savefig(out_path, dpi=300, bbox_inches='tight')
        print(f"[INFO] Co-occurrence network graph saved to {out_path}")

    except Exception as e:
        print(f"[ERROR] Failed to visualize co-occurrence: {e}")
    finally:
        close_connection(client)


if __name__ == "__main__":
    visualize_cooccurrence()
