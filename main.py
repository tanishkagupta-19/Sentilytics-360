from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Depends, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
import logging
import asyncio
import os

from database.db import engine, get_db
from database import models
from src.processing.pipeline import run_sentiment_pipeline

# --- Create Tables ---
models.Base.metadata.create_all(bind=engine)

# --- Logging setup ---
logger = logging.getLogger("sentilytics")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)

logger.info("[ENV] Reddit client ID present: %s", bool(os.getenv("REDDIT_CLIENT_ID")))
logger.info("[ENV] Reddit secret present: %s", bool(os.getenv("REDDIT_CLIENT_SECRET")))

# --- Initialize ---
app = FastAPI(
    title="Sentilytics 360 API",
    description="API for real-time sentiment analysis across social platforms.",
    version="1.0.0"
)

# --- CORS (Important for frontend working on another port) ---
# Restrict to frontend origin in production
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url, "http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

# --- Request Schema ---
class KeywordRequest(BaseModel):
    keyword: str
    max_results: int = 50


class SentimentResponse(BaseModel):
    keyword: str
    total_results: int
    sentiment_breakdown: dict
    data: list


class AnalysisResponse(BaseModel):
    status: str
    message: str

# ---------------------------------------------------------
# Helper functions
# ---------------------------------------------------------
def credentials_available() -> bool:
    """Check if any upstream credential (Twitter/Reddit) is configured."""
    return bool(os.getenv("TWITTER_BEARER_TOKEN")) or bool(os.getenv("REDDIT_CLIENT_ID"))


async def _run_pipeline_in_thread(keyword: str, max_results: int):
    """Run blocking pipeline in a background thread to avoid blocking the event loop."""
    return await asyncio.to_thread(run_sentiment_pipeline, keyword, max_results)


def _background_pipeline(keyword: str, max_results: int):
    """Used for async background execution."""
    try:
        df = run_sentiment_pipeline(keyword, max_results)
        logger.info("Background job completed: keyword=%s, rows=%d",
                     keyword, len(df) if hasattr(df, "shape") else 0)
        # Results are automatically saved to DB by the pipeline
    except Exception:
        logger.exception("Background job failed for keyword=%s", keyword)

# ----------------------------------------------------------
# 1. FRONTEND API ENDPOINT
# ----------------------------------------------------------
@app.get("/")
def root():
    """Root endpoint - API health check."""
    return {"message": "Welcome to the Sentilytics 360 API!"}


@app.get("/api/sentiment", response_model=SentimentResponse)
async def sentiment(query: str = Query(..., min_length=1, max_length=200)):
    """
    Analyze sentiment for a keyword.
    
    - `query`: Search term (max 200 chars)
    
    Returns sentiment breakdown and up to 200 posts
    """
    if not query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be only whitespace.")

    try:
        logger.info(f"Processing sentiment analysis for query: {query}")
        df = await asyncio.to_thread(run_sentiment_pipeline, query, 200)

        if df.empty:
            return SentimentResponse(
                keyword=query,
                total_results=0,
                sentiment_breakdown={},
                data=[],
            )

        sentiment_breakdown = (
            df["sentiment"].value_counts().to_dict()
            if "sentiment" in df.columns else {}
        )

        return SentimentResponse(
            keyword=query,
            total_results=len(df),
            sentiment_breakdown=sentiment_breakdown,
            data=df.to_dict(orient="records"),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error processing sentiment for query: {query}")
        raise HTTPException(status_code=500, detail="Internal server error during analysis.")


# ----------------------------------------------------------
# 2. OPTIONAL — Your existing POST endpoint
# ----------------------------------------------------------
@app.post("/api/run_analysis/", response_model=AnalysisResponse)
def run_analysis_endpoint(request: KeywordRequest):
    """Run sentiment analysis pipeline via POST request."""
    if not request.keyword or not request.keyword.strip():
        raise HTTPException(status_code=400, detail="Keyword cannot be empty.")

    if request.max_results < 1 or request.max_results > 500:
        raise HTTPException(status_code=400, detail="max_results must be between 1 and 500.")

    try:
        logger.info(f"Running analysis for keyword: {request.keyword}, max_results: {request.max_results}")
        df = run_sentiment_pipeline(request.keyword, request.max_results)
        
        result_count = len(df) if hasattr(df, "__len__") else 0
        return AnalysisResponse(
            status="success",
            message=f"Pipeline completed for '{request.keyword}'. {result_count} results saved to DB."
        )
    except Exception as e:
        logger.exception(f"Analysis failed for keyword: {request.keyword}")
        raise HTTPException(status_code=500, detail="Analysis pipeline failed. Please try again.")


# ----------------------------------------------------------
# 3. OPTIONAL — Fetch all DB results
# ----------------------------------------------------------
@app.get("/api/results/")
def get_all_results(db: Session = Depends(get_db), skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=1000)):
    """
    Fetch all results with pagination.
    
    - `skip`: Number of records to skip (default 0)
    - `limit`: Number of records to return (max 1000, default 100)
    """
    total = db.query(models.SentimentResult).count()
    results = db.query(models.SentimentResult).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "data": results
    }


# ----------------------------------------------------------
# 4. ADVANCED — Analyze endpoint with pagination and background tasks
# ----------------------------------------------------------
@app.get("/analyze")
async def analyze_keyword(
    keyword: str = Query(..., min_length=1, max_length=200),
    background_tasks: BackgroundTasks = BackgroundTasks(), 
    max_results: int = Query(25, ge=1, le=200),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    background: bool = Query(False),
):
    """Run sentiment analysis pipeline for a keyword with pagination.

    Parameters:
    - `keyword`: Search term (required, max 200 chars)
    - `max_results`: Number of posts to analyze (1-200, default 25)
    - `page`: Page number for pagination (default 1)
    - `page_size`: Results per page (1-100, default 25)
    - `background`: If true, runs async and returns 202 (default false)
    
    Requires REDDIT_CLIENT_ID environment variable to be set.
    """
    if not keyword.strip():
        raise HTTPException(status_code=400, detail="Keyword cannot be only whitespace.")

    if not credentials_available():
        logger.error("Missing upstream credentials.")
        raise HTTPException(status_code=503, detail="Upstream credentials not configured. Set REDDIT_CLIENT_ID.")

    try:
        # Run in background mode if requested
        if background:
            background_tasks.add_task(_background_pipeline, keyword, max_results)
            return {"status": "scheduled", "message": "Analysis scheduled to run in background"}

        # Run pipeline (non-blocking)
        results_df = await _run_pipeline_in_thread(keyword, max_results)

        # Validate pipeline output
        if results_df is None or not hasattr(results_df, "empty"):
            raise HTTPException(status_code=500, detail="Pipeline returned unexpected result type")

        if results_df.empty:
            return {"data": [], "summary": {"total_posts": 0, "sentiment_counts": {}, "platform_summary": {}}}

        # Convert to JSON records
        data = results_df.to_dict("records")
        total = len(data)
        start = (page - 1) * page_size
        end = start + page_size
        paged = data[start:end]

        # Summaries
        sentiment_counts = results_df["sentiment"].value_counts().to_dict() if "sentiment" in results_df.columns else {}
        platform_summary = {}
        if "source" in results_df.columns and "sentiment" in results_df.columns:
            try:
                platform_summary = (
                    results_df.groupby("source")["sentiment"]
                    .value_counts()
                    .unstack(fill_value=0)
                    .to_dict("index")
                )
            except (KeyError, ValueError):
                platform_summary = {}

        summary = {
            "total_posts": total,
            "sentiment_counts": sentiment_counts,
            "platform_summary": platform_summary,
            "page": page,
            "page_size": page_size,
            "has_next": end < total,
        }

        return {"data": paged, "summary": summary}

    except HTTPException:
        raise
    except Exception:
        logger.exception("Error during analysis for keyword=%s", keyword)
        raise HTTPException(status_code=500, detail="Internal error during analysis.")