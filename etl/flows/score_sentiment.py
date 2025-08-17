from prefect import flow, task
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import pandas as pd
from sqlalchemy.orm import sessionmaker
import logging
from typing import List, Dict
import os

from etl.common.db import engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Configuration ---
# Use the model specified in the .env file, with a fallback
HF_MODEL = os.getenv("HF_MODEL", "distilbert-base-uncased-finetuned-sst-2-english")
BATCH_SIZE = 32 # Process 32 reviews at a time

@task
def get_reviews_to_score(limit=1000) -> pd.DataFrame:
    """Fetches reviews from the database that don't have a sentiment score yet."""
    logger.info(f"Fetching up to {limit} reviews to score.")
    query = "SELECT review_id, review_text FROM review WHERE sentiment_score IS NULL LIMIT %s"
    try:
        with engine.connect() as conn:
            df = pd.read_sql(query, conn, params=[limit])
        logger.info(f"Found {len(df)} reviews to score.")
        return df
    except Exception as e:
        logger.error(f"Failed to fetch reviews: {e}")
        return pd.DataFrame()

@task
def predict_sentiment(reviews_df: pd.DataFrame) -> pd.DataFrame:
    """
    Predicts sentiment for a DataFrame of reviews using a HuggingFace model.
    """
    if reviews_df.empty:
        logger.info("No reviews to predict sentiment for.")
        return pd.DataFrame()

    logger.info(f"Loading sentiment analysis model: {HF_MODEL}")
    # Using a pipeline is the easiest way to use HF models
    sentiment_pipeline = pipeline(
        "sentiment-analysis",
        model=HF_MODEL,
        # You can add device=0 to use a GPU if available
    )

    review_texts = reviews_df['review_text'].tolist()
    logger.info(f"Predicting sentiment for {len(review_texts)} reviews in batches of {BATCH_SIZE}...")

    # The pipeline can take a list of texts and will batch them automatically
    results = sentiment_pipeline(review_texts, batch_size=BATCH_SIZE)

    # Process results
    # The result is a list of dicts like {'label': 'POSITIVE', 'score': 0.999}
    reviews_df['sentiment_label'] = [r['label'] for r in results]
    # We'll convert the score to be -1 for NEGATIVE and +1 for POSITIVE
    reviews_df['sentiment_score'] = [
        r['score'] if r['label'] == 'POSITIVE' else -r['score']
        for r in results
    ]

    logger.info("Sentiment prediction complete.")
    return reviews_df[['review_id', 'sentiment_label', 'sentiment_score']]

@task
def update_sentiment_scores(scored_df: pd.DataFrame):
    """Updates the database with the new sentiment scores."""
    if scored_df.empty:
        logger.info("No scores to update in the database.")
        return

    logger.info(f"Updating {len(scored_df)} sentiment scores in the database.")

    Session = sessionmaker(bind=engine)
    with Session() as session:
        try:
            for record in scored_df.to_dict('records'):
                session.execute(
                    """
                    UPDATE review
                    SET sentiment_label = :sentiment_label, sentiment_score = :sentiment_score
                    WHERE review_id = :review_id
                    """,
                    record
                )
            session.commit()
            logger.info("Successfully updated sentiment scores.")
        except Exception as e:
            logger.error(f"Database error during sentiment score update: {e}")
            session.rollback()
            raise

@flow(name="Sentiment Scoring Flow")
def score_sentiment_flow():
    """
    The main flow to orchestrate sentiment analysis of product reviews.
    """
    reviews_to_score = get_reviews_to_score()
    if not reviews_to_score.empty:
        scored_reviews = predict_sentiment(reviews_to_score)
        update_sentiment_scores(scored_reviews)
    else:
        logger.info("No new reviews to score. Flow finished.")

if __name__ == "__main__":
    score_sentiment_flow()
