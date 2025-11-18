import requests
import snscrape.modules.twitter as sntwitter
import pandas as pd


# ======================================================
# 1. FETCH TWITTER DATA  (SNSCRAPE)
# ======================================================
def fetch_twitter_data(keyword, max_results=50):
    tweets = []
    try:
        scraper = sntwitter.TwitterSearchScraper(f'"{keyword}"')
        for tweet in scraper.get_items():
            if len(tweets) >= max_results:
                break
            tweets.append({
                "source": "Twitter",
                "created_at": tweet.date,
                "text": tweet.rawContent
            })
    except Exception as e:
        print(f"[Twitter Error] {e}")
        return []
    print(f"[Twitter] Fetched {len(tweets)} tweets for '{keyword}'")
    return tweets


# ======================================================
# 2. FETCH REDDIT DATA  (PUSHSIFT API)
# ======================================================
def fetch_reddit_data(keyword, max_results=50):
    url = f"https://www.reddit.com/search.json?q={keyword}&limit={max_results}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers)
        json_data = response.json()
    except Exception as e:
        print(f"[Reddit Error] {e}")
        return []

    posts = []
    for post in json_data.get("data", {}).get("children", []):
        data = post.get("data", {})
        posts.append({
            "source": "Reddit",
            "created_at": pd.to_datetime(data.get("created_utc", None), unit='s', errors='coerce'),
            "text": f"{data.get('title', '')}. {data.get('selftext', '')}"
        })

    print(f"[Reddit] Fetched {len(posts)} posts for '{keyword}'")

    return posts