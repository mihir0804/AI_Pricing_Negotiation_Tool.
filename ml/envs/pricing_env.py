import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pandas as pd
from typing import Optional

# This is a simplified demand model. In a real-world scenario, this could be
# a more complex, trained model (e.g., a regression model).
def simple_demand_model(price: float, base_price: float, elasticity: float = -1.5) -> int:
    """
    Calculates the expected number of orders based on price.
    A simple log-log demand model: log(Q) = a + b*log(P)
    """
    if price <= 0:
        return 0
    # Assuming base demand is 100 units at base_price
    base_demand = 100
    price_ratio = price / base_price
    demand = base_demand * (price_ratio ** elasticity)
    # Add some stochasticity
    demand = np.random.poisson(max(0, demand))
    return int(demand)


class PricingEnv(gym.Env):
    """
    A custom Gymnasium environment for dynamic pricing.

    Observation:
        A dictionary containing the product's context, e.g., competitor prices,
        sentiment, etc.

    Action:
        A continuous value representing the percentage change from the base price.
        E.g., an action of 0.1 means setting the price to base_price * 1.1.

    Reward:
        The profit generated in one step.
    """
    metadata = {'render_modes': ['human']}

    def __init__(self, product_features: pd.DataFrame, render_mode: Optional[str] = None):
        super().__init__()
        self.render_mode = render_mode

        # This dataframe holds the features for all products for one time step (e.g., a day)
        # In a real use case, this would be refreshed with new data for each episode.
        self.product_features = product_features
        self.current_product_index = 0

        # --- Define action and observation spaces ---
        # Action: A continuous value for price change percentage, e.g., from -30% to +30%
        self.action_space = spaces.Box(low=-0.3, high=0.3, shape=(1,), dtype=np.float32)

        # Observation: Features like competitor price, sentiment, etc.
        # We normalize these features to be in a similar range, typically [0, 1] or [-1, 1]
        self.observation_space = spaces.Dict({
            "avg_competitor_price_7d": spaces.Box(low=0, high=np.inf, shape=(1,)),
            "avg_sentiment_30d": spaces.Box(low=-1, high=1, shape=(1,)),
            "avg_orders_14d": spaces.Box(low=0, high=np.inf, shape=(1,)),
            "current_price_ratio": spaces.Box(low=0, high=np.inf, shape=(1,)), # price / base_price
        })

        self.current_state = None
        self.current_price = None

    def _get_obs(self) -> dict:
        """Constructs the observation dictionary from the current product's features."""
        features = self.product_features.iloc[self.current_product_index]
        return {
            "avg_competitor_price_7d": np.array([features['avg_competitor_price_7d']], dtype=np.float32),
            "avg_sentiment_30d": np.array([features['avg_sentiment_30d']], dtype=np.float32),
            "avg_orders_14d": np.array([features['avg_orders_14d']], dtype=np.float32),
            "current_price_ratio": np.array([self.current_price / features['base_price']], dtype=np.float32),
        }

    def reset(self, seed: Optional[int] = None, options: Optional[dict] = None):
        super().reset(seed=seed)

        # Move to the next product for a new episode
        self.current_product_index = (self.current_product_index + 1) % len(self.product_features)

        # Initialize price to the base price
        self.current_price = self.product_features.iloc[self.current_product_index]['base_price']

        self.current_state = self._get_obs()
        return self.current_state, {}

    def step(self, action: np.ndarray):
        # The action is the percentage change
        price_change_pct = action[0]

        # Calculate the new price
        base_price = self.product_features.iloc[self.current_product_index]['base_price']
        self.current_price = base_price * (1 + price_change_pct)

        # Simulate market response using the demand model
        cost = self.product_features.iloc[self.current_product_index]['cost']
        orders = simple_demand_model(self.current_price, base_price)

        # Calculate reward (profit)
        revenue = self.current_price * orders
        total_cost = cost * orders
        profit = revenue - total_cost
        reward = float(profit)

        # The episode ends after one step for this simple environment
        terminated = True
        truncated = False # No truncation in this simple case

        # Get the next state (which is the same in this one-step episode)
        self.current_state = self._get_obs()

        info = {
            "price": self.current_price,
            "orders": orders,
            "revenue": revenue,
            "profit": profit
        }

        if self.render_mode == "human":
            self._render_human(info)

        return self.current_state, reward, terminated, truncated, info

    def _render_human(self, info: dict):
        """Simple text-based rendering."""
        print("--- Pricing Step ---")
        print(f"Product Index: {self.current_product_index}")
        for key, value in info.items():
            print(f"{key.capitalize()}: {value:.2f}")
        print("--------------------")

    def close(self):
        pass
