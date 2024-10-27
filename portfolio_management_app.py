# Installing yfinance for retrieving data
pip install yfinance --quiet

# Importing necessary libraries
import streamlit as st
from datetime import date
import yfinance as yf
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import plotly.subplots as sp
from plotly.subplots import make_subplots
import plotly.figure_factory as ff
import plotly.io as pio
from IPython.display import display
from plotly.offline import init_notebook_mode
init_notebook_mode(connected=True)

# Hiding Warnings
import warnings
warnings.filterwarnings('ignore')

def perform_portfolio_analysis(df, tickers_weights):
    """
    This function takes historical stock data and the weights of the securities in the portfolio,
    It calculates individual security returns, cumulative returns, volatility, and Sharpe Ratios.
    It then visualizes this data, showing historical performance and a risk-reward plot.

    Parameters:
    - df (pd.DataFrame): DataFrame containing historical stock data with securities as columns.
    - tickers_weights (dict): A dictionary where keys are ticker symbols (str) and values are their 
        respective weights (float)in the portfolio.

    Returns:
    - fig1: A Plotly Figure with two subplots:
      1. Line plot showing the historical returns of each security in the portfolio.
      2. Plot showing the annualized volatility and last cumulative return of each security 
        colored by their respective Sharpe Ratio.

    Notes:
    - The function assumes that 'pandas', 'numpy', and 'plotly.graph_objects' are imported as 'pd', 'np', and 'go' respectively.
    - The function also utilizes 'plotly.subplots.make_subplots' for creating subplots.
    - The risk-free rate is assumed to be 1% per annum for Sharpe Ratio calculation.
    """

    # Starting DataFrame and Series 
    individual_cumsum = pd.DataFrame()
    individual_vol = pd.Series(dtype=float)
    individual_sharpe = pd.Series(dtype=float)


    # Iterating through tickers and weights in the tickers_weights dictionary
    for ticker, weight in tickers_weights.items():
        if ticker in df.columns: # Confirming that the tickers are available
            individual_returns = df[ticker].pct_change() # Computing individual daily returns for each ticker
            individual_cumsum[ticker] = ((1 + individual_returns).cumprod() - 1) * 100 # Computing cumulative returns over the period for each ticker 
            vol = (individual_returns.std() * np.sqrt(252)) * 100 # Computing annualized volatility
            individual_vol[ticker] = vol # Adding annualized volatility for each ticker
            individual_excess_returns = individual_returns - 0.01 / 252 # Computing the excess returns
            sharpe = (individual_excess_returns.mean() / individual_returns.std() * np.sqrt(252)).round(2) # Computing Sharpe Ratio
            individual_sharpe[ticker] = sharpe # Adding Sharpe Ratio for each ticker

            # Creating subplots for comparison across securities
            fig1 = make_subplots(rows = 1, cols = 2, horizontal_spacing=0.25,
                            column_titles=['Historical Performance Assets', 'Risk-Reward'],
                            column_widths=[.55, .45],
                            shared_xaxes=False, shared_yaxes=False)
        
    # Adding the historical returns for each ticker on the first subplot    
    for ticker in individual_cumsum.columns:
        fig1.add_trace(go.Scatter(x=individual_cumsum.index,
                                  y=individual_cumsum[ticker],
                                  mode = 'lines',
                                  name = ticker,
                                  hovertemplate = '%{y:.2f}%',
                                  showlegend=True),
                            row=1, col=1)

    # Defining colors for markers on the second subplot
    sharpe_colors = [individual_sharpe[ticker] for ticker in individual_cumsum.columns]

    # Adding markers for each ticker on the second subplot
    fig1.add_trace(go.Scatter(x=individual_vol.tolist(),
                              y=individual_cumsum.iloc[-1].tolist(),
                              mode='markers+text',
                              marker=dict(size=75, color = sharpe_colors, 
                                          colorscale = 'Bluered_r',
                                          colorbar=dict(title='Sharpe Ratio'),
                                          showscale=True),
                              name = 'Returns',
                              text = individual_cumsum.columns.tolist(),
                              textfont=dict(color='white'),
                              showlegend=False,
                              hovertemplate = '%{y:.2f}%<br>Annualized Volatility: %{x:.2f}%<br>Sharpe Ratio: %{marker.color:.2f}',
                              textposition='middle center'),
                        row=1, col=2)
            
    # Updating layout
    fig1.update_layout(title={
        'text': f'<b>Portfolio Analysis</b>',
        'font': {'size': 24}
    },
                       template = 'plotly_white',
                       height = 650, width = 1250,
                       hovermode = 'x unified',
                       legend_x=.45,
                       legend_y=.5)
        
    fig1.update_yaxes(title_text='Returns (%)', col=1)
    fig1.update_yaxes(title_text='Returns (%)', col = 2)
    fig1.update_xaxes(title_text = 'Date', col = 1)
    fig1.update_xaxes(title_text = 'Annualized Volatility (%)', col =2)
            
    return fig1 # Returning figure


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


def portfolio_vs_benchmark(port_returns, benchmark_returns):

    """
    This function calculates and displays the cumulative returns, annualized volatility, and Sharpe Ratios
    for both the portfolio and the benchmark. It provides a side-by-side comparison to assess the portfolio's
    performance relative to the benchmark.

    Parameters:
    - port_returns (pd.Series): A Pandas Series containing the daily returns of the portfolio.
    - benchmark_returns (pd.Series): A Pandas Series containing the daily returns of the benchmark.

    Returns:
    - fig2: A Plotly Figure object with two subplots:
      1. Line plot showing the cumulative returns of both the portfolio and the benchmark over time.
      2. Scatter plot indicating the annualized volatility and the last cumulative return of both the portfolio
         and the benchmark, colored by their respective Sharpe Ratios.

    Notes:
    - The function assumes that 'numpy' and 'plotly.graph_objects' are imported as 'np' and 'go' respectively.
    - The function also utilizes 'plotly.subplots.make_subplots' for creating subplots.
    - The risk-free rate is assumed to be 1% per annum for Sharpe Ratio calculation.
    """

    # Computing the cumulative returns for the portfolio and the benchmark
    portfolio_cumsum = (((1 + port_returns).cumprod() - 1) * 100).round(2)
    benchmark_cumsum = (((1 + benchmark_returns).cumprod() - 1) * 100).round(2)

    # Computing the annualized volatility for the portfolio and the benchmark
    port_vol = ((port_returns.std() * np.sqrt(252)) * 100).round(2)
    benchmark_vol = ((benchmark_returns.std() * np.sqrt(252)) * 100).round(2)

    # Computing Sharpe Ratio for the portfolio and the benchmark
    excess_port_returns = port_returns - 0.01 / 252
    port_sharpe = (excess_port_returns.mean() / port_returns.std() * np.sqrt(252)).round(2)
    exces_benchmark_returns = benchmark_returns - 0.01 / 252
    benchmark_sharpe = (exces_benchmark_returns.mean() / benchmark_returns.std() * np.sqrt(252)).round(2)

    # Creating a subplot to compare portfolio performance with the benchmark
    fig2 = make_subplots(rows = 1, cols = 2, horizontal_spacing=0.25,
                        column_titles=['Cumulative Returns', 'Portfolio Risk-Reward'],
                        column_widths=[.55, .45],
                        shared_xaxes=False, shared_yaxes=False)

    # Adding the cumulative returns for the portfolio
    fig2.add_trace(go.Scatter(x=portfolio_cumsum.index, 
                             y = portfolio_cumsum,
                             mode = 'lines', name = 'Portfolio', showlegend=False,
                             hovertemplate = '%{y:.2f}%'),
                             row=1,col=1)
    
    # Adding the cumulative returns for the benchmark
    fig2.add_trace(go.Scatter(x=benchmark_cumsum.index, 
                             y = benchmark_cumsum,
                             mode = 'lines', name = 'Benchmark', showlegend=False,
                             hovertemplate = '%{y:.2f}%'),
                             row=1,col=1)
    

    # Creating risk-reward plot for the benchmark and the portfolio
    fig2.add_trace(go.Scatter(x = [port_vol, benchmark_vol], y = [portfolio_cumsum.iloc[-1], benchmark_cumsum.iloc[-1]],
                             mode = 'markers+text', 
                             marker=dict(size = 75, 
                                         color = [port_sharpe, benchmark_sharpe],
                                         colorscale='Bluered_r',
                                         colorbar=dict(title='Sharpe Ratio'),
                                         showscale=True),
                             name = 'Returns', 
                             text=['Portfolio', 'Benchmark'], textposition='middle center',
                             textfont=dict(color='white'),
                             hovertemplate = '%{y:.2f}%<br>Annualized Volatility: %{x:.2f}%<br>Sharpe Ratio: %{marker.color:.2f}',
                             showlegend=False),
                             row = 1, col = 2)
    
    
    # Configuring layout
    fig2.update_layout(title={
        'text': f'<b>Portfolio vs Benchmark</b>',
        'font': {'size': 24}
    },
                      template = 'plotly_white',
                      height = 650, width = 1250,
                      hovermode = 'x unified',
                      #legend_x=.45,
                      #legend_y=.5
                      )
    
    fig2.update_yaxes(title_text='Cumulative Returns (%)', col=1)
    fig2.update_yaxes(title_text='Cumulative Returns (%)', col = 2)
    fig2.update_xaxes(title_text = 'Date', col = 1)
    fig2.update_xaxes(title_text = 'Annualized Volatility (%)', col =2)

    return fig2 # Returning subplots

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


def portfolio_returns(tickers_and_values, start_date, end_date, benchmark):

    """
    This function downloads historical stock data, calculates the weighted returns to build a portfolio,
    and compares these returns to a benchmark.
    It also displays the portfolio allocation and the performance of the portfolio against the benchmark.

    Parameters:
    - tickers_and_values (dict): A dictionary where keys are ticker symbols (str) and values are the current
      amounts (float) invested in each ticker.
    - start_date (str): The start date for the historical data in the format 'YYYY-MM-DD'.
    - end_date (str): The end date for the historical data in the format 'YYYY-MM-DD'.
    - benchmark (str): The ticker symbol for the benchmark against which to compare the portfolio's performance.

    Returns:
    - Displays three plots:
      1. A pie chart showing the portfolio allocation by ticker.
      2. A plot to analyze historical returns and volatility of each security
         in the portfolio. (Not plotted if portfolio only has one security)
      2. A comparison between portfolio returns and volatility against the benchmark over the specified period.

    Notes:
    - The function assumes that 'yfinance', 'pandas', 'plotly.graph_objects', and 'plotly.express' are imported
      as 'yf', 'pd', 'go', and 'px' respectively.
    - For single security portfolios, the function calculates returns without weighting.
    - The function utilizes a helper function 'portfolio_vs_benchmark' for comparing portfolio returns with
      the benchmark, which needs to be defined separately.
    - Another helper function 'perform_portfolio_analysis' is called for portfolios with more than one security,
      which also needs to be defined separately.
    """

    # Obtaining tickers data with yfinance
    df = yf.download(tickers=list(tickers_and_values.keys()),
                     start=start_date, end=end_date)

    # Checking if there is data available in the given date range
    if isinstance(df.columns, pd.MultiIndex):
        missing_data_tickers = []
        for ticker in tickers_and_values.keys():
            first_valid_index = df['Adj Close'][ticker].first_valid_index()
            if first_valid_index is None or first_valid_index.strftime('%Y-%m-%d') > start_date:
                missing_data_tickers.append(ticker)

        if missing_data_tickers:
            error_message = f"No data available for the following tickers starting from {start_date}: {', '.join(missing_data_tickers)}"
            return "error", error_message
    else:
        # For a single ticker, simply check the first valid index
        first_valid_index = df['Adj Close'].first_valid_index()
        if first_valid_index is None or first_valid_index.strftime('%Y-%m-%d') > start_date:
            error_message = f"No data available for the ticker starting from {start_date}"
            return "error", error_message
    
    # Calculating portfolio value
    total_portfolio_value = sum(tickers_and_values.values())

    # Calculating the weights for each security in the portfolio
    tickers_weights = {ticker: value / total_portfolio_value for ticker, value in tickers_and_values.items()}

    # Checking if dataframe has MultiIndex columns
    if isinstance(df.columns, pd.MultiIndex):
        df = df['Adj Close'].fillna(df['Close']) # If 'Adjusted Close' is not available, use 'Close'

    # Checking if there are more than just one security in the portfolio
    if len(tickers_weights) > 1:
        weights = list(tickers_weights.values()) # Obtaining weights
        weighted_returns = df.pct_change().mul(weights, axis = 1) # Computed weighted returns
        port_returns = weighted_returns.sum(axis=1) # Sum weighted returns to build portfolio returns
    # If there is only one security in the portfolio...
    else:
        df = df['Adj Close'].fillna(df['Close'])  # Obtaining 'Adjusted Close'. If not available, use 'Close'
        port_returns = df.pct_change() # Computing returns without weights

    # Obtaining benchmark data with yfinance
    benchmark_df = yf.download(benchmark, 
                               start=start_date, end=end_date) 
    # Obtaining 'Adjusted Close'. If not available, use 'Close'.
    benchmark_df = benchmark_df['Adj Close'].fillna(benchmark_df['Close'])

    # Computing benchmark returns
    benchmark_returns = benchmark_df.pct_change()


    # Plotting a pie plot
    fig = go.Figure(data=[go.Pie(
        labels=list(tickers_weights.keys()), # Obtaining tickers 
        values=list(tickers_weights.values()), # Obtaining weights
        hoverinfo='label+percent', 
        textinfo='label+percent',
        hole=.65,
        marker=dict(colors=px.colors.qualitative.G10)
    )])

    # Defining layout
    fig.update_layout(title={
        'text': '<b>Portfolio Allocation</b>',
        'font': {'size': 24}
    }, height=550, width=1250)

    # Running function to compare portfolio and benchmark
    fig2 = portfolio_vs_benchmark(port_returns, benchmark_returns)    

    #fig.show() # Displaying Portfolio Allocation plot

    # If we have more than one security in the portfolio, 
    # we run function to evaluate each security individually
    fig1 = None
    if len(tickers_weights) > 1:
        fig1 = perform_portfolio_analysis(df, tickers_weights)
        #fig1.show()
    # Displaying Portfolio vs Benchmark plot    
    #fig2.show()
    return "success", (fig, fig1, fig2)
