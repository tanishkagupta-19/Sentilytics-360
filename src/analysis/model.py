from typing import List, Dict, Union, Any, cast
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import logging
import torch

logger = logging.getLogger("sentilytics")

class SentimentAnalyzer:
    def __init__(self, model_name: str = "cardiffnlp/twitter-roberta-base-sentiment-latest"):
        logger.info(f"Loading model: {model_name}")
        self.model_name = model_name
        
        # Initialize the pipeline directly (simplest & safest way)
        # We use the 'pipeline' helper which handles model/tokenizer loading automatically
        device = 0 if torch.cuda.is_available() else -1
        self.pipe = pipeline(
            "text-classification",
            model=model_name,
            tokenizer=model_name,
            device=device, # Use GPU if available
            top_k=None # Return all scores so we can normalize if needed (optional)
        )
        
        # Max length for this specific model is usually 512
        self.max_length = 512

    def analyze(self, texts: List[str]) -> List[Dict[str, Union[str, float]]]:
        if not texts:
            return []

        # 1. Basic cleaning (removing nulls/non-strings)
        valid_texts = [str(t) if t else "" for t in texts]

        results = []
        try:
            # 2. Let the pipeline handle truncation and batching natively
            # truncation=True ensures we don't crash on long texts
            raw_outputs = self.pipe(
                valid_texts, 
                truncation=True, 
                max_length=self.max_length, 
                batch_size=16
            )

            # 3. Normalize output
            # The pipeline returns a list of dicts (or list of lists if top_k is set)
            for output in raw_outputs:
                # Handle cases where top_k=None returns a single dict or list
                if isinstance(output, list):
                    # FIX: Explicitly cast for Pylance so it knows this is a list of dicts
                    output_list = cast(List[Dict[str, Any]], output)
                    # Use .get() for extra safety against missing keys
                    top_result = max(output_list, key=lambda x: x.get('score', -1.0))
                else:
                    top_result = output

                # Safely access keys with .get in case the model returns unexpected formats
                if isinstance(top_result, dict):
                    label = top_result.get('label', 'Neutral')
                    score = top_result.get('score', 0.0)
                else:
                    label = 'Neutral'
                    score = 0.0

                # Standardize labels (The model returns 'negative', 'neutral', 'positive' OR 'LABEL_0'...)
                # We normalize them to Title Case for your UI
                clean_label = "Neutral"
                label_lower = str(label).lower()
                
                if "neg" in label_lower or "label_0" in label_lower:
                    clean_label = "Negative"
                elif "pos" in label_lower or "label_2" in label_lower:
                    clean_label = "Positive"
                elif "neu" in label_lower or "label_1" in label_lower:
                    clean_label = "Neutral"

                results.append({
                    "label": clean_label,
                    "score": float(score)
                })

        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            # Return neutral fallback on crash
            return [{"label": "Neutral", "score": 0.0} for _ in texts]

        return results

# Singleton pattern (Standard Python)
_analyzer_instance = None

def get_analyzer():
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = SentimentAnalyzer()
    return _analyzer_instance