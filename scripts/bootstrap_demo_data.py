import pandas as pd
from sqlalchemy.exc import IntegrityError
import sys
import os

# Add project root to path to allow importing from etl
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from etl.common.db import engine

def bootstrap_data():
    """
    Inserts initial seed data for products and competitors into the database.
    This function is idempotent and will not insert duplicate data.
    """
    print("--- Starting data bootstrapping ---")

    # --- Sample Data ---
    products_data = [
        {'product_id': 101, 'sku': 'HD-01', 'name': 'HyperDrone X1', 'description': 'A high-speed racing drone.', 'category': 'Drones', 'base_price': 249.99, 'cost': 150.00},
        {'product_id': 102, 'sku': 'CAM-4K', 'name': 'ActionCam 4K', 'description': 'A rugged 4K action camera.', 'category': 'Cameras', 'base_price': 199.99, 'cost': 120.00},
        {'product_id': 103, 'sku': 'VR-2025', 'name': 'VirtuReal Headset', 'description': 'An immersive VR headset.', 'category': 'VR', 'base_price': 399.99, 'cost': 250.00},
    ]

    competitors_data = [
        {'competitor_id': 1, 'name': 'CompetitorA', 'website_url': 'https://www.competitorA.com'},
        {'competitor_id': 2, 'name': 'CompetitorB', 'website_url': 'https://www.competitorB.com'},
        {'competitor_id': 3, 'name': 'CompetitorC', 'website_url': 'https://www.competitorC.com'},
    ]

    products_df = pd.DataFrame(products_data)
    competitors_df = pd.DataFrame(competitors_data)

    with engine.connect() as conn:
        # --- Insert Products ---
        print("Inserting products...")
        try:
            products_df.to_sql('products', conn, if_exists='append', index=False)
            print(f"Successfully inserted {len(products_df)} product records.")
        except IntegrityError:
            print("Products already exist, skipping insertion.")
        except Exception as e:
            print(f"An error occurred while inserting products: {e}")

        # --- Insert Competitors ---
        print("Inserting competitors...")
        try:
            competitors_df.to_sql('competitors', conn, if_exists='append', index=False)
            print(f"Successfully inserted {len(competitors_df)} competitor records.")
        except IntegrityError:
            print("Competitors already exist, skipping insertion.")
        except Exception as e:
            print(f"An error occurred while inserting competitors: {e}")

    print("--- Data bootstrapping complete ---")


if __name__ == "__main__":
    bootstrap_data()
