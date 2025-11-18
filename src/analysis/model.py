from typing import List, Dict, Union
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TextClassificationPipeline
from functools import lru_cache

class SentimentAnalyzer:
    def __init__(self, model_name: str = "cardiffnlp/twitter-roberta-base-sentiment-latest"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        
        self.pipeline = TextClassificationPipeline(
            model=self.model,
            tokenizer=self.tokenizer,
            task="text-classification"
        )

        self.label_map = {
            "LABEL_0": "Negative",
            "LABEL_1": "Neutral",
            "LABEL_2": "Positive"
        }

    def analyze(self, texts: List[str]) -> List[Dict[str, Union[str, float]]]:
        if not texts or not isinstance(texts, list):
            return []
        cleaned_texts = [str(t) for t in texts if t]
        if not cleaned_texts:
            return []
        
        results = self.pipeline(cleaned_texts)
        
        normalized = []
        for res in results:
            normalized.append({
                "label": self.label_map.get(res["label"], res["label"]),
                "score": float(res["score"])
            })
        
        return normalized
@lru_cache(maxsize=1)
def get_analyzer():
    return SentimentAnalyzer()