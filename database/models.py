# database/models.py
from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from datetime import datetime
from .db import Base # Import Base from db.py in the same folder

class SentimentResult(Base):
    """
    SQLAlchemy Model for storing the results of the sentiment analysis.
    """
    __tablename__ = "sentiment_results"

    id = Column(Integer, primary_key=True, index=True)
    input_text = Column(Text, nullable=False)
    sentiment_label = Column(String(50), nullable=False) # e.g., 'Positive', 'Negative'
    sentiment_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)