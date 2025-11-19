from database.db import engine
from ..connectors.api_clients import fetch_twitter_data, fetch_reddit_data
from .text_cleaner import preprocess_text
from ..analysis.model import get_analyzer
import pandas as pd

def _standardize_posts(posts, source):
    """Internal helper to ensure posts are dicts with standard keys."""
    standardized = []
    for post in posts:
        # Accessing dictionary keys since our clients return dicts now
        standardized.append({
            "source": source,
            "created_at": post.get('created_at'),
            "text": post.get('text', "")
        })
    return standardized

def run_sentiment_pipeline(keyword, max_results=50):
    analyzer = get_analyzer()

    # --- 1. EXTRACT ---
    # Fetch data (Twitter will use Mock Data if scraping fails)
    twitter_posts = fetch_twitter_data(keyword, max_results)
    reddit_posts = fetch_reddit_data(keyword, max_results)

    # --- Combine and Standardize ---
    all_posts = _standardize_posts(twitter_posts, "Twitter")
    all_posts.extend(_standardize_posts(reddit_posts, "Reddit"))
    
    if not all_posts:
        print("No posts were fetched from either source.")
        return pd.DataFrame()

    df = pd.DataFrame(all_posts)
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
        results_df.rename(columns={'label': 'sentiment', 'score': 'sentiment_score'}, inplace=True)
        results_df['sentiment'] = results_df['sentiment'].astype(str).str.capitalize()
        
        print(f"✅ Analysis successful. Generated {len(results_df)} sentiment scores.")

    except Exception as e:
        print(f"❌ Sentiment analysis failed: {e}")
        # Return DataFrame without sentiment if analysis crashes
        return df 

    # Join results back to the main dataframe
    # We use the index to ensure alignment
    results_df.index = valid_texts_df.index
    df = df.merge(
        results_df[['sentiment', 'sentiment_score']], 
        left_index=True, 
        right_index=True, 
        how='left'
    )
    
    # Fill NaNs for display safety
    df['sentiment'] = df['sentiment'].fillna('Neutral')
    df['sentiment_score'] = df['sentiment_score'].fillna(0.0)

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
        print(f"Successfully saved {len(db_columns)} results to the database.")
    except Exception as e:
        print(f"DATABASE SAVE FAILED: {e}")

    return df