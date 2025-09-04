from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TextClassificationPipeline
)
from transformers.pipelines import pipeline
from typing import List, Dict, Union, Optional
from typing_extensions import Literal

class SentimentAnalyzer:
    def __init__(self, model_name: str = "cardiffnlp/twitter-roberta-base-sentiment-latest"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        
        self.pipeline = TextClassificationPipeline(
            model=self.model,
            tokenizer=self.tokenizer,
            task="text-classification",
            return_all_scores=False
        )

    def analyze(self, texts: List[str]) -> List[Dict[str, Union[str, float]]]:
        if not texts:
            return []
        
        if not isinstance(texts, list):
            return []
            
        try:
            # Clean and process texts
            cleaned_texts = [str(t) for t in texts if t]
            if not cleaned_texts:
                return []
                
            # Run sentiment analysis and ensure we get results
            results = self.pipeline(cleaned_texts)
            return results if results is not None else []
            
        except Exception:
            # Return empty list on any error to maintain interface contract
            return []