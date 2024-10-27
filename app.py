import streamlit as st
from ui import build_ui

# Defining page settings
st.set_page_config(
    page_title="PortfolioPro",
    page_icon="💰",
    layout='wide',
    initial_sidebar_state='expanded'
)

# Set custom theme
st.markdown("""
    <style>
        :root {
            --primary-color: #7792E3;
            --background-color: #FFFFFF;
            --secondary-background-color: #F0F2F6;
            --text-color: #31333F;
            --font: sans-serif;
        }
    </style>
    """, unsafe_allow_html=True)

# Build the UI
build_ui()