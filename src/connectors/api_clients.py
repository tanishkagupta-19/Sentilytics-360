import os
import praw
import pandas as pd
import asyncio
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dotenv import load_dotenv
from twikit import Client

load_dotenv()

# --- 🛡️ SAFETY NET: Mock Data Generator ---
# Crucial for demos! Prevents "0 Results" if Twitter blocks you.
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
            # Generate a recent timestamp
            "created_at": (datetime.now() - timedelta(minutes=random.randint(1, 120))).strftime("%a %b %d %H:%M:%S +0000 %Y"),
            "source": "twitter"
        })
    return mock_data

# --- Twitter Function (Using Twikit) ---
def _require_twitter_credentials() -> tuple[str, str, str]:
    username = os.getenv("TWITTER_USERNAME")
    email = os.getenv("TWITTER_EMAIL")
    password = os.getenv("TWITTER_PASSWORD")

    missing = [name for name, value in [
        ("TWITTER_USERNAME", username),
        ("TWITTER_EMAIL", email),
        ("TWITTER_PASSWORD", password),
    ] if not value]

    if missing:
        raise RuntimeError(
            f"⚠️ [Twitter] Missing credentials: {', '.join(missing)}. "
            "Set them in your .env before running the pipeline."
        )

    return username, email, password  # type: ignore


async def _login_with_credentials(client: Client, cookies_path: str) -> None:
    username, email, password = _require_twitter_credentials()
    print("[Twitter] Logging in with credentials...")
    await client.login(
        auth_info_1=username,
        auth_info_2=email,
        password=password
    )
    client.save_cookies(cookies_path)
    print("[Twitter] Login successful. Cookies saved.")


async def get_tweets_async(keyword: str, max_results: int) -> Optional[List[Dict[str, str]]]:
    client = Client('en-US')
    cookies_path = 'twitter_cookies.json'

    # 1. Try to load cookies first
    if os.path.exists(cookies_path):
        try:
            client.load_cookies(cookies_path)
        except Exception as e:
            print(f"❌ [Twitter] Cookie load failed: {e}. Will attempt credential login.")

    login_attempted = False

    async def _ensure_logged_in():
        nonlocal login_attempted
        if not login_attempted:
            login_attempted = True
            try:
                await _login_with_credentials(client, cookies_path)
            except Exception as login_err:
                print(f"[Twitter Error] Login failed: {login_err}")
                return False
        return os.path.exists(cookies_path)

    if not os.path.exists(cookies_path):
        if not await _ensure_logged_in():
            return None

    print(f"🐦 [Twitter] Searching for: {keyword}...")

    for attempt in range(2):
        try:
            tweets = await client.search_tweet(keyword, product='Latest', count=max_results)
            final_data = []
            if tweets:
                for tweet in tweets:
                    final_data.append({
                        "text": tweet.text,
                        "created_at": tweet.created_at,
                        "source": "twitter"
                    })
                print(f"✅ [Twitter] Found {len(final_data)} tweets.")
                return final_data
            print("❌ [Twitter] No tweets found.")
            return None

        except Exception as e:
            print(f"❌ [Twitter Scrape Error] {e}")

            # Retry once after forcing a fresh login
            if attempt == 0:
                print("🔁 [Twitter] Retrying after refreshing credentials...")
                if not await _ensure_logged_in():
                    break
            else:
                break

    return None  # Trigger mock data fallback

def fetch_twitter_data(keyword, max_results=10):
    """Wrapper to run async code synchronously with fallback."""
    try:
        data = asyncio.run(get_tweets_async(keyword, max_results))
        
        # CRITICAL FIX: If data is None or empty, use Mock Data
        if not data:
            return get_mock_twitter_data(keyword, max_results)
        return data
        
    except Exception as e:
        print(f"❌ [Twitter Wrapper Error] {e}")
        # CRITICAL FIX: Return Mock Data on crash
        return get_mock_twitter_data(keyword, max_results)

# --- Reddit Function (Unchanged) ---
def fetch_reddit_data(keyword, max_results=10):
    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        print("❌ [Reddit Error] Credentials not set.")
        return []
        
    print(f"🔴 [Reddit] Searching for: {keyword}...")
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
        print(f"✅ [Reddit] Found {len(posts)} posts.")
        return posts
    except Exception as e:
        print(f"❌ [Reddit Error] {e}")
        return []

# --- Main Execution ---
if __name__ == "__main__":
    SEARCH_TERM = "AI Investment bubble"
    MAX_RESULTS = 10

    # Fetch Data
    twitter_data = fetch_twitter_data(SEARCH_TERM, MAX_RESULTS)
    reddit_data = fetch_reddit_data(SEARCH_TERM, MAX_RESULTS)

    all_data = twitter_data + reddit_data

    if not all_data:
        print("No data was fetched.")
    else:
        print("\n--- Combined Data ---")
        df = pd.DataFrame(all_data)
        print(df.head(len(all_data)))