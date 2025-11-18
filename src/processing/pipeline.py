from database.db import engine
from ..connectors.api_clients import fetch_twitter_data, fetch_reddit_data
from .text_cleaner import preprocess_text
from ..analysis.model import get_analyzer
import pandas as pd

def _standardize_posts(posts, source):
    """Internal helper to ensure posts are dicts with standard keys."""
    standardized = []
    for post in posts:
        # Crucial fix: Accessing dictionary keys instead of object attributes
        standardized.append({
            "source": source,
            "created_at": post.get('created_at'),
            "text": post.get('text', "")
        })
    return standardized

def run_sentiment_pipeline(keyword, max_results=50):
    analyzer = get_analyzer()

    # --- 1. EXTRACT ---
    twitter_posts = []
    try:
        twitter_posts = fetch_twitter_data(keyword, max_results)
    except Exception as e:
        print(f"Twitter fetch failed: {e}")

    reddit_posts = []
    try:
        reddit_posts = fetch_reddit_data(keyword, max_results)
    except Exception as e:
        print(f"Reddit fetch failed: {e}")

    # --- Combine and Standardize Data (using fixed logic) ---
    all_posts = _standardize_posts(twitter_posts, "Twitter")
    all_posts.extend(_standardize_posts(reddit_posts, "Reddit"))
    
    if not all_posts:
        print("No posts were fetched from either source. Returning empty DataFrame.")
        return pd.DataFrame()

    df = pd.DataFrame(all_posts)
    df['cleaned_text'] = df['text'].apply(preprocess_text)

    # --- 2. TRANSFORM (Analysis) ---
    # NOTE: Do NOT reset the index here. It preserves the link to df.
    valid_texts_df = df[df['cleaned_text'].str.len() > 0].copy() 
    if valid_texts_df.empty:
        print("All fetched texts were empty after cleaning. Returning empty DataFrame.")
        return pd.DataFrame()

    # Apply analysis
    results_df = pd.DataFrame()
    try:
        raw_results = analyzer.analyze(valid_texts_df['cleaned_text'].tolist())
        results_df = pd.DataFrame(raw_results)
        
        # Rename and clean sentiment columns for merge
        results_df.rename(columns={'label': 'sentiment', 'score': 'sentiment_score'}, inplace=True)
        results_df['sentiment'] = results_df['sentiment'].astype(str).str.capitalize()

    except Exception as e:
        print(f"Sentiment analysis failed: {e}. Skipping analysis and database save.")
        return df # Return raw DataFrame if analysis fails

    # NEW: Prepare results_df for index-based merge
    # Set the index of results_df to match the original index of valid_texts_df
    results_df.index = valid_texts_df.index
    
    # Merge results back into the original DataFrame using index
    df = df.merge(
        results_df[['sentiment', 'sentiment_score']], 
        left_index=True,          # Merge on df's index
        right_index=True,         # Merge on results_df's index
        how='left'
    )
    
    # Clean up the result
    df.dropna(subset=['sentiment'], inplace=True) # Drop rows where analysis failed/wasn't performed

    # --- 3. LOAD (Database) ---
    db_columns = df[['text', 'sentiment', 'sentiment_score']].copy()

    db_columns.rename(columns={
        'text': 'input_text',
        'sentiment': 'sentiment_label',
    }, inplace=True)

    try:
        db_columns.to_sql(
            name='sentiment_results',
            con=engine,
            if_exists='append',
            index=False
        )
        print(f"Successfully saved {len(db_columns)} results to the database.")
    except Exception as e:
        print(f"DATABASE SAVE FAILED: {e}")

    return df