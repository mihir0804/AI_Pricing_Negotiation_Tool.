from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

# Load .env file from the project root.
# This assumes the scripts are run from the root of the project,
# or that the .env file is in a discoverable path.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
dotenv_path = os.path.join(project_root, '.env')

if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path=dotenv_path)
else:
    # Fallback for when running in a different context (like Docker)
    # where env vars are passed directly.
    pass

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set. Ensure you have a .env file in the project root or the variable is set in your environment.")

# The `future=True` flag enables 2.0 style usage now
engine = create_engine(DATABASE_URL, future=True)
