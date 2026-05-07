import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from PIL import Image

# Import MongoDB connection
from config.connection import get_connection, close_connection

# Page Configuration
st.set_page_config(
    page_title="India News Analytics",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
    <style>
    .stMetric {
        background-color: #1E2127;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    .block-container {
        padding-top: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📰 India News Big Data Dashboard")
st.markdown("Interactive analytics dashboard built with **Streamlit**, **Plotly**, and **MongoDB**.")

# ---------------------------------------------------------
# Data Fetching Functions (Cached to avoid multiple DB calls)
# ---------------------------------------------------------
@st.cache_data(ttl=600)
def fetch_metrics():
    client, db, collection = get_connection()
    try:
        total_headlines = collection.estimated_document_count()
        total_categories = db.category_counts.count_documents({})
        return total_headlines, total_categories
    except Exception as e:
        return 0, 0
    finally:
        close_connection(client)

@st.cache_data(ttl=600)
def fetch_yearly_counts():
    client, db, collection = get_connection()
    try:
        cursor = db.yearly_counts.find().sort("_id", 1)
        data = list(cursor)
        df = pd.DataFrame(data)
        if not df.empty:
            df.rename(columns={"_id": "Year", "count": "Headlines Count"}, inplace=True)
        return df
    except Exception as e:
        return pd.DataFrame()
    finally:
        close_connection(client)

@st.cache_data(ttl=600)
def fetch_monthly_counts():
    client, db, collection = get_connection()
    try:
        cursor = db.monthly_counts.find().sort("_id", 1)
        data = list(cursor)
        df = pd.DataFrame(data)
        if not df.empty:
            df["label"] = df["_id"].apply(lambda x: f"{x[:4]}-{x[4:]}")
            df.rename(columns={"count": "Headlines Count"}, inplace=True)
        return df
    except Exception as e:
        return pd.DataFrame()
    finally:
        close_connection(client)

@st.cache_data(ttl=600)
def fetch_category_counts():
    client, db, collection = get_connection()
    try:
        cursor = db.category_counts.find().sort("count", -1).limit(20)
        data = list(cursor)
        df = pd.DataFrame(data)
        if not df.empty:
            df.rename(columns={"_id": "Category", "count": "Headlines Count"}, inplace=True)
            df["Category"] = df["Category"].apply(lambda x: "unknown" if not x else x)
        return df
    except Exception as e:
        return pd.DataFrame()
    finally:
        close_connection(client)

@st.cache_data(ttl=600)
def fetch_sentiment_data():
    client, db, collection = get_connection()
    try:
        doc = db.sentiment_distribution.find_one()
        if doc:
            return pd.DataFrame({
                "Sentiment": ["Positive", "Negative", "Neutral"],
                "Count": [doc.get("positive", 0), doc.get("negative", 0), doc.get("neutral", 0)]
            }), doc.get("avg_compound_score", None), doc.get("analyzer", "Unknown")
        return pd.DataFrame(), None, None
    except Exception as e:
        return pd.DataFrame(), None, None
    finally:
        close_connection(client)

@st.cache_data(ttl=600)
def fetch_sentiment_by_category():
    client, db, collection = get_connection()
    try:
        cursor = db.sentiment_by_category.find().sort("avg_compound", -1)
        data = list(cursor)
        df = pd.DataFrame(data)
        return df
    except Exception as e:
        return pd.DataFrame()
    finally:
        close_connection(client)

@st.cache_data(ttl=600)
def fetch_cooccurrence():
    client, db, collection = get_connection()
    try:
        cursor = db.word_cooccurrence.find().sort("count", -1).limit(30)
        data = list(cursor)
        df = pd.DataFrame(data)
        return df
    except Exception as e:
        return pd.DataFrame()
    finally:
        close_connection(client)

def search_headlines(query, limit=50):
    client, db, collection = get_connection()
    try:
        cursor = collection.find(
            {"$text": {"$search": query}},
            {"score": {"$meta": "textScore"}, "headline_text": 1, "headline_category": 1, "publish_date": 1, "_id": 0}
        ).sort([("score", {"$meta": "textScore"})]).limit(limit)
        return list(cursor)
    except Exception as e:
        return []
    finally:
        close_connection(client)

# ---------------------------------------------------------
# Sidebar — Filters & Search
# ---------------------------------------------------------
st.sidebar.header("🔧 Dashboard Controls")

# Search Box
st.sidebar.subheader("🔍 Search Headlines")
search_query = st.sidebar.text_input("Search in 3.8M headlines", placeholder="e.g. cricket, election, covid...")

# ---------------------------------------------------------
# Fetch Data
# ---------------------------------------------------------
total_headlines, total_categories = fetch_metrics()
df_yearly = fetch_yearly_counts()
df_monthly = fetch_monthly_counts()
df_categories = fetch_category_counts()
df_sentiment, avg_compound, analyzer_name = fetch_sentiment_data()
df_sent_by_cat = fetch_sentiment_by_category()
df_cooccurrence = fetch_cooccurrence()

# Year range filter in sidebar
if not df_yearly.empty:
    all_years = sorted(df_yearly["Year"].tolist())
    st.sidebar.subheader("📅 Year Filter")
    year_range = st.sidebar.select_slider(
        "Select year range",
        options=all_years,
        value=(all_years[0], all_years[-1])
    )
else:
    year_range = None

# Category filter
if not df_categories.empty:
    st.sidebar.subheader("📂 Category Filter")
    all_cats = df_categories["Category"].tolist()
    selected_cats = st.sidebar.multiselect("Select categories", all_cats, default=all_cats[:10])
else:
    selected_cats = []

# ---------------------------------------------------------
# Main Content — Tabbed Layout
# ---------------------------------------------------------

# 1. Top Metrics Row
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="Total Headlines", value=f"{total_headlines:,}")
with col2:
    st.metric(label="Unique Categories", value=f"{total_categories:,}")
with col3:
    if not df_yearly.empty:
        years_span = f"{df_yearly['Year'].min()} - {df_yearly['Year'].max()}"
        st.metric(label="Data Timespan", value=years_span)
    else:
        st.metric(label="Data Timespan", value="N/A")
with col4:
    if avg_compound is not None:
        st.metric(label=f"Avg Sentiment ({analyzer_name})", value=f"{avg_compound:+.4f}")
    else:
        st.metric(label="Avg Sentiment", value="N/A")

st.markdown("---")

# Tabs for different analyses
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Time Trends", "📊 Categories", "😊 Sentiment", "🔗 Co-occurrence", "🔍 Search"
])

# ---------------------------------------------------------
# Tab 1: Time Trends
# ---------------------------------------------------------
with tab1:
    col_yearly, col_monthly = st.columns(2)

    with col_yearly:
        st.subheader("Yearly Publishing Trend")
        if not df_yearly.empty:
            df_y_filtered = df_yearly.copy()
            if year_range:
                df_y_filtered = df_y_filtered[
                    (df_y_filtered["Year"] >= year_range[0]) &
                    (df_y_filtered["Year"] <= year_range[1])
                ]
            fig_time = px.line(
                df_y_filtered,
                x="Year",
                y="Headlines Count",
                markers=True,
                line_shape="spline",
                color_discrete_sequence=["#00b4d8"]
            )
            fig_time.update_traces(fill='tozeroy')
            st.plotly_chart(fig_time, width='stretch')
        else:
            st.warning("No yearly data found.")

    with col_monthly:
        st.subheader("Monthly Publishing Trend")
        if not df_monthly.empty:
            df_m_filtered = df_monthly.copy()
            if year_range:
                df_m_filtered = df_m_filtered[
                    (df_m_filtered["year"] >= year_range[0]) &
                    (df_m_filtered["year"] <= year_range[1])
                ]
            fig_monthly = px.line(
                df_m_filtered,
                x="label",
                y="Headlines Count",
                color_discrete_sequence=["#2196F3"]
            )
            fig_monthly.update_layout(xaxis_title="Month", xaxis_tickangle=45)
            st.plotly_chart(fig_monthly, width='stretch')
        else:
            st.warning("No monthly data found. Run agg_monthly_trend.py first.")

# ---------------------------------------------------------
# Tab 2: Categories
# ---------------------------------------------------------
with tab2:
    st.subheader("Top News Categories")
    if not df_categories.empty:
        df_cat_filtered = df_categories.copy()
        if selected_cats:
            df_cat_filtered = df_cat_filtered[df_cat_filtered["Category"].isin(selected_cats)]

        fig_cat = px.bar(
            df_cat_filtered,
            x="Headlines Count",
            y="Category",
            orientation='h',
            color="Headlines Count",
            color_continuous_scale="Viridis"
        )
        fig_cat.update_layout(yaxis={'categoryorder': 'total ascending'}, height=500)
        st.plotly_chart(fig_cat, width='stretch')
    else:
        st.warning("No category data found.")

    # Word Cloud Image
    st.subheader("☁️ Most Frequent Words (WordCloud)")
    wordcloud_path = os.path.join(os.path.dirname(__file__), "output", "wordcloud.png")
    if os.path.exists(wordcloud_path):
        image = Image.open(wordcloud_path)
        st.image(image, width='stretch', caption="Top Words in India News Headlines")
    else:
        st.warning("WordCloud image not found. Ensure visualize_words.py has run.")

# ---------------------------------------------------------
# Tab 3: Sentiment
# ---------------------------------------------------------
with tab3:
    col_pie, col_bar = st.columns(2)

    with col_pie:
        st.subheader("Overall Sentiment Distribution")
        if not df_sentiment.empty:
            fig_sent = px.pie(
                df_sentiment,
                values="Count",
                names="Sentiment",
                color="Sentiment",
                color_discrete_map={"Positive": "#2a9d8f", "Negative": "#e76f51", "Neutral": "#e9c46a"},
                hole=0.4
            )
            fig_sent.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_sent, width='stretch')
        else:
            st.warning("No sentiment data found.")

    with col_bar:
        st.subheader("Sentiment by Category")
        if not df_sent_by_cat.empty:
            fig_sbc = px.bar(
                df_sent_by_cat.sort_values("avg_compound"),
                x="avg_compound",
                y="category",
                orientation='h',
                color="avg_compound",
                color_continuous_scale="RdYlGn",
                color_continuous_midpoint=0,
                labels={"avg_compound": "Avg Compound Score", "category": "Category"}
            )
            fig_sbc.update_layout(height=500, yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig_sbc, width='stretch')
        else:
            st.warning("No sentiment-by-category data. Run agg_sentiment_by_category.py first.")

# ---------------------------------------------------------
# Tab 4: Co-occurrence
# ---------------------------------------------------------
with tab4:
    st.subheader("🔗 Top Word Pair Co-occurrences")
    if not df_cooccurrence.empty:
        fig_co = px.bar(
            df_cooccurrence.head(25),
            x="count",
            y="pair",
            orientation="h",
            color="count",
            color_continuous_scale="Blues",
            labels={"count": "Co-occurrence Count", "pair": "Word Pair"}
        )
        fig_co.update_layout(
            yaxis={"categoryorder": "total ascending"},
            height=600
        )
        st.plotly_chart(fig_co, width='stretch')

        # Show network graph image if available
        net_path = os.path.join(os.path.dirname(__file__), "output", "cooccurrence_network.png")
        if os.path.exists(net_path):
            st.subheader("Network Graph")
            image = Image.open(net_path)
            st.image(image, width='stretch', caption="Word Co-occurrence Network")
    else:
        st.warning("No co-occurrence data. Run agg_cooccurrence.py first.")

# ---------------------------------------------------------
# Tab 5: Search
# ---------------------------------------------------------
with tab5:
    st.subheader("🔍 Full-Text Search in 3.8M Headlines")

    if search_query:
        results = search_headlines(search_query, limit=100)
        if results:
            st.success(f"Found {len(results)} matching headlines for **'{search_query}'**")
            df_results = pd.DataFrame(results)
            if "score" in df_results.columns:
                df_results = df_results.sort_values("score", ascending=False)
            st.dataframe(df_results, width='stretch', height=500)
        else:
            st.warning(f"No results found for '{search_query}'. Try a different search term.")
    else:
        st.info("Use the search box in the sidebar to search across all 3.8 million headlines using MongoDB Full-Text Search.")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "India News Big Data Analytics Dashboard | "
    "Built with Streamlit, Plotly, MongoDB & VADER NLP"
    "</div>",
    unsafe_allow_html=True
)
