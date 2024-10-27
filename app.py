import streamlit as st
from ui copy import build_ui

# Defining page settings
## Ref: https://docs.streamlit.io/develop/api-reference/configuration/st.set_page_config
st.set_page_config(
    page_title="Portfolio Manager",
    page_icon=":heavy_dollar_sign:", 
    layout='wide',
    initial_sidebar_state='auto'
)

# Setting theme
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

# Building user interface
build_ui()
