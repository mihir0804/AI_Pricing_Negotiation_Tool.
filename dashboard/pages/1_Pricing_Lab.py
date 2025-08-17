import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

# --- API Configuration ---
API_URL = "http://api:8000/api/v1"

st.set_page_config(layout="wide")

st.title("🔬 Pricing Lab")
st.markdown("Get AI-powered price recommendations and explore what-if scenarios.")

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
selected_product_name = st.selectbox("Select a Product", options=product_map.keys())
selected_product_id = product_map[selected_product_name]

st.divider()

col1, col2 = st.columns(2, gap="large")

# --- Recommendation Column ---
with col1:
    st.header("Price Recommendation")
    if st.button("Get Recommendation", use_container_width=True):
        with st.spinner("Calling the AI pricing model..."):
            try:
                payload = {"product_id": selected_product_id, "constraints": {}}
                response = requests.post(f"{API_URL}/recommend_price", json=payload)
                response.raise_for_status()
                recommendation = response.json()

                st.subheader("Recommended Price:")
                st.success(f"## ${recommendation['recommended_price']:.2f}")
                st.caption(f"Based on policy ID: {recommendation['policy_id']} with confidence {recommendation.get('confidence_score', 'N/A')}")
            except requests.exceptions.RequestException as e:
                st.error(f"API Error: {e.response.json().get('detail') if e.response else str(e)}")

# --- What-If Analysis Column ---
with col2:
    st.header("What-If Scenario")
    what_if_price = st.number_input("Enter a hypothetical price:", min_value=0.01, step=10.0, value=199.99)

    if st.button("Analyze Scenario", use_container_width=True):
        with st.spinner("Running prediction..."):
            try:
                payload = {"product_id": selected_product_id, "price": what_if_price}
                response = requests.post(f"{API_URL}/what_if", json=payload)
                response.raise_for_status()
                scenario = response.json()
                prediction = scenario['prediction']

                st.subheader("Predicted Outcomes:")

                fig = go.Figure()
                fig.add_trace(go.Indicator(
                    mode = "number+delta",
                    value = prediction['orders'],
                    title = {"text": "Predicted Orders"},
                    # delta = {'reference': 80, 'relative': True, 'valueformat':'.0%'}
                ))
                fig.add_trace(go.Indicator(
                    mode = "number+delta",
                    value = prediction['revenue'],
                    title = {"text": "Predicted Revenue"},
                ))
                fig.add_trace(go.Indicator(
                    mode = "number",
                    value = prediction['profit_margin'] * 100,
                    title = {"text": "Profit Margin (%)"},
                ))

                fig.update_layout(
                    grid = {'rows': 1, 'columns': 3, 'pattern': "independent"},
                    template = {'data' : {'indicator': [{
                        'title': {'font': {'size': 16}},
                        'number': {'font': {'size': 36}},
                    }]}},
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font_color="white"
                )
                st.plotly_chart(fig, use_container_width=True)

            except requests.exceptions.RequestException as e:
                st.error(f"API Error: {e.response.json().get('detail') if e.response else str(e)}")
