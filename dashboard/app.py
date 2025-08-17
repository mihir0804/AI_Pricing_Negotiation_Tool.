import streamlit as st
import requests
import pandas as pd
from utils.styling import apply_custom_styling

# --- Page Configuration ---
st.set_page_config(
    page_title="AI Pricing Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Styling ---
apply_custom_styling()

# --- API Configuration ---
API_URL = "http://api:8000/api/v1"

# --- Main Page ---
st.title("Welcome to the AI Pricing Assistant 🤖")

st.markdown("""
This dashboard is your command center for dynamic pricing.
Use the navigation on the left to explore different modules:

- **🏠 Home**: You are here.
- **🔬 Pricing Lab**: Get price recommendations and run what-if scenarios.
- **📈 Performance**: Monitor your product KPIs and revenue trends.
- ** প্রতিযোগ Competitor Watch**: Keep an eye on competitor pricing movements.

Let's get started!
""")

st.header("Key Metrics Overview")

# --- Fetch Data ---
@st.cache_data(ttl=600) # Cache data for 10 minutes
def get_products():
    try:
        response = requests.get(f"{API_URL}/products")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch products from API: {e}")
        return []

products = get_products()

if products:
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Products Tracked", f"{len(products)}")
    # These would be calculated from a dedicated API endpoint in a real scenario
    col2.metric("Average Margin", "22.5%", "1.2%")
    col3.metric("Overall Sentiment", "Positive", "😊")
else:
    st.warning("Could not retrieve product data from the API.")


st.header("Product List")
if products:
    df = pd.DataFrame(products)
    st.dataframe(df, use_container_width=True)
else:
    st.info("No products found.")
