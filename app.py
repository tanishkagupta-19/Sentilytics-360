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

logger.info("[ENV] Twitter token present: %s", bool(os.getenv("TWITTER_BEARER_TOKEN")))
logger.info("[ENV] Reddit client ID present: %s", bool(os.getenv("REDDIT_CLIENT_ID")))
logger.info("[ENV] Reddit secret present: %s", bool(os.getenv("REDDIT_CLIENT_SECRET")))

# --- Initialize ---
app = FastAPI(
    title="Sentilytics 360 API",
    description="API for real-time sentiment analysis across social platforms.",
    version="1.0.0"
)

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
# 1. BACKEND ENDPOINT MATCHING YOUR FRONTEND
# ----------------------------------------------------------
@app.get("/")
def root():
    """Root endpoint - API health check."""
    return {"message": "Welcome to the Sentilytics 360 API!"}


@app.get("/api/sentiment")
def sentiment(query: str):
    """
    Called by frontend using:
    GET http://localhost:8000/api/sentiment?query=tesla
    """
    if not query or not query.strip():
        raise HTTPException(status_code=400, detail="Query parameter cannot be empty.")

    try:
        logger.info(f"Processing sentiment analysis for query: {query}")
        df = run_sentiment_pipeline(query, 200)

        if df.empty:
            return {
                "keyword": query,
                "total_results": 0,
                "sentiment_breakdown": {},
                "data": [],
            }

        return {
            "keyword": query,
            "total_results": len(df),
            "sentiment_breakdown": (
                df["sentiment"].value_counts().to_dict()
                if "sentiment" in df.columns else {}
            ),
            "data": df.to_dict(orient="records"),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error processing sentiment for query: {query}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# ----------------------------------------------------------
# 2. OPTIONAL — Your existing POST endpoint (kept as-is)
# ----------------------------------------------------------
@app.post("/api/run_analysis/")
def run_analysis_endpoint(request: KeywordRequest):
    """Run sentiment analysis pipeline via POST request."""
    if not request.keyword or not request.keyword.strip():
        raise HTTPException(status_code=400, detail="Keyword cannot be empty.")

    try:
        logger.info(f"Running analysis for keyword: {request.keyword}, max_results: {request.max_results}")
        df = run_sentiment_pipeline(request.keyword, request.max_results)
        return {
            "status": "success",
            "message": f"Pipeline completed for '{request.keyword}'. {len(df)} results saved to DB."
        }
    except Exception as e:
        logger.exception(f"Analysis failed for keyword: {request.keyword}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


# ----------------------------------------------------------
# 3. OPTIONAL — Fetch all DB results (kept as-is)
# ----------------------------------------------------------
@app.get("/api/results/")
def get_all_results(db: Session = Depends(get_db)):
    results = db.query(models.SentimentResult).all()
    return results


# ----------------------------------------------------------
# 4. ADVANCED — Analyze endpoint with pagination and background tasks
# ----------------------------------------------------------
@app.get("/analyze")
async def analyze_keyword(
    keyword: str,
    max_results: int = Query(25, ge=1, le=200),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    background: bool = Query(False),
    background_tasks: BackgroundTasks = Depends(),
):
    """Run sentiment analysis pipeline for a keyword.

    - `background=true` → runs in background, returns 202
    - supports pagination with `page` and `page_size`
    """
    if not keyword:
        raise HTTPException(status_code=400, detail="Keyword cannot be empty.")

    if not credentials_available():
        logger.error("Missing upstream credentials.")
        raise HTTPException(status_code=503, detail="Upstream credentials not configured.")

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
            return {"data": [], "summary": {}}

        # Convert to JSON records
        data = results_df.to_dict("records")
        total = len(data)
        start = (page - 1) * page_size
        end = start + page_size
        paged = data[start:end]

        # Summaries
        sentiment_counts = results_df["sentiment"].value_counts().to_dict()
        platform_summary = (
            results_df.groupby("source")["sentiment"]
            .value_counts()
            .unstack(fill_value=0)
            .to_dict("index")
        )

        summary = {
            "total_posts": total,
            "sentiment_counts": sentiment_counts,
            "platform_summary": platform_summary,
            "page": page,
            "page_size": page_size,
        }

        return {"data": paged, "summary": summary}

    except HTTPException:
        raise
    except Exception:
        logger.exception("Error during analysis for keyword=%s", keyword)
        raise HTTPException(status_code=500, detail="Internal error during analysis.")
