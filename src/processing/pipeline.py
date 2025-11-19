from database.db import engine
# FIX: Use absolute imports instead of relative ".." imports
from src.connectors.api_clients import fetch_twitter_data, fetch_reddit_data
from src.processing.text_cleaner import preprocess_text
from src.analysis.model import get_analyzer
import pandas as pd
import logging

logger = logging.getLogger("sentilytics")

def _standardize_posts(posts, source):
    """Internal helper to ensure posts are dicts with standard keys."""
    standardized = []
    if not posts:
        return []
        
    for post in posts:
        standardized.append({
            "source": source,
            "created_at": post.get('created_at'),
            "text": post.get('text', "")
        })
    return standardized

def run_sentiment_pipeline(keyword, max_results=50):
    analyzer = get_analyzer()

    print(f"🚀 [Pipeline] Starting analysis for: {keyword}")

    # --- 1. EXTRACT ---
    # Fetch data (Twitter will use Mock Data if scraping fails)
    twitter_posts = fetch_twitter_data(keyword, max_results)
    reddit_posts = fetch_reddit_data(keyword, max_results)

    # --- Combine and Standardize ---
    all_posts = _standardize_posts(twitter_posts, "Twitter")
    all_posts.extend(_standardize_posts(reddit_posts, "Reddit"))
    
    if not all_posts:
        print("⚠️ [Pipeline] No posts found from any source.")
        return pd.DataFrame()

    df = pd.DataFrame(all_posts)
    
    # Safety check for empty text
    if 'text' not in df.columns:
        return pd.DataFrame()

    df['cleaned_text'] = df['text'].apply(preprocess_text)

    # --- 2. TRANSFORM (Analysis) ---
    # Filter out empty texts
    valid_texts_df = df[df['cleaned_text'].str.len() > 0].copy()
    
    if valid_texts_df.empty:
        return df

    # Apply analysis
    results_df = pd.DataFrame()
    try:
        # Run the actual AI model
        raw_results = analyzer.analyze(valid_texts_df['cleaned_text'].tolist())
        results_df = pd.DataFrame(raw_results)
        
        # Standardize column names
        if not results_df.empty:
            results_df.rename(columns={'label': 'sentiment', 'score': 'sentiment_score'}, inplace=True)
            results_df['sentiment'] = results_df['sentiment'].astype(str).str.lower()
        
        print(f"✅ [Pipeline] Analysis successful. Generated {len(results_df)} scores.")

    except Exception as e:
        print(f"❌ [Pipeline Error] Sentiment analysis failed: {e}")
        return df 

    # Join results back to the main dataframe
    if not results_df.empty:
        results_df.index = valid_texts_df.index
        df = df.merge(
            results_df[['sentiment', 'sentiment_score']], 
            left_index=True, 
            right_index=True, 
            how='left'
        )
    
    # Fill NaNs for display safety
    if 'sentiment' in df.columns:
        df['sentiment'] = df['sentiment'].fillna('Neutral')
        df['sentiment_score'] = df['sentiment_score'].fillna(0.0)
    else:
        # Fallback if merge failed
        df['sentiment'] = 'Neutral'
        df['sentiment_score'] = 0.0

    # --- 3. LOAD (Database) ---
    try:
        db_columns = df[['text', 'sentiment', 'sentiment_score']].copy()
        db_columns.rename(columns={
            'text': 'input_text',
            'sentiment': 'sentiment_label',
        }, inplace=True)

        db_columns.to_sql(
            name='sentiment_results',
            con=engine,
            if_exists='append',
            index=False
        )
        print(f"💾 [Database] Saved {len(db_columns)} results.")
    except Exception as e:
        print(f"⚠️ [Database Error] Save failed (Non-critical): {e}")

    return df