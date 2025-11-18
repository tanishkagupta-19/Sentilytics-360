# main.py
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import logging
import asyncio
import os
from src.pipeline import run_sentiment_pipeline


# ---------------------------------------------------------
# Logging setup
# ---------------------------------------------------------
logger = logging.getLogger("sentilytics")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)

logger.info("[ENV] Twitter token present: %s", bool(os.getenv("TWITTER_BEARER_TOKEN")))
logger.info("[ENV] Reddit client ID present: %s", bool(os.getenv("REDDIT_CLIENT_ID")))
logger.info("[ENV] Reddit secret present: %s", bool(os.getenv("REDDIT_CLIENT_SECRET")))


# ---------------------------------------------------------
# FastAPI app configuration
# ---------------------------------------------------------
app = FastAPI(
    title="Sentilytics 360 API",
    description="API for real-time sentiment analysis across social platforms.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict in production
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


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
        # TODO: Save df to database or storage if needed
    except Exception:
        logger.exception("Background job failed for keyword=%s", keyword)


# ---------------------------------------------------------
# Routes
# ---------------------------------------------------------
@app.get("/")
def root():
    return {"message": "Welcome to the Sentilytics 360 API!"}


@app.get("/analyze")
async def analyze_keyword(
    keyword: str,
    max_results: int = Query(25, ge=1, le=200),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    background: bool = Query(False),
    background_tasks: BackgroundTasks = None,
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
            if not background_tasks:
                raise HTTPException(status_code=400, detail="background_tasks must be provided when background=true")
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
