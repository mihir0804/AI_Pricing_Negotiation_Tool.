import argparse
import pandas as pd
import numpy as np
import os

from stable_baselines3 import PPO, A2C, SAC

from envs.pricing_env import PricingEnv, simple_demand_model
from train_rl import load_feature_data

# --- Available Algorithms ---
ALGOS = {"ppo": PPO, "a2c": A2C, "sac": SAC}

def evaluate_policy(args):
    """
    Loads a trained policy and evaluates its performance on a set of test products.
    """
    # --- Load Data and Environment ---
    # We use the same data loading logic, but in a real scenario, this would be a separate,
    # held-out test set that the model has not seen during training.
    df = load_feature_data()
    env = PricingEnv(product_features=df)

    # --- Load Trained Model ---
    try:
        model = ALGOS[args.algo].load(args.model_path, env=env)
        print(f"Successfully loaded model from {args.model_path}")
    except Exception as e:
        print(f"Error loading model: {e}")
        return

    # --- Evaluation Loop ---
    total_profit = 0
    total_revenue = 0
    num_episodes = len(df)

    results = []

    print(f"\n--- Running evaluation on {num_episodes} products ---")

    obs, _ = env.reset()
    for i in range(num_episodes):
        action, _states = model.predict(obs, deterministic=True)

        # Get the simulated outcome from the environment's logic
        # We can't use env.step() because that would advance the episode.
        # Instead, we call the simulation logic directly.
        product_idx = env.current_product_index
        product_info = df.iloc[product_idx]
        base_price = product_info['base_price']
        cost = product_info['cost']

        price = base_price * (1 + action[0])
        orders = simple_demand_model(price, base_price)
        revenue = price * orders
        profit = revenue - (cost * orders)

        results.append({
            "product_id": product_info['product_id'],
            "predicted_price": price,
            "predicted_orders": orders,
            "predicted_revenue": revenue,
            "predicted_profit": profit
        })

        total_profit += profit
        total_revenue += revenue

        # Move to the next product in the environment for the next iteration
        obs, _ = env.reset()

    # --- Report Results ---
    results_df = pd.DataFrame(results)
    avg_profit = total_profit / num_episodes
    avg_revenue = total_revenue / num_episodes

    print("\n--- Evaluation Results ---")
    print(f"Average Profit per Product: ${avg_profit:.2f}")
    print(f"Average Revenue per Product: ${avg_revenue:.2f}")
    print("\n--- Detailed Predictions ---")
    print(results_df)

    if args.save_results:
        results_df.to_csv(args.save_results, index=False)
        print(f"\nSaved detailed results to {args.save_results}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", type=str, required=True, help="Path to the trained model .zip file")
    parser.add_argument("--algo", type=str, required=True, choices=ALGOS.keys(), help="RL Algorithm used for the model")
    parser.add_argument("--save_results", type=str, default=None, help="Path to save the evaluation results CSV file")
    args = parser.parse_args()

    evaluate_policy(args)
