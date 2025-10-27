import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Portfolio Optimizer", layout="wide")

st.title("📊 Portfolio Optimization Tool")
st.write("Select your assets and data sampling rate to begin.")


st.header("📈 Select Assets")

# --- (1) Dropdown of common stocks ---
common_stocks = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "NVDA",
    "JPM", "V", "UNH", "DIS", "NFLX", "BAC", "KO", "PEP",
    "INTC", "AMD", "NKE", "XOM", "PG"
]

dropdown_selection = st.multiselect(
    "Choose from common stocks:",
    options=common_stocks,
    default=["AAPL", "MSFT"],
    help="Select any number of these common stocks."
)

# --- (2) Text input for custom tickers ---
manual_input = st.text_input(
    "Add custom tickers (comma-separated, e.g. IBM, TSM, SHOP):",
    value="",
    help="You can type custom tickers here if they're not in the dropdown."
)

# --- (3) Combine and clean all tickers ---
custom_symbols = [s.strip().upper() for s in manual_input.split(",") if s.strip()]
all_symbols = list(set(dropdown_selection + custom_symbols))  # remove duplicates

st.write(f"**Selected symbols:** {', '.join(all_symbols) if all_symbols else 'None'}")

# --- (4) Validate tickers with yfinance ---
if st.button("✅Confirm Portfolio"):
    valid_symbols = []
    invalid_symbols = []

    progress = st.progress(0)
    for i, sym in enumerate(all_symbols):
        try:
            ticker = yf.Ticker(sym)
            info = ticker.info
            # Newer versions of yfinance deprecate .info — fallback check:
            if info and ("shortName" in info or "longName" in info):
                valid_symbols.append(sym)
            else:
                invalid_symbols.append(sym)
        except Exception:
            invalid_symbols.append(sym)
        progress.progress((i + 1) / len(all_symbols))

    st.session_state["assets"] = valid_symbols

    # Display results
    if valid_symbols:
        st.success(f"✅ Valid symbols: {', '.join(valid_symbols)}")
    if invalid_symbols:
        st.warning(f"⚠️ Invalid or unrecognized: {', '.join(invalid_symbols)}")

# --- Optional: limit total number of stocks ---
MAX_ASSETS = 10
if "assets" in st.session_state and len(st.session_state["assets"]) > MAX_ASSETS:
    st.error(f"⚠️ You can select at most {MAX_ASSETS} stocks.")
    st.session_state["assets"] = st.session_state["assets"][:MAX_ASSETS]

# --- (5) Sampling rate selection ---
st.subheader("⏱️ Sampling Rate")

sampling_options = {
    "15 Minutes": "15m",
    "30 Minutes": "30m",
    "1 Hour": "1h",
    "1 Day (Recommended)": "1d",
    "1 Week": "1wk",
    "1 Month": "1mo"
}

sampling_choice = st.selectbox(
    "Select data sampling rate:",
    options=list(sampling_options.keys()),
    index=3,  # pre-select "1 Day (Recommended)"
    help="Choose how frequently to sample stock data for portfolio analysis."
)

sampling_interval = sampling_options[sampling_choice]

st.session_state["sampling_interval"] = sampling_interval

st.write(f"📊 Sampling every **{sampling_choice}** → interval code: `{sampling_interval}`")

# --- (6) Portfolio Risk and Phi Selector ---
st.subheader("🎯 Portfolio Risk Settings")

st.markdown("**φ (phi)** controls the risk-return tradeoff. Recommended range: `0.01 ≤ φ ≤ 100,000`")

risk_mode = st.radio(
    "Select Risk Mode:",
    options=["Low Risk (φ = 1)", "Medium Risk (φ = 250)", "High Risk (φ = 10000)", "Manual φ Entry"],
    index=1,  # Default to Medium Risk
    help="Select a preset risk level or enter your own φ value."
)

# Default phi values for presets
phi_values = {
    "Low Risk (φ = 1)": 1,
    "Medium Risk (φ = 250)": 250,
    "High Risk (φ = 10000)": 10000
}

if risk_mode in phi_values:
    phi = phi_values[risk_mode]
else:
    phi = st.number_input(
        "Enter custom φ (risk factor):",
        min_value=0.01,
        max_value=100000.0,
        value=250.0,
        step=0.01,
        help="Smaller φ → lower risk tolerance; Larger φ → higher risk tolerance."
    )

st.session_state["phi"] = phi
st.write(f"Selected φ (risk factor): **{phi:.2f}**")

# --- (7) Portfolio Total ---
st.subheader("💰 Portfolio Total")

portfolio_total = st.number_input(
    "Enter total portfolio amount ($):",
    min_value=0.0,
    value=10000.0,
    step=100.0,
    help="Total amount to invest. Default is $10,000."
)

st.session_state["portfolio_total"] = portfolio_total
st.write(f"Portfolio total: **${portfolio_total:,.2f}**")

# --- (8) Short Selling Option ---
st.subheader("📉 Short Selling")

allow_shorts = st.toggle(
    "Allow short selling (use Lagrange method instead of PGD)",
    value=False,
    help="If enabled, short positions are allowed (Lagrange method). If disabled, only long positions are used (PGD)."
)

st.session_state["allow_shorts"] = allow_shorts
st.write("Short selling allowed:" if allow_shorts else "Only long positions (no shorts).")
