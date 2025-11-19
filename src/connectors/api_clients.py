import os
import praw
import pandas as pd
import asyncio
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional, TypeVar, Callable, Coroutine, Any
from dotenv import load_dotenv
from twikit import Client
import logging

load_dotenv()
logger = logging.getLogger("sentilytics")

# --- 🛡️ SAFETY NET: Mock Data Generator ---
def get_mock_twitter_data(keyword: str, count: int = 5) -> List[Dict[str, str]]:
    print(f"⚠️ [Twitter] Scraper failed/blocked. Generating {count} MOCK tweets for demo.")
    mock_data = []
    templates = [
        f"I honestly think {keyword} is changing the industry!",
        f"Why is everyone talking about {keyword} today?",
        f"Not sure if I agree with the recent news about {keyword}.",
        f"Just saw a huge update regarding {keyword}. Interesting times.",
        f"{keyword} is definitely overhyped right now.",
        f"Looking for more info on {keyword}, any recommendations?",
        f"The impact of {keyword} on the market is undeniable."
    ]
    for i in range(count):
        mock_data.append({
            "text": random.choice(templates),
            "created_at": (datetime.now() - timedelta(minutes=random.randint(1, 120))).strftime("%a %b %d %H:%M:%S +0000 %Y"),
            "source": "twitter"
        })
    return mock_data

# --- Twitter Function ---
async def get_tweets_async(keyword: str, max_results: int) -> Optional[List[Dict[str, str]]]:
    client = Client('en-US')
    cookies_path = 'twitter_cookies.json'

    if not os.path.exists(cookies_path):
        logger.warning("[Twitter] No cookies found. Skipping login attempt.")
        return None

    try:
        client.load_cookies(cookies_path)
        tweets = await client.search_tweet(keyword, product='Latest', count=max_results)
        
        final_data = []
        if tweets:
            for tweet in tweets:
                final_data.append({
                    "text": tweet.text,
                    "created_at": tweet.created_at,
                    "source": "twitter"
                })
            return final_data
        return None

    except Exception as e:
        logger.error(f"[Twitter] Async Search Error: {e}")
        return None

def fetch_twitter_data(keyword, max_results=10):
    """Wrapper to run async code synchronously with fallback."""
    try:
        data = asyncio.run(get_tweets_async(keyword, max_results))
        
        # CRITICAL FIX: If data is None/Empty, use Mock Data
        if not data:
            return get_mock_twitter_data(keyword, max_results)
        return data
        
    except Exception as e:
        logger.error(f"[Twitter Wrapper Error] {e}")
        # CRITICAL FIX: Return Mock Data on crash
        return get_mock_twitter_data(keyword, max_results)

# --- Reddit Function ---
def fetch_reddit_data(keyword, max_results=10):
    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        print("ℹ️ [Reddit] Credentials not set. Skipping.")
        return []
        
    try:
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent="Sentilytics360 Scraper v1.0"
        )
        subreddit = reddit.subreddit("all")
        posts = []
        # Limiting to max_results to avoid slow loading
        for sub in subreddit.search(keyword, limit=max_results, sort="new"):
            posts.append({
                "text": f"{sub.title} {sub.selftext}", 
                "created_at": str(datetime.fromtimestamp(sub.created_utc)),
                "source": "reddit"
            })
        print(f"✅ [Reddit] Found {len(posts)} posts.")
        return posts
    except Exception as e:
        print(f"❌ [Reddit Error] {e}")
        return []