import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="Jarves Trading Trial 1.5", page_icon="📈", layout="wide")

st.markdown("""
<style>
.stApp{background:#050a14;color:#e8f0ff}
.block-container{padding:.7rem .45rem 3rem;max-width:1400px}
h1,h2,h3{color:#e8f0ff}
[data-testid="stMetric"]{background:#071827;border:1px solid #123149;padding:10px;border-radius:12px}
.panel{background:#050f1d;border:1px solid #143047;border-radius:14px;padding:12px;margin:8px 0}
.small{color:#8aa5bf;font-size:12px}
div[data-baseweb="select"]>div{background:#071827}
@media(max-width:700px){.block-container{padding:.4rem .3rem 2rem}}
</style>
""", unsafe_allow_html=True)

st.markdown("# ⚡ JARVES <span style='color:#00e6ad'>TRADING</span>", unsafe_allow_html=True)
st.caption("TRIAL 1.5 • Mobile-first • Market movers • Candlestick chart + possible order-block zones")

with st.sidebar:
    st.header("⚙️ Scanner settings")
    scan_mode = st.selectbox("Scan universe", ["Watchlist (20)", "First 100 NSE shares"])
    st.caption("Market data is provided by Yahoo Finance and can be delayed or incomplete.")
    if st.button("🔄 Refresh data", use_container_width=True):
        st.cache_data.clear()

WATCHLIST = [
    "RELIANCE", "HDFCBANK", "ICICIBANK", "INFY", "TCS", "SBIN", "AXISBANK",
    "KOTAKBANK", "ITC", "LT", "BHARTIARTL", "TATAMOTORS", "M&M",
    "BAJFINANCE", "WIPRO", "ADANIPORTS", "EICHERMOT", "SUNPHARMA",
    "TATASTEEL", "MARUTI"
]
NSE_URL = "https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv"

@st.cache_data(ttl=300, show_spinner=False)
def get_symbols(mode):
    if mode == "Watchlist (20)":
        return WATCHLIST
    try:
        import requests
        response = requests.get(NSE_URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=12)
        response.raise_for_status()
        csv_df = pd.read_csv(pd.io.common.StringIO(response.text))
        symbol_col = next(c for c in csv_df.columns if c.strip().upper() == "SYMBOL")
        return csv_df[symbol_col].dropna().astype(str).str.strip().tolist()[:100]
    except Exception:
        return WATCHLIST

@st.cache_data(ttl=180, show_spinner=False)
def get_candles(symbol):
    try:
        df = yf.download(
            symbol + ".NS", period="5d", interval="15m",
            progress=False, auto_adjust=False, threads=False
        )
        if df is None or df.empty:
            return pd.DataFrame()
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        needed = ["Open", "High", "Low", "Close"]
        if not all(c in df.columns for c in needed):
            return pd.DataFrame()
        return df.dropna(subset=needed)
    except Exception:
        return pd.DataFrame()

def analyse(symbol, df):
    if df.empty or len(df) < 3:
        return None
    close = df["Close"].astype(float)
    price = float(close.iloc[-1])
    previous = float(close.iloc[-2])
    change_pct = (price / previous - 1) * 100 if previous else 0.0

    ema9 = float(close.ewm(span=9, adjust=False).mean().iloc[-1])
    ema21 = float(close.ewm(span=21, adjust=False).mean().iloc[-1])
    # Trend definition is consistent across all symbols.
    if ema9 > ema21 and price > ema9:
        trend = "UPTREND"
    elif ema9 < ema21 and price < ema9:
        trend = "DOWNTREND"
    else:
        trend = "SIDEWAYS"

    volume = df["Volume"].fillna(0).astype(float) if "Volume" in df.columns else pd.Series(0, index=df.index)
    avg_volume = float(volume.iloc[-21:-1].mean()) if len(volume) > 2 else 0.0
    volume_ratio = float(volume.iloc[-1]) / avg_volume if avg_volume > 0 else 0.0

    recent = df.tail(30)
    support = float(recent["Low"].min())
    resistance = float(recent["High"].max())

    bullish_ob = None
    bearish_ob = None
    candles = df.tail(24)
    for i in range(len(candles) - 1, 0, -1):
        previous_candle = candles.iloc[i - 1]
        current_candle = candles.iloc[i]
        if (bullish_ob is None and previous_candle["Close"] < previous_candle["Open"]
                and current_candle["Close"] > current_candle["Open"]
                and current_candle["Close"] > previous_candle["High"]):
            bullish_ob = (float(previous_candle["Low"]), float(previous_candle["High"]))
        if (bearish_ob is None and previous_candle["Close"] > previous_candle["Open"]
                and current_candle["Close"] < current_candle["Open"]
                and current_candle["Close"] < previous_candle["Low"]):
            bearish_ob = (float(previous_candle["Low"]), float(previous_candle["High"]))
        if bullish_ob and bearish_ob:
            break

    return {
        "Symbol": symbol, "Price": price, "Change %": change_pct,
        "Trend": trend, "Vol Ratio": volume_ratio,
        "Support": support, "Resistance": resistance,
        "Bull OB": bullish_ob, "Bear OB": bearish_ob
    }

symbols = get_symbols(scan_mode)
candle_data = {}
rows = []
with st.spinner(f"Scanning {len(symbols)} shares. This can take a little time…"):
    for symbol in symbols:
        df = get_candles(symbol)
        if not df.empty:
            candle_data[symbol] = df
            result = analyse(symbol, df)
            if result:
                rows.append(result)

market = pd.DataFrame(rows)
if market.empty:
    st.error("Market data abhi nahi mila. Refresh karein ya market hours mein dobara try karein.")
    st.stop()

market = market.sort_values("Change %", ascending=False).reset_index(drop=True)
gainers = market.head(10)
losers = market.nsmallest(10, "Change %")
most_active = market.sort_values("Vol Ratio", ascending=False).head(10)

st.markdown('<div class="panel"><b>◉ MARKET MOVERS</b><br><span class="small">Strong price movers and higher-volume shares are highlighted. Select a share in the chart tab to inspect possible order-block zones.</span></div>', unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4)
m1.metric("Shares received", len(market))
m2.metric("Gainers", int((market["Change %"] > 0).sum()))
m3.metric("Losers", int((market["Change %"] < 0).sum()))
m4.metric("Volume ≥ 1.5×", int((market["Vol Ratio"] >= 1.5).sum()))

flow_tab, movers_tab, chart_tab, scanner_tab = st.tabs(
    ["〰️ FLOW", "▲▼ MOVERS", "📊 CHART + ORDER BLOCKS", "📋 SCANNER"]
)

with flow_tab:
    st.subheader("LIVE MARKET FLOW")
    st.caption("Visual summary of price movers. This is not exchange order-book depth; actual live updates depend on the data provider.")
    fig = go.Figure()
    x = np.linspace(0, 1, 80)
    for j, (_, row) in enumerate(gainers.head(8).iterrows()):
        y = 0.5 + (j + 1) * 0.035 * (x ** 0.7)
        fig.add_trace(go.Scatter(
            x=x, y=y, mode="lines",
            line=dict(width=1.5, color="rgba(0,230,173,0.75)"),
            name=f'{row["Symbol"]} {row["Change %"]:+.2f}%'
        ))
    for j, (_, row) in enumerate(losers.head(8).iterrows()):
        y = 0.5 - (j + 1) * 0.035 * (x ** 0.7)
        fig.add_trace(go.Scatter(
            x=x, y=y, mode="lines",
            line=dict(width=1.5, color="rgba(255,80,124,0.75)"),
            name=f'{row["Symbol"]} {row["Change %"]:+.2f}%'
        ))
    fig.update_layout(
        height=390, template="plotly_dark", paper_bgcolor="#050a14",
        plot_bgcolor="#050a14", margin=dict(l=5, r=5, t=10, b=5),
        xaxis=dict(visible=False), yaxis=dict(visible=False),
        legend=dict(orientation="h", y=-0.15)
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.subheader("Strongest movers")
    st.dataframe(gainers[["Symbol", "Price", "Change %", "Trend", "Vol Ratio"]].round(2),
                 use_container_width=True, hide_index=True)

with movers_tab:
    selected_list = st.radio("Highlight list", ["Gainers", "Losers", "Most Active"], horizontal=True)
    view = gainers if selected_list == "Gainers" else losers if selected_list == "Losers" else most_active
    for _, row in view.iterrows():
        color = "#00e6ad" if row["Change %"] >= 0 else "#ff507c"
        st.markdown(
            f'<div class="panel" style="display:flex;justify-content:space-between;align-items:center">'
            f'<div><b>{row["Symbol"]}</b><br><span class="small">₹{row["Price"]:,.2f} · Vol {row["Vol Ratio"]:.2f}× · {row["Trend"]}</span></div>'
            f'<b style="color:{color}">{row["Change %"]:+.2f}%</b></div>',
            unsafe_allow_html=True
        )

with chart_tab:
    options = market["Symbol"].tolist()
    selected_symbol = st.selectbox("🔎 Search / select share", options)
    row = market.loc[market["Symbol"] == selected_symbol].iloc[0]
    df = candle_data[selected_symbol]

    p1, p2, p3, p4 = st.columns(4)
    p1.metric("Price", f'₹{row["Price"]:,.2f}', f'{row["Change %"]:+.2f}%')
    p2.metric("Trend", row["Trend"])
    p3.metric("Volume ratio", f'{row["Vol Ratio"]:.2f}×')
    p4.metric("Support / Resistance", f'{row["Support"]:.2f} / {row["Resistance"]:.2f}')

    chart = go.Figure()
    chart.add_trace(go.Candlestick(
        x=df.index, open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"],
        name=selected_symbol, increasing_line_color="#00e6ad", decreasing_line_color="#ff507c"
    ))
    if row["Bull OB"]:
        low, high = row["Bull OB"]
        chart.add_hrect(y0=low, y1=high, fillcolor="rgba(0,230,173,0.20)",
                        line_color="#00e6ad", annotation_text="Possible Bullish OB")
    if row["Bear OB"]:
        low, high = row["Bear OB"]
        chart.add_hrect(y0=low, y1=high, fillcolor="rgba(255,80,124,0.18)",
                        line_color="#ff507c", annotation_text="Possible Bearish OB")
    chart.add_hline(y=row["Support"], line_dash="dot", line_color="#4b9dff", annotation_text="Support")
    chart.add_hline(y=row["Resistance"], line_dash="dot", line_color="#f6c85f", annotation_text="Resistance")
    chart.update_layout(
        height=470, template="plotly_dark", paper_bgcolor="#050a14",
        plot_bgcolor="#050a14", margin=dict(l=5, r=5, t=20, b=5),
        xaxis_rangeslider_visible=False
    )
    st.plotly_chart(chart, use_container_width=True, config={"displayModeBar": False})

    ob1, ob2 = st.columns(2)
    with ob1:
        st.markdown("#### 🟢 Bullish order-block candidate")
        if row["Bull OB"]:
            st.success(f'₹{row["Bull OB"][0]:.2f} – ₹{row["Bull OB"][1]:.2f}')
        else:
            st.info("Available candles mein clear bullish candidate nahi mila.")
    with ob2:
        st.markdown("#### 🔴 Bearish order-block candidate")
        if row["Bear OB"]:
            st.error(f'₹{row["Bear OB"][0]:.2f} – ₹{row["Bear OB"][1]:.2f}')
        else:
            st.info("Available candles mein clear bearish candidate nahi mila.")
    st.caption("Order-block zones are rule-based estimates, not guaranteed institutional zones or trading recommendations.")

with scanner_tab:
    display = market[["Symbol", "Price", "Change %", "Trend", "Vol Ratio", "Support", "Resistance"]].copy()
    st.dataframe(display.round(2), use_container_width=True, hide_index=True, height=520)

st.markdown("---")
st.caption(
    f"JARVES TRADING • Yahoo Finance data • Rendered {datetime.now().strftime('%d-%b-%Y %H:%M:%S')} • "
    "Verify prices with your broker before trading. This app does not place orders."
)
