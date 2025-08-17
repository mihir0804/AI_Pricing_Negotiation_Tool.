# AI_Pricing_Negotiation_Tool.
E-commerce businesses face challenges with dynamic pricing as current ML models rely on static factors like demand, seasonality, and competitor prices. They often miss real-time competitor behavior, customer sentiment, and alignment with business goals (profit vs. growth), leading to suboptimal pricing and lost opportunities.

Now that the branch rules are set up, here is how you can run and see the application, as detailed in the README.md file:

## Step 1: Launch All Services with Docker Compose

- Open your terminal in the project's root directory and run this command. This will build the Docker images and start all the services (database, API, dashboard, etc.) in the background.

**docker-compose -f infra/docker-compose.yml up --build -d**

# Step 2: Populate the Database with Demo Data

To have data to visualize, you need to run the bootstrapping scripts. You'll need to install the dependencies first if you haven't already.

## Install dependencies
- **pip install -r etl/requirements.txt**

## Run the scripts
- **python scripts/bootstrap_demo_data.py**
- **python scripts/load_sales_mock.py**

# Step 3: View the Dashboard!

Once the services are running, you can access the main application—the Streamlit dashboard—in your web browser at this URL:

http://localhost:8501

You should see the "Glassy Purple" interface and be able to interact with the "Pricing Lab" and other pages.

For reference, the other services are also available:

**API Docs: http://localhost:8000/docs
Prefect UI: http://localhost:4200**
