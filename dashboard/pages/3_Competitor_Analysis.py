import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# --- API Configuration ---
API_URL = "http://api:8000/api/v1"

st.set_page_config(layout="wide")

st.title(" প্রতিযোগ Competitor Watch")
st.markdown("Keep an eye on how your competitors are pricing your products.")

# --- Helper function to get products ---
@st.cache_data(ttl=300)
def get_products():
    try:
        response = requests.get(f"{API_URL}/products")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return []

products = get_products()

if not products:
    st.error("Could not connect to the API to fetch products. Please ensure the API service is running.")
    st.stop()

product_map = {p['name']: p['product_id'] for p in products}
selected_product_name = st.selectbox("Select a Product to Analyze", options=product_map.keys())
selected_product_id = product_map[selected_product_name]

# --- Fetch Competitor Price Data ---
@st.cache_data(ttl=60)
def get_competitor_price_data(product_id):
    try:
        response = requests.get(f"{API_URL}/products/{product_id}/competitor_prices")
        response.raise_for_status()
        data = response.json()
        if not data:
            return pd.DataFrame()
        df = pd.DataFrame(data)
        df['observed_at'] = pd.to_datetime(df['observed_at'])
        # The price comes in as string from the Numeric type in DB
        df['price'] = pd.to_numeric(df['price'])
        return df.sort_values('observed_at')
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch competitor price data: {e}")
        return pd.DataFrame()

price_df = get_competitor_price_data(selected_product_id)

st.divider()

if price_df.empty:
    st.warning("No competitor pricing data found for the selected product.")
else:
    st.header(f"Price History for {selected_product_name}")

    # --- Chart ---
    fig = px.line(
        price_df,
        x='observed_at',
        y='price',
        color='competitor_name',
        title='Competitor Prices Over Time',
        markers=True
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="white",
        xaxis_title="Date",
        yaxis_title="Price ($)"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.header("Raw Price Data")
    st.dataframe(price_df, use_container_width=True)
