from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database.db import engine, get_db
from database import models
from src.processing.pipeline import run_sentiment_pipeline

# --- Create Tables ---
models.Base.metadata.create_all(bind=engine)

# --- Initialize ---
app = FastAPI()

# --- CORS (Important for frontend working on another port) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Request Schema ---
class KeywordRequest(BaseModel):
    keyword: str
    max_results: int = 50

# ----------------------------------------------------------
# 1. BACKEND ENDPOINT MATCHING YOUR FRONTEND
# ----------------------------------------------------------
@app.get("/api/sentiment")
def sentiment(query: str):
    """
    Called by frontend using:
    GET http://localhost:5000/api/sentiment?query=tesla
    """

    try:
        df = run_sentiment_pipeline(query, 200)

        return {
            "keyword": query,
            "total_results": len(df),
            "sentiment_breakdown": (
                df["sentiment"].value_counts().to_dict()
                if "sentiment" in df.columns else {}
            ),
            "data": df.to_dict(orient="records"),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")


# ----------------------------------------------------------
# 2. OPTIONAL — Your existing POST endpoint (kept as-is)
# ----------------------------------------------------------
@app.post("/api/run_analysis/")
def run_analysis_endpoint(request: KeywordRequest):
    try:
        df = run_sentiment_pipeline(request.keyword, request.max_results)
        return {
            "status": "success",
            "message": f"Pipeline completed for '{request.keyword}'. {len(df)} results saved to DB."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {e}")


# ----------------------------------------------------------
# 3. OPTIONAL — Fetch all DB results (kept as-is)
# ----------------------------------------------------------
@app.get("/api/results/")
def get_all_results(db: Session = Depends(get_db)):
    results = db.query(models.SentimentResult).all()
    return results
