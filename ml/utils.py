from stable_baselines3 import PPO, A2C, SAC
import os

ALGOS = {"ppo": PPO, "a2c": A2C, "sac": SAC}

def load_model(model_path: str, algo: str, env=None):
    """
    Loads a trained Stable-Baselines3 model.

    :param model_path: Path to the saved model .zip file.
    :param algo: The algorithm the model was trained with (e.g., 'ppo').
    :param env: The environment to load the model with.
    :return: A loaded SB3 model.
    """
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found at {model_path}")

    if algo not in ALGOS:
        raise ValueError(f"Unknown algorithm: {algo}. Must be one of {list(ALGOS.keys())}")

    try:
        model = ALGOS[algo].load(model_path, env=env)
        print(f"Successfully loaded model from {model_path}")
        return model
    except Exception as e:
        print(f"Error loading model: {e}")
        raise
