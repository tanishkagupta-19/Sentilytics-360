# src/connectors/api_clients.py
import os
import tweepy
import praw
import pandas as pd
import logging
from dotenv import load_dotenv
from prawcore import exceptions as prawcore_exceptions
from datetime import datetime

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def search_twitter(keyword: str, max_results: int = 50) -> list:
    """
    Fetches recent tweets for a given keyword using the Twitter API v2.
    Returns data in the Sentilytics 360 standard format.
    """
    bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
    if not bearer_token:
        logging.error("TWITTER_BEARER_TOKEN environment variable is not set.")
        return []

    try:
        client = tweepy.Client(bearer_token, wait_on_rate_limit=True)
        query = f"{keyword} -is:retweet lang:en"
        
        response = client.search_recent_tweets(
            query=query, 
            max_results=max_results,
            # Request additional fields: author_id and created_at
            tweet_fields=["created_at"],
            # Request user fields to get the username
            expansions=["author_id"],
            user_fields=["username"]
        )
        
        tweets = getattr(response, 'data', None)
        includes = getattr(response, 'includes', {})
        users = includes.get('users', [])
        
        # Create a dictionary to map author_id to username
        user_map = {user.id: user.username for user in users}
        
        if not tweets:
            logging.info(f"[Twitter] No tweets found for keyword: {keyword}")
            return []
            
        tweets_data = []
        for tweet in tweets:
            username = user_map.get(tweet.author_id, "UnknownUser")
            tweets_data.append({
                "source": "Twitter",
                "text": tweet.text,
                "author": username,
                "timestamp": tweet.created_at,
                "topic": keyword,
                "link": f"https://twitter.com/{username}/status/{tweet.id}"
            })
        return tweets_data

    except tweepy.TweepyException as e:
        logging.error(f"An error occurred with the Twitter API: {e}")
        return []
    except Exception as e:
        logging.error(f"An unexpected error occurred while fetching tweets: {e}")
        return []

def search_reddit(keyword: str, max_results: int = 50) -> list:
    """
    Fetches recent Reddit posts for a given keyword from r/all.
    Returns data in the Sentilytics 360 standard format.
    """
    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        logging.error("REDDIT_CLIENT_ID or REDDIT_CLIENT_SECRET environment variables are not set.")
        return []

    try:
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent="Sentilytics360 Scraper v1.0"
        )
        
        subreddit = reddit.subreddit("all")
        
        reddit_data = []
        for post in subreddit.search(keyword, limit=max_results, sort="new"):
            reddit_data.append({
                "source": "Reddit",
                "text": f"{post.title}. {post.selftext}",
                "author": str(post.author),
                "timestamp": datetime.utcfromtimestamp(post.created_utc),
                "topic": keyword,
                "link": f"https://www.reddit.com{post.permalink}"
            })

        if not reddit_data:
            logging.info(f"[Reddit] No posts found for keyword: {keyword}")

        return reddit_data

    except prawcore_exceptions.PrawcoreException as e:
        logging.error(f"An error occurred with the Reddit API: {e}")
        return []
    except Exception as e:
        logging.error(f"An unexpected error occurred while fetching from Reddit: {e}")
        return []