import argparse
import pandas as pd
import os
import uuid
import json
from datetime import datetime

from stable_baselines3 import PPO, A2C, SAC
from stable_baselines3.common.env_checker import check_env
from stable_baselines3.common.callbacks import EvalCallback
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

from envs.pricing_env import PricingEnv

# --- Available Algorithms ---
ALGOS = {"ppo": PPO, "a2c": A2C, "sac": SAC}

def load_feature_data() -> pd.DataFrame:
    """Loads feature data from the fv_product_context materialized view."""
    # In a real scenario, you'd connect to the production DB.
    # For now, we'll create some mock data that matches the schema.
    print("Loading feature data...")

    # --- Mock Data Generation ---
    # This simulates the data that would be in the fv_product_context view.
    # In a live run, you would replace this with a DB query.
    # load_dotenv()
    # DATABASE_URL = os.getenv("DATABASE_URL")
    # engine = create_engine(DATABASE_URL)
    # with engine.connect() as conn:
    #     df = pd.read_sql("SELECT * FROM fv_product_context;", conn)

    data = {
        'product_id': range(10),
        'base_price': [100, 150, 200, 50, 300, 250, 80, 120, 180, 220],
        'cost': [50, 70, 100, 20, 150, 120, 40, 60, 90, 110],
        'avg_competitor_price_7d': [98, 155, 205, 48, 295, 255, 82, 118, 185, 215],
        'avg_sentiment_30d': [0.8, 0.9, 0.7, 0.95, 0.6, 0.85, 0.75, 0.92, 0.88, 0.81],
        'avg_orders_14d': [110, 80, 60, 200, 40, 50, 150, 100, 70, 55]
    }
    df = pd.DataFrame(data)
    print(f"Loaded {len(df)} products.")
    return df


def register_policy_in_db(policy_name: str, algo: str, hyperparameters: dict, storage_path: str):
    """Adds a new record to the rl_policies table."""
    print(f"Registering policy '{policy_name}' in the database.")
    load_dotenv()
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        print("DATABASE_URL not found, skipping policy registration.")
        return

    engine = create_engine(DATABASE_URL)

    insert_query = text("""
        INSERT INTO rl_policies (policy_name, algorithm, hyperparameters, storage_path, is_active, created_at)
        VALUES (:policy_name, :algorithm, :hyperparameters, :storage_path, :is_active, :created_at)
    """)

    with engine.begin() as conn:
        conn.execute(insert_query, {
            "policy_name": policy_name,
            "algorithm": algo,
            "hyperparameters": json.dumps(hyperparameters),
            "storage_path": storage_path,
            "is_active": False, # New policies are not active by default
            "created_at": datetime.utcnow()
        })
    print("Policy registered successfully.")


def train(args):
    """The main training pipeline."""
    df = load_feature_data()

    # --- Environment Setup ---
    env = PricingEnv(product_features=df)
    # It's a good practice to check your custom environment
    check_env(env)

    # --- Model Training ---
    # You can define custom network architectures here if needed
    policy_kwargs = dict(net_arch=dict(pi=[64, 64], vf=[64, 64]))

    model = ALGOS[args.algo](
        "MlpPolicy",
        env,
        policy_kwargs=policy_kwargs,
        tensorboard_log=f"logs/{args.algo}",
        verbose=1,
        learning_rate=args.lr,
        n_steps=args.n_steps,
        batch_size=args.batch_size,
        gamma=0.99
    )

    # Create a unique name for this training run
    run_name = f"{args.algo}_{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    print(f"--- Starting training for run: {run_name} ---")
    model.learn(total_timesteps=args.timesteps, tb_log_name=run_name)
    print("--- Training complete ---")

    # --- Save and Register Model ---
    os.makedirs(args.save_path, exist_ok=True)
    model_path = os.path.join(args.save_path, f"{run_name}.zip")
    model.save(model_path)
    print(f"Model saved to {model_path}")

    hyperparams = {
        "learning_rate": args.lr,
        "n_steps": args.n_steps,
        "batch_size": args.batch_size
    }
    register_policy_in_db(run_name, args.algo, hyperparams, model_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--algo", type=str, default="ppo", choices=ALGOS.keys(), help="RL Algorithm")
    parser.add_argument("--timesteps", type=int, default=20000, help="Total training timesteps")
    parser.add_argument("--lr", type=float, default=3e-4, help="Learning rate")
    parser.add_argument("--n_steps", type=int, default=2048, help="Number of steps to run for each environment per update")
    parser.add_argument("--batch_size", type=int, default=64, help="Minibatch size")
    parser.add_argument("--save_path", type=str, default="models/", help="Path to save trained models")
    args = parser.parse_args()

    train(args)
