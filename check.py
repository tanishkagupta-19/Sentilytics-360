from src.connectors.api_clients import search_twitter

tweets = search_twitter("Elon Musk", 10)
print(tweets)
