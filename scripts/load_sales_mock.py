import pandas as pd
import numpy as np
from datetime import date, timedelta
import sys
import os

# Add project root to path to allow importing from etl
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from etl.common.db import engine

def generate_mock_kpis(days=90):
    """
    Generates a DataFrame of mock KPI data for all products for the last N days.
    """
    print(f"--- Generating mock KPI data for the last {days} days ---")

    with engine.connect() as conn:
        products_df = pd.read_sql("SELECT product_id, base_price FROM products", conn)

    if products_df.empty:
        print("No products found in the database. Run bootstrap_demo_data.py first.")
        return pd.DataFrame()

    all_kpis = []
    today = date.today()

    for _, product in products_df.iterrows():
        product_id = product['product_id']
        base_price = float(product['base_price'])

        for i in range(days):
            kpi_date = today - timedelta(days=i)

            # Add weekly seasonality (higher sales on weekends)
            weekday_factor = 1.5 if kpi_date.weekday() >= 5 else 1.0

            # Generate mock data
            avg_price = base_price * (1 + np.random.uniform(-0.05, 0.05))
            orders = int(np.random.poisson(20 * weekday_factor) + 10)
            revenue = avg_price * orders
            conversion_rate = np.random.uniform(0.01, 0.05)

            all_kpis.append({
                'product_id': product_id,
                'kpi_date': kpi_date,
                'revenue': revenue,
                'orders': orders,
                'conversion_rate': conversion_rate,
                'average_price': avg_price
            })

    return pd.DataFrame(all_kpis)


def load_mock_kpis():
    """
    Loads mock KPI data into the product_daily_kpi table.
    This function is idempotent and will not insert data for dates that already exist.
    """
    kpis_df = generate_mock_kpis()

    if kpis_df.empty:
        print("No KPI data generated. Exiting.")
        return

    with engine.connect() as conn:
        # Check for existing data to ensure idempotency
        existing_kpis = pd.read_sql("SELECT product_id, kpi_date FROM product_daily_kpi", conn)
        existing_kpis['kpi_date'] = pd.to_datetime(existing_kpis['kpi_date']).dt.date

        if not existing_kpis.empty:
            merged_df = kpis_df.merge(
                existing_kpis,
                on=['product_id', 'kpi_date'],
                how='left',
                indicator=True
            )
            kpis_to_insert = merged_df[merged_df['_merge'] == 'left_only'].drop(columns=['_merge'])
        else:
            kpis_to_insert = kpis_df

    if kpis_to_insert.empty:
        print("KPI data already seems to be up to date. No new data inserted.")
        return

    print(f"Inserting {len(kpis_to_insert)} new KPI records...")
    try:
        with engine.begin() as conn:
            kpis_to_insert.to_sql('product_daily_kpi', conn, if_exists='append', index=False)
        print("Successfully inserted mock KPI data.")
    except Exception as e:
        print(f"An error occurred while inserting KPI data: {e}")


if __name__ == "__main__":
    load_mock_kpis()
