import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# --- API Configuration ---
API_URL = "http://api:8000/api/v1"

st.set_page_config(layout="wide")

st.title("📈 Performance Metrics")
st.markdown("Monitor key performance indicators for your products over time.")

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

# --- Fetch KPI Data ---
@st.cache_data(ttl=60)
def get_kpi_data(product_id):
    try:
        response = requests.get(f"{API_URL}/products/{product_id}/kpis")
        response.raise_for_status()
        data = response.json()
        if not data:
            return pd.DataFrame()
        df = pd.DataFrame(data)
        df['kpi_date'] = pd.to_datetime(df['kpi_date'])
        return df.sort_values('kpi_date')
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch KPI data: {e}")
        return pd.DataFrame()

kpi_df = get_kpi_data(selected_product_id)

st.divider()

if kpi_df.empty:
    st.warning("No KPI data found for the selected product.")
else:
    st.header(f"Performance for {selected_product_name}")

    # --- Charts ---
    fig_revenue = px.line(kpi_df, x='kpi_date', y='revenue', title='Revenue Over Time', markers=True)
    fig_revenue.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white")
    st.plotly_chart(fig_revenue, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        fig_orders = px.line(kpi_df, x='kpi_date', y='orders', title='Daily Orders', markers=True)
        fig_orders.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white")
        st.plotly_chart(fig_orders, use_container_width=True)
    with col2:
        fig_conversion = px.line(kpi_df, x='kpi_date', y='conversion_rate', title='Conversion Rate (%)', markers=True)
        fig_conversion.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white")
        st.plotly_chart(fig_conversion, use_container_width=True)

    st.dataframe(kpi_df, use_container_width=True)
