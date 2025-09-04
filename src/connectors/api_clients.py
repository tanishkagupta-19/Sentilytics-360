import os
import tweepy
import praw
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

def fetch_twitter_data(keyword, max_results=50):
    bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
    if not bearer_token:
        raise ValueError("TWITTER_BEARER_TOKEN environment variable not set.")
    
    client = tweepy.Client(bearer_token)
    query = f"{keyword} -is:retweet lang:en"
    
    response = client.search_recent_tweets(
        query=query, 
        max_results=max_results, 
        tweet_fields=["created_at"]
    )
    
    data = getattr(response, 'data', None)
    
    if data:
        return data
    return []

def fetch_reddit_data(keyword, max_results=50):
    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        raise ValueError("Reddit API credentials not set in environment variables.")

    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent="Sentilytics360 Scraper v1.0"
    )
    
    subreddit = reddit.subreddit("all")
    posts = []
    for sub in subreddit.search(keyword, limit=max_results, sort="new"):
        posts.append({
            "created_at": pd.to_datetime(sub.created, unit='s'),
            "text": f"{sub.title}. {sub.selftext}"
        })
    return posts