import pandas as pd
from database.db import engine
from ..connectors.api_clients import fetch_twitter_data, fetch_reddit_data
from .text_cleaner import preprocess_text
from ..analysis.model import get_analyzer

def run_sentiment_pipeline(keyword, max_results=50):
    analyzer = get_analyzer()  
    try:
        twitter_posts = fetch_twitter_data(keyword, max_results)
    except Exception as e:
        print(f"Twitter fetch failed: {e}")
        twitter_posts = []

    try:
        reddit_posts = fetch_reddit_data(keyword, max_results)
    except Exception as e:
        print(f"Reddit fetch failed: {e}")
        reddit_posts = []

    all_posts = []
    for tweet in twitter_posts:
        all_posts.append({
            "source": "Twitter",
            "created_at": tweet.get("created_at"),
            "text": tweet.get("text", "")
        })
    for post in reddit_posts:
        all_posts.append({
            "source": "Reddit",
            "created_at": post.get('created_at'),
            "text": post.get('text', "")
        })

    if not all_posts:
        return pd.DataFrame()

    df = pd.DataFrame(all_posts)
    df['cleaned_text'] = df['text'].apply(preprocess_text)

    valid_texts_df = df[df['cleaned_text'].str.len() > 0].copy()
    if valid_texts_df.empty:
        return pd.DataFrame()

    try:
        results = analyzer.analyze(valid_texts_df['cleaned_text'].tolist())
    except Exception as e:
        print(f"Sentiment analysis failed: {e}")
        results = []

    if results and len(results) == len(valid_texts_df):
        valid_texts_df['sentiment'] = [str(res['label']).capitalize() for res in results]
        valid_texts_df['sentiment_score'] = [res['score'] for res in results]
    else:
        valid_texts_df['sentiment'] = None
        valid_texts_df['sentiment_score'] = None

    df = df.merge(valid_texts_df[['sentiment', 'sentiment_score']], left_index=True, right_index=True, how='left')
    df.dropna(subset=['sentiment'], inplace=True)


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
