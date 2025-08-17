# 🤖 AI-Powered Pricing Negotiation Assistant

This project is an end-to-end solution for dynamic e-commerce pricing. It uses Reinforcement Learning (RL), sentiment analysis, and a GenAI-powered chatbot to help business managers explore and set optimal prices, moving beyond static ML models to account for real-time market dynamics.

## ✨ Features

*   **Dynamic Price Recommendations**: An RL agent (trained with Stable-Baselines3) recommends optimal prices to maximize profit.
*   **Interactive Negotiation Chatbot**: A LangChain-powered chatbot allows managers to get price recommendations in natural language (e.g., "What's the best price for the HyperDrone if I want a 20% margin?").
*   **"Glassy Purple" Modern Dashboard**: A multi-page Streamlit dashboard provides a "Next Level and Modern" UI for visualizing KPIs, running what-if scenarios, and tracking competitor prices.
*   **Automated Data Pipelines**: Prefect flows orchestrate the ingestion of competitor prices (via Playwright) and the analysis of customer review sentiment (via HuggingFace Transformers).
*   **Robust & Scalable Backend**: A FastAPI-powered API serves the model's predictions and data to the frontend, all containerized with Docker.
*   **Comprehensive Database Schema**: A well-designed PostgreSQL schema with materialized views for efficient feature retrieval.

## 🚀 Tech Stack

*   **Backend**: FastAPI, Python 3.11
*   **Frontend**: Streamlit
*   **Database**: PostgreSQL
*   **ML/RL**: Stable-Baselines3, Gymnasium, PyTorch, HuggingFace Transformers
*   **Chatbot**: LangChain, OpenAI
*   **Data Pipeline**: Prefect, Playwright
*   **Infrastructure**: Docker, Docker Compose

## 🏛️ Architecture

```
+-----------------+      +----------------------+      +------------------+
|   Dashboard     |----->|      FastAPI         |<---->|   PostgreSQL     |
|  (Streamlit)    |      | (Uvicorn/Gunicorn)   |      |      (DB)        |
+-----------------+      +----------------------+      +------------------+
        ^                         ^                            ^
        |                         |                            |
+-----------------+      +-----------------+      +----------------------+
|  User / Manager |----->|      Bot        |<---->|     ETL / Prefect    |
| (CLI / Web)     |      |  (LangChain)    |      | (Scraper, Sentiment) |
+-----------------+      +-----------------+      +----------------------+
                                  |
                                  v
                         +-----------------+
                         |   ML Training   |
                         | (SB3 / PyTorch) |
                         +-----------------+
```

## 📂 Repository Structure

```
ai-pricing-negotiation/
├── api/                  # FastAPI application
├── bot/                  # LangChain negotiation chatbot
├── dashboard/            # Streamlit dashboard application
├── data/                 # (Git-ignored) Local data storage
├── etl/                  # Prefect ETL flows (scraping, sentiment)
├── infra/                # Docker, .env, and database setup
├── ml/                   # RL environment, training, and evaluation scripts
├── models/               # (Git-ignored) Saved trained model artifacts
├── scripts/              # Helper scripts for bootstrapping data
└── README.md             # This file
```

## 🛠️ Local Setup & Run

Follow these steps to get the entire application running locally.

### 1. Prerequisites

*   Docker and Docker Compose installed.
*   Python 3.11+ and `pip` installed.
*   An OpenAI API key for the chatbot.

### 2. Configuration

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd ai-pricing-negotiation
    ```

2.  **Set up environment variables:**
    -   Copy the example `.env` file from the `infra` directory to the project root.
    ```bash
    cp infra/.env.example .env
    ```
    -   Edit the `.env` file and add your `OPENAI_API_KEY`. The other variables are pre-configured for the local Docker setup.

### 3. Launch Services

Bring up the entire stack (Postgres, FastAPI, Streamlit, Prefect) using Docker Compose.

```bash
docker-compose -f infra/docker-compose.yml up --build -d
```

*   **API** will be available at `http://localhost:8000`
*   **Dashboard** will be available at `http://localhost:8501`
*   **Prefect UI** will be available at `http://localhost:4200`
*   **Postgres DB** will be available at `localhost:5432`

### 4. Bootstrap Data

Run the helper scripts to populate the database with initial data.

```bash
# Install dependencies for scripts (uses etl requirements)
pip install -r etl/requirements.txt

# Run the scripts
python scripts/bootstrap_demo_data.py
python scripts/load_sales_mock.py
```

### 5. Run ETL Flows

Run the ETL flows manually to populate competitor prices and sentiment scores.

```bash
# Run the scraper (uses mock data, see script for details)
python etl/flows/scrape_competitors.py

# Run sentiment analysis (will be no-op until you add reviews)
python etl/flows/score_sentiment.py

# Refresh the feature view for the ML model
python etl/flows/materialize_features.py
```

### 6. Train an RL Model

Train a new pricing model using the training script.

```bash
# Install ML dependencies
pip install -r ml/requirements.txt

# Run training (this will take a few minutes)
python ml/train_rl.py --algo ppo --timesteps 20000
```
This will save a new model in the `models/` directory and register it in the database.

## 🚀 How to Use

*   **Dashboard**: Open `http://localhost:8501` in your browser. You can now explore the different pages to get price recommendations and view analytics.
*   **Chatbot**: Run the chatbot from your terminal for an interactive session.
    ```bash
    # Install bot dependencies
    pip install -r bot/requirements.txt

    # Run the bot
    python bot/negotiate.py
    ```
    **Example Questions:**
    *   "What is the best price for product 101?"
    *   "Can you get me a price for product 102 with a minimum margin of 25%?"

*   **API**: Explore the API documentation at `http://localhost:8000/docs`.

## 🔮 Future Improvements

*   **Real-time Scraping**: Implement real-time scraping with alerts for sudden price changes.
*   **Explainable AI (XAI)**: Integrate SHAP or similar libraries to explain *why* the RL model chose a specific price.
*   **A/B Testing Framework**: Build out the A/B testing module to compare the RL agent's policy against a baseline in a live environment.
*   **Advanced Demand Model**: Replace the simple demand model in the RL environment with a more sophisticated, trained model.
*   **Web Interface for Chatbot**: Integrate the chatbot into the Streamlit dashboard instead of running it in the CLI.
