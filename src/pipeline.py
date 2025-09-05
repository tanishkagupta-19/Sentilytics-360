import pandas as pd
from src.connectors.api_clients import fetch_twitter_data, fetch_reddit_data
from src.processing.text_cleaner import preprocess_text
from src.analysis.model import SentimentAnalyzer

analyzer = SentimentAnalyzer()

def run_sentiment_pipeline(keyword, max_results=50):
    
    twitter_posts = fetch_twitter_data(keyword, max_results)
    reddit_posts = fetch_reddit_data(keyword, max_results)
    
    all_posts = []
    for tweet in twitter_posts:
        all_posts.append({"source": "Twitter", "created_at": tweet.created_at, "text": tweet.text})
    for post in reddit_posts:
        all_posts.append({"source": "Reddit", "created_at": post['created_at'], "text": post['text']})

    if not all_posts:
        return pd.DataFrame()

    df = pd.DataFrame(all_posts)
    df['cleaned_text'] = df['text'].apply(preprocess_text)
    
    valid_texts_df = df[df['cleaned_text'].str.len() > 0].copy()
    if valid_texts_df.empty:
        return pd.DataFrame()

        
    results = analyzer.analyze(valid_texts_df['cleaned_text'].tolist())

    # Check if the results are valid and match the expected length
    if results and len(results) == len(valid_texts_df):
        sentiments = [str(res['label']).capitalize() for res in results]
        scores = [res['score'] for res in results]
        
        valid_texts_df['sentiment'] = sentiments
        valid_texts_df['sentiment_score'] = scores
    else:
        # If no results, assign None to prevent the error
        valid_texts_df['sentiment'] = None
        valid_texts_df['sentiment_score'] = None
    
    df = df.merge(valid_texts_df[['sentiment', 'sentiment_score']], left_index=True, right_index=True, how='left')
    df.dropna(subset=['sentiment'], inplace=True)
    
    return df
