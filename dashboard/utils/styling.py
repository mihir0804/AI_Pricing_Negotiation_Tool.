import streamlit as st

def apply_custom_styling():
    st.markdown("""
    <style>
    /* --- Base Theme --- */
    body {
        color: #fff;
        background-color: #1a1a2e;
    }
    .stApp {
        background: linear-gradient(270deg, #1a1a2e, #16213e, #0f3460);
        background-size: 600% 600%;
        animation: gradientAnimation 16s ease infinite;
    }

    @keyframes gradientAnimation {
        0%{background-position:0% 50%}
        50%{background-position:100% 50%}
        100%{background-position:0% 50%}
    }

    /* --- Sidebar --- */
    .css-1d391kg {
        background-color: rgba(255, 255, 255, 0.05);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
    }
    .css-1d391kg .css-1v3fvcr {
        color: #e94560; /* Accent color for sidebar title */
    }

    /* --- Main Content --- */
    .st-emotion-cache-16txtl3 {
      padding: 2rem;
    }

    h1, h2, h3 {
        color: #e94560;
    }

    /* --- Widgets --- */
    .stButton>button {
        background-color: #e94560;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 20px;
    }
    .stButton>button:hover {
        background-color: #ff6e7f;
    }
    .stSelectbox, .stTextInput, .stNumberInput {
        border-radius: 8px;
    }

    /* --- Glassmorphism Cards for Metrics --- */
    .st-emotion-cache-1r6slb0 { /* Metric container */
        background: rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(5px);
    }

    /* --- Dataframes --- */
    .stDataFrame {
        background-color: transparent;
    }

    </style>
    """, unsafe_allow_html=True)
