from src.connectors.api_clients import fetch_twitter_data

tweets = fetch_twitter_data("Elon Musk", 10)
print(tweets)
