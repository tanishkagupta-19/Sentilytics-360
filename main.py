# main.py
from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from src.processing.pipeline import run_sentiment_pipeline
import os

print("[ENV] Twitter token present:", bool(os.getenv("TWITTER_BEARER_TOKEN")))
print("[ENV] Reddit client ID present:", bool(os.getenv("REDDIT_CLIENT_ID")))
print("[ENV] Reddit secret present:", bool(os.getenv("REDDIT_CLIENT_SECRET")))

# Initialize the FastAPI app
app = FastAPI(
    title="Sentilytics 360 API",
    description="An API to analyze public sentiment from social media.",
    version="1.0.0"
)

# Configure CORS to allow your frontend to communicate with this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict this to your frontend's domain in production
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

@app.get("/analyze")
def analyze_keyword(keyword: str, max_results: int = 25):
    """
    Runs the sentiment analysis pipeline for a given keyword.
    """
    if not keyword:
        raise HTTPException(status_code=400, detail="Keyword cannot be empty.")
    
    try:
        results_df = run_sentiment_pipeline(keyword, max_results)
        
        if results_df.empty:
            return {"data": [], "summary": {}}

        # Convert DataFrame to a list of dictionaries for JSON
        data = results_df.to_dict('records')
        
        # Create a summary for easy visualization
        sentiment_counts = results_df['sentiment'].value_counts().to_dict()
        platform_summary = results_df.groupby('source')['sentiment'].value_counts().unstack(fill_value=0).to_dict('index')

        summary = {
            "total_posts": len(data),
            "sentiment_counts": sentiment_counts,
            "platform_summary": platform_summary
        }
        
        return {"data": data, "summary": summary}
    except Exception as e:
        #-- Private note: Log the full error for debugging
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="An internal error occurred during analysis.")