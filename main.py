# Main execution script to run the entire Big Data pipeline in one go.

import os
import sys

# Import all steps from the new project structure
from data.import_csv_to_mongo import import_data
from config.setup_indexes import setup_indexes
from pipelines.agg_category_count import count_categories
from pipelines.agg_word_freq import compute_word_frequencies
from pipelines.agg_time_series import compute_yearly_counts
from pipelines.agg_monthly_trend import compute_monthly_counts
from pipelines.sentiment_analysis import perform_sentiment_analysis
from pipelines.agg_sentiment_by_category import compute_sentiment_by_category
from pipelines.agg_cooccurrence import compute_cooccurrence
from visualization.visualize_categories import visualize_top_categories
from visualization.visualize_words import visualize_word_frequencies
from visualization.visualize_time_series import visualize_time_series
from visualization.visualize_monthly_trend import visualize_monthly_trend
from visualization.visualize_sentiment import visualize_sentiment_distribution
from visualization.visualize_sentiment_by_category import visualize_sentiment_by_category
from visualization.visualize_cooccurrence import visualize_cooccurrence

def main():
    print("="*60)
    print("🚀 STARTING INDIA NEWS BIG DATA ANALYSIS PIPELINE 🚀")
    print("="*60)
    
    print("\n[STEP 1/12] Ingesting CSV Data into MongoDB...")
    # import_data() # Uncomment if you need to re-import
    
    print("\n[STEP 2/12] Setting up MongoDB Indexes for Performance...")
    setup_indexes()
    
    print("\n[STEP 3/12] Running Aggregation Pipeline 1 (Category Count)...")
    count_categories()
    
    print("\n[STEP 4/12] Running Aggregation Pipeline 2 (Word Frequency — with Stop Words filter)...")
    compute_word_frequencies()
    
    print("\n[STEP 5/12] Running Aggregation Pipeline 3 (Yearly Time-Series)...")
    compute_yearly_counts()
    
    print("\n[STEP 6/12] Running Aggregation Pipeline 4 (Monthly Trend)...")
    compute_monthly_counts()
    
    print("\n[STEP 7/12] Running NLP Sentiment Analysis (VADER)...")
    perform_sentiment_analysis()
    
    print("\n[STEP 8/12] Running Sentiment Analysis by Category...")
    compute_sentiment_by_category()
    
    print("\n[STEP 9/12] Running Word Co-occurrence Analysis...")
    compute_cooccurrence()
    
    print("\n[STEP 10/12] Generating Charts (Categories, Words & Monthly Trend)...")
    visualize_top_categories()
    visualize_word_frequencies()
    visualize_monthly_trend()
    
    print("\n[STEP 11/12] Generating Charts (Sentiment, Sentiment by Category & Co-occurrence)...")
    visualize_time_series()
    visualize_sentiment_distribution()
    visualize_sentiment_by_category()
    visualize_cooccurrence()
    
    print("\n" + "="*60)
    print("✅ PIPELINE COMPLETED SUCCESSFULLY!")
    print(f"📊 Please check the '{os.path.abspath('output')}' folder for your charts.")
    print("="*60)
    
    print("\n[STEP 12/12] Starting Streamlit Interactive Dashboard...")
    try:
        import subprocess
        subprocess.run(["streamlit", "run", "dashboard.py"])
    except Exception as e:
        print(f"Failed to start Streamlit: {e}")

if __name__ == "__main__":
    main()
