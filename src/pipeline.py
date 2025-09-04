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
    scores = []
    sentiments = []
    
    if results is not None:
        for res in results:
            if isinstance(res, dict) and 'label' in res and 'score' in res:
                sentiments.append(str(res['label']).capitalize())
                scores.append(float(res['score']))
    
    if sentiments:  # Only update if we have results
        valid_texts_df['sentiment'] = sentiments
    valid_texts_df['sentiment_score'] = scores
    
    df = df.merge(valid_texts_df[['sentiment', 'sentiment_score']], left_index=True, right_index=True, how='left')
    df.dropna(subset=['sentiment'], inplace=True)
    
    return df
