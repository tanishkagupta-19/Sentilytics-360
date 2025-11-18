import os
import praw
import pandas as pd
from dotenv import load_dotenv
from ntscraper import Nitter

load_dotenv()
scraper = Nitter(log_level=1)

def fetch_twitter_data(keyword, max_results=10):
    print(f"[Twitter] Searching for: {keyword}...")
    try:
        tweets = scraper.get_tweets(
            keyword,
            mode='term',
            number=max_results,
            language='en'
        )
        final_data = []
        if 'tweets' in tweets and len(tweets['tweets']) > 0:
            for tweet in tweets['tweets']:
                final_data.append({
                    "text": tweet['text'],
                    "created_at": tweet['date'],
                    "source": "twitter"
                })
        else:
            print("[Twitter] No tweets found.")
        return final_data
    except Exception as e:
        print(f"[Twitter Error] Could not fetch data: {e}")
        return []

def fetch_reddit_data(keyword, max_results=10):
    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    if not client_id or not client_secret:
        print("[Reddit Error] Credentials not set.")
        return []
    print(f"[Reddit] Searching for: {keyword}...")
    try:
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent="Sentilytics360 Scraper v1.0"
        )
        subreddit = reddit.subreddit("all")
        posts = []
        for sub in subreddit.search(keyword, limit=max_results, sort="new"):
            posts.append({
                "text": f"{sub.title} {sub.selftext}",
                "created_at": pd.to_datetime(sub.created_utc, unit='s'),
                "source": "reddit"
            })
        return posts
    except Exception as e:
        print(f"[Reddit Error] Could not fetch data: {e}")
        return []

if __name__ == "__main__":
    SEARCH_TERM = "AI Investment bubble"
    MAX_RESULTS = 10

    twitter_data = fetch_twitter_data(SEARCH_TERM, MAX_RESULTS)
    reddit_data = fetch_reddit_data(SEARCH_TERM, MAX_RESULTS)

    all_data = twitter_data + reddit_data

    if not all_data:
        print("No data was fetched.")
    else:
        print("--- Combined Data (List of Dictionaries) ---")
        print(all_data)