import streamlit as st
import pandas as pd
import numpy as np
from backend import PortfolioOptimizer

st.set_page_config(page_title="Portfolio Results", page_icon="📊")

st.title("📊 Portfolio Optimization Results")

# Retrieve all session state variables from the main page
assets = st.session_state.get("assets", [])
phi = st.session_state.get("phi", 250)
allow_shorts = st.session_state.get("allow_shorts", False)
sampling_rate = st.session_state.get("sampling_rate", "1d")
portfolio_total = st.session_state.get("portfolio_total", 10000)

st.write("### ⚙️ Settings Recap")
st.write(f"**Assets:** {assets}")
st.write(f"**Sampling Rate:** {sampling_rate}")
st.write(f"**φ (risk factor):** {phi}")
st.write(f"**Shorts Allowed:** {allow_shorts}")
st.write(f"**Portfolio Total:** ${portfolio_total:,.2f}")

# (Placeholder for backend logic)
st.divider()
if len(assets) != 0:
    optimizer = PortfolioOptimizer(assets, phi, allow_shorts,sampling_rate, portfolio_total)
    optimizer.fetch_data()
    cov_matrix, corr_matrix = optimizer.compute_cov_corr()
    data = optimizer.run_optimization()

    #print out cov, corr_matrix
    cov_df = pd.DataFrame(cov_matrix, index=optimizer.assets, columns=optimizer.assets)
    corr_df = pd.DataFrame(corr_matrix, index=optimizer.assets, columns=optimizer.assets)

    # Display in Streamlit
    st.write("### Covariance Matrix")
    st.dataframe(cov_df.style.format("{:.6f}"))

    st.write("### Correlation Matrix")
    st.dataframe(corr_df.style.format("{:.3f}"))


    #print out optimnal vector
    pvec = data['pvec']
    mean_returns = data["mr"]
    percentages = [a/portfolio_total * 100 for a in pvec]
    df = pd.DataFrame({
        "Asset": assets,
        "Amount ($)": pvec,
        "Percentage (%)": percentages,
        "Mean Returns (%)": mean_returns * 100
    })

    # Optional: format columns for readability
    df["Amount ($)"] = df["Amount ($)"].map("${:,.2f}".format)
    df["Percentage (%)"] = df["Percentage (%)"].map("{:.2f}%".format)
    df["Mean Returns (%)"] = df["Mean Returns (%)"].map("${:,.2f}".format)

    # Display in Streamlit
    st.write("### Portfolio Allocation")
    st.dataframe(df)

    downside_99 = data['risk']
    expected_returns = data['expected_returns']
    std = data['std']

    expected_return_pct = (expected_returns/ portfolio_total) * 100
    st.metric("Expected Return", f"{expected_return_pct:.2f}% per {sampling_rate.lower()}")

    periods_per_year = {
        "15m": 252*6.5*4,   # approx 252 trading days, 6.5 hours/day, 4 intervals/hour
        "30m": 252*6.5*2,
        "1h": 252*6.5,
        "1d": 252,
        "1wk": 52,
        "1mo": 12
    }

    annual_factor = periods_per_year[optimizer.sampling_rate]
    annualized_return = expected_return_pct * annual_factor 

    st.metric("Expected Annualized Return", f"{annualized_return:.2f}% per year")

    # --- 99% downside ---
    st.metric("99% Downside Risk", f"{downside_99:.2f}% of portfolio")
else:
    st.write('Your all Cash')
