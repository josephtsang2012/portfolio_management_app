import streamlit as st
from datetime import date
from functions import perform_portfolio_analysis, portfolio_vs_benchmark, portfolio_returns
from streamlit_js_eval import streamlit_js_eval
## Ref: https://docs.streamlit.io/develop/api-reference/widgets/st.color_picker
## Ref: https://streamlit-emoji-shortcodes-streamlit-app-gwckff.streamlit.app/

def build_ui():
    # Custom CSS
    st.markdown("""
    <style>
    .big-font {
        font-size:60px !important;
        font-weight: bold;
        color: #191A19;
    }
                
    .sidebar-header {
        font-size:18px;
        color: #191A19;
    }
                
    .description {
        font-size:18px;
        color: #191A19;
    }
                                
    .subheader {
        font-size: 25px;
        color: #191A19;
    }
    .stButton>button {
        color: #4F4F4F;
        background-color: #E0E0E0;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        # Ticker and Value Input
        st.subheader(":chart: Portfolio Composition")
        if 'num_pairs' not in st.session_state:
            st.session_state['num_pairs'] = 1

        def add_input_pair():
            st.session_state['num_pairs'] += 1

        tickers_and_values = {}
        for n in range(st.session_state['num_pairs']):
            col1, col2 = st.columns(2)
            with col1:
                ticker = st.text_input(f"Ticker {n+1}", key=f"ticker_{n+1}", placeholder="e.g., AAPL")
            with col2:
                value = st.number_input(f"Amount ($)", min_value=0.0, format="%.2f", key=f"value_{n+1}")
            if ticker and value > 0:
                tickers_and_values[ticker] = value

        st.button("➕ Add Ticker", on_click=add_input_pair)

        # Benchmark Input
        st.markdown("---")
        st.subheader(":vs: Benchmark")
        benchmark = st.text_input("Ticker symbol", placeholder="e.g., VOO")

        # Date Input
        st.markdown("---")
        st.subheader(":calendar: Period")
        st.markdown("Default Jan-1980 as earliest, and today as latest. Beware of positive date range.")
        start_date = st.date_input("Start Date", value=date.today().replace(year=date.today().year - 1), min_value=date(1980, 1, 1), max_value=date.today())
        end_date = st.date_input("End Date", value=date.today(), min_value=date(1980, 1, 1), max_value=date.today())

        # Run Analysis Button
        st.markdown("---")
        run_analysis = st.button("See Result")

        # Reset Button
        if st.button("Reset Values"): #Javascript to refresh the page if true/ pressed
            streamlit_js_eval(js_expressions="parent.window.location.reload()")
    
    # Main content
    st.markdown('<p class="big-font">Easy Portfolio Manager</p>', unsafe_allow_html=True)
    st.markdown('<p class="description">Build your own investment portfolio with a simple few clicks!</p>', unsafe_allow_html=True)

    # Run Analysis
    if run_analysis:
        if not tickers_and_values:
            st.error("Please input at least one ticker with a non-zero amount before running result.")
        elif not benchmark:
            st.error("Please enter a benchmark ticker before running result.")
        elif end_date - start_date <30:
            st.error("Please set end date at least 30 days beyond start date before running result.")
        else:
            start_date_str = start_date.strftime('%Y-%m-%d')
            end_date_str = end_date.strftime('%Y-%m-%d')

            with st.spinner('Analyzing your portfolio...'):
                status, result = portfolio_returns(tickers_and_values, start_date_str, end_date_str, benchmark)

            if status == "error":
                st.error(result)
            else:
                fig, fig1, fig2 = result

                if fig is not None:
                    st.plotly_chart(fig, use_container_width=True)
                if fig1 is not None:
                    st.plotly_chart(fig1, use_container_width=True)
                if fig2 is not None:
                    st.plotly_chart(fig2, use_container_width=True)

                # Extract data for AI analysis
                portfolio_data = {
                    'return': fig2.data[0].y[-1],
                    'volatility': fig2.data[2].x[0],
                    'sharpe': fig2.data[2].marker.color[0]
                }
                benchmark_data = {
                    'return': fig2.data[1].y[-1],
                    'volatility': fig2.data[2].x[1],
                    'sharpe': fig2.data[2].marker.color[1]
                }

    # Footnote
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #8d8d8d; font-size: 14px;">
        Demo Created and Updated in Oct 2024<br>
    </div>
    """, unsafe_allow_html=True)
