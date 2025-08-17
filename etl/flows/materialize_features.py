from prefect import flow, task
from sqlalchemy.exc import SQLAlchemyError
import logging

from etl.common.db import engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@task(name="Refresh Materialized View")
def refresh_materialized_view():
    """
    Executes the SQL command to refresh the fv_product_context materialized view.
    """
    logger.info("Refreshing the fv_product_context materialized view...")

    # The CONCURRENTLY option allows the view to be refreshed without locking it,
    # but it requires the view to have a UNIQUE index. I will add that to the schema.
    refresh_query = "REFRESH MATERIALIZED VIEW CONCURRENTLY fv_product_context;"

    try:
        with engine.begin() as conn:
            conn.execute(refresh_query)
        logger.info("Successfully refreshed the materialized view.")
    except SQLAlchemyError as e:
        # If CONCURRENTLY fails, it might be because it's the first run.
        # We can fall back to a normal refresh.
        if "CONCURRENTLY" in str(e):
            logger.warning("CONCURRENTLY refresh failed. Trying a standard refresh. This will lock the view.")
            try:
                with engine.begin() as conn:
                    conn.execute("REFRESH MATERIALIZED VIEW fv_product_context;")
                logger.info("Successfully refreshed the materialized view with standard method.")
            except SQLAlchemyError as inner_e:
                logger.error(f"Standard refresh also failed: {inner_e}")
                raise
        else:
            logger.error(f"Database error during materialized view refresh: {e}")
            raise


@flow(name="Feature Materialization Flow")
def materialize_features_flow():
    """
    The main flow to orchestrate the feature materialization process.
    """
    refresh_materialized_view()


if __name__ == "__main__":
    materialize_features_flow()
