import re
import string
import emoji
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")

try:
    nltk.data.find("corpora/stopwords")
except LookupError:
    nltk.download("stopwords")

stop_words = set(stopwords.words('english'))

def preprocess_text(text):
    """Cleans and normalizes raw social media text."""
    if not isinstance(text, str):
        return ""
        
    text = emoji.demojize(text, delimiters=(" ", " "))
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\@\w+|\#\w+', '', text)
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = text.lower()
    tokens = word_tokenize(text)
    filtered_words = [word for word in tokens if word.isalpha() and word not in stop_words]
    
    return " ".join(filtered_words)