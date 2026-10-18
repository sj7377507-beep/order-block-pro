import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import requests
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import time

# Jarves Trading — mobile-first visual prototype.
# Note: yfinance data may be delayed/incomplete. This is NOT a guaranteed real-time feed.
# Kotak Neo API integration should replace the market-data functions after API auth/session setup.

st.set_page_config(
    page_title="Jarves Trading | Live Market Flow",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
:root { color-scheme: dark; }
.stApp { background: #020711; color: #e8f2ff; }
[data-testid="stHeader"] { background: rgba(2,7,17,0.95); }
.block-container { max-width: 1600px; padding: .7rem .7rem 5rem; }
h1,h2,h3,h4,p,span,label { color: #e8f2ff; }
.jarves-brand { display:flex; align-items:center; gap:12px; padding:7px 2px 14px; }
.jarves-logo { font-size:34px; color:#00ffc3; line-height:1; text-shadow:0 0 18px #00ffc3; }
.jarves-title { font-size:25px; font-weight:850; letter-spacing:2px; line-height:1.05; }
.jarves-sub { font-size:10px; letter-spacing:4px; color:#7ba8cb; }
.live-pill { display:inline-block; padding:7px 12px; border:1px solid #006b59; border-radius:30px; color:#00ffc3; background:#03221f; font-size:12px; font-weight:700; }
.metric-card { background:linear-gradient(140deg,#07182a,#03101c); border:1px solid #10334c; border-radius:12px; padding:13px 14px; min-height:92px; box-shadow:inset 0 0 18px #00131e; }
.metric-name { color:#8daecc; font-size:12px; font-weight:700; }
.metric-value { font-size:20px; font-weight:800; margin-top:4px; }
.metric-change { font-size:12px; font-weight:700; margin-top:2px; }
.green { color:#00ffc3 !important; }
.red { color:#ff477e !important; }
.muted { color:#7895ad !important; }
.panel { background:#030d19; border:1px solid #10334c; border-radius:14px; padding:13px; margin:8px 0; }
.panel-title { font-size:17px; font-weight:800; letter-spacing:.4px; margin-bottom:2px; }
.panel-sub { color:#83a6c4; font-size:12px; margin-bottom:10px; }
.stock-row { display:flex; align-items:center; justify-content:space-between; gap:8px; padding:10px 8px; border-bottom:1px solid #102236; border-radius:7px; }
.stock-row.selected { border:1px solid #00dcb1; background:#03231f; }
.stock-name { font-weight:700; font-size:13px; }
.stock-price { color:#b8cce0; font-size:12px; }
.stock-pct { font-weight:800; font-size:13px; }
.tag { display:inline-block; border:1px solid #116b59; background:#032a23; color:#00ffc3; padding:3px 7px; border-radius:6px; font-size:10px; font-weight:700; }
.tag-red { border-color:#76243e; background:#2a0917; color:#ff477e; }
div.stButton > button { width:100%; border:1px solid #14405a; background:#061728; color:#d9eaff; border-radius:9px; padding:8px 10px; }
div.stButton > button:hover { border-color:#00ffc3; color:#00ffc3; }
div[data-baseweb="select"] > div { background:#061728; border-color:#17405a; }
[data-testid="stDataFrame"] { border:1px solid #123149; border-radius:10px; }
hr { border-color:#10283a; }
footer {visibility:hidden;}
@media (max-width: 768px) {
  .block-container { padding:.35rem .35rem 4rem; }
  .jarves-title { font-size:20px; }
  .jarves-logo { font-size:29px; }
  .metric-card { padding:9px; min-height:79px; }
  .metric-value { font-size:16px; }
  .metric-name,.metric-change { font-size:10px; }
  .panel { padding:9px; }
  .panel-title { font-size:15px; }
}
</style>
""", unsafe_allow_html=True)

# --------------------------- Data helpers ---------------------------
@st.cache_data(ttl=180, show_spinner=False)
def get_nse_symbols():
    url = "https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv"
    headers = {"User-Agent": "Mozilla/5.0", "Accept": "text/csv,*/*"}
    try:
        r = requests.get(url, headers=headers, timeout=12)
        r.raise_for_status()
        df = pd.read_csv(pd.io.common.BytesIO(r.content))
        col = next((c for c in df.columns if c.strip().upper() == "SYMBOL"), None)
        if col:
            syms = df[col].dropna().astype(str).str.strip().tolist()
            return sorted(set(s for s in syms if s and s != "nan"))
    except Exception:
        pass
    # Small fallback universe only; clearly labelled in UI if NSE list can't be fetched.
    return ["RELIANCE","TCS","HDFCBANK","ICICIBANK","INFY","SBIN","LT","AXISBANK",
            "WIPRO","TATAMOTORS","ITC","BHARTIARTL","KOTAKBANK","BAJFINANCE","SUNPHARMA",
            "TATASTEEL","MARUTI","NTPC","POWERGRID","ONGC"]

@st.cache_data(ttl=180, show_spinner=False)
def download_market_data(symbols, period="5d", interval="15m"):
    result = {}
    # Batch in moderate groups to reduce provider throttling.
    for start in range(0, len(symbols), 30):
        batch = symbols[start:start+30]
        tickers = [s + ".NS" for s in batch]
        try:
            raw = yf.download(
                tickers=tickers, period=period, interval=interval,
                group_by="ticker", auto_adjust=True, progress=False,
                threads=True, prepost=False
            )
            if raw is None or raw.empty:
                continue
            for sym in batch:
                ticker = sym + ".NS"
                try:
                    if isinstance(raw.columns, pd.MultiIndex):
                        if ticker not in raw.columns.get_level_values(0):
                            continue
                        d = raw[ticker].copy()
                    elif len(batch) == 1:
                        d = raw.copy()
                    else:
                        continue
                    d = d.dropna(subset=["Close"])
                    if len(d) >= 2:
                        result[sym] = d
                except Exception:
                    continue
        except Exception:
            continue
        time.sleep(.15)
    return result

def analyze_one(sym, d):
    d = d.copy().dropna(subset=["Close"])
    if len(d) < 2:
        return None
    close = d["Close"].astype(float)
    volume = d["Volume"].fillna(0).astype(float) if "Volume" in d else pd.Series(0, index=d.index)
    last = float(close.iloc[-1])
    prev = float(close.iloc[-2])
    pct = (last / prev - 1) * 100 if prev else 0.0
    ema9 = close.ewm(span=9, adjust=False).mean()
    ema21 = close.ewm(span=21, adjust=False).mean()
    trend = "UPTREND" if ema9.iloc[-1] > ema21.iloc[-1] else "DOWNTREND"
    v_now = float(volume.iloc[-1]) if len(volume) else 0.0
    v_avg = float(volume.iloc[-21:-1].mean()) if len(volume) > 2 else 0.0
    vol_ratio = v_now / v_avg if v_avg > 0 else 0.0
    # Simple recent swing ranges, for visual guidance only—not institutional order-flow data.
    recent = d.tail(30)
    support = float(recent["Low"].min()) if "Low" in recent else float(close.tail(20).min())
    resistance = float(recent["High"].max()) if "High" in recent else float(close.tail(20).max())
    # Basic candle-based heuristic zones; not a true order-block algorithm.
    bull_low = bull_high = bear_low = bear_high = np.nan
    if len(d) >= 5 and all(c in d.columns for c in ["Open","High","Low","Close"]):
        x = d.tail(20)
        for i in range(len(x)-1, 0, -1):
            row = x.iloc[i]
            prior = x.iloc[i-1]
            if row["Close"] > row["Open"] and prior["Close"] < prior["Open"]:
                bull_low, bull_high = float(prior["Low"]), float(prior["High"])
                break
        for i in range(len(x)-1, 0, -1):
            row = x.iloc[i]
            prior = x.iloc[i-1]
            if row["Close"] < row["Open"] and prior["Close"] > prior["Open"]:
                bear_low, bear_high = float(prior["Low"]), float(prior["High"])
                break
    return {
        "Symbol": sym, "Price": last, "Change %": pct, "Trend": trend,
        "Volume": v_now, "Vol Ratio": vol_ratio, "Support": support,
        "Resistance": resistance, "Bull OB Low": bull_low, "Bull OB High": bull_high,
        "Bear OB Low": bear_low, "Bear OB High": bear_high,
    }

def money(x):
    try: return f"₹{float(x):,.2f}"
    except: return "—"

def pct_html(x):
    try:
        return f'<span class="{"green" if float(x)>=0 else "red"}">{float(x):+.2f}%</span>'
    except:
        return '<span class="muted">—</span>'

def flow_figure(df, selected=None):
    fig = go.Figure()
    # Decorative flow ribbons represent the stock's measured % change, not order-book depth.
    if df is not None and not df.empty:
        top = df.sort_values("Change %", ascending=False).head(8)
        bottom = df.sort_values("Change %").head(8)
        xs = np.linspace(0, 1, 60)
        for j, (_, row) in enumerate(top.iterrows()):
            y_end = min(0.9, 0.12 + j*0.085 + max(0, row["Change %"])*0.025)
            ys = y_end * (xs**(0.72 + j*0.025)) + 0.5*(1-xs)
            fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", line=dict(width=1.1, color=f"rgba(0,255,190,{max(.25,.7-j*.05)})"), hovertemplate=f'{row["Symbol"]}: {row["Change %"]:+.2f}%<extra></extra>', showlegend=False))
        for j, (_, row) in enumerate(bottom.iterrows()):
            y_end = max(0.08, 0.42 - j*0.045 - abs(min(0, row["Change %"]))*0.025)
            ys = y_end * (xs**(0.72 + j*0.025)) + 0.5*(1-xs)
            fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", line=dict(width=1.1, color=f"rgba(255,55,120,{max(.25,.7-j*.05)})"), hovertemplate=f'{row["Symbol"]}: {row["Change %"]:+.2f}%<extra></extra>', showlegend=False))
    fig.add_hline(y=.5, line_color="#91a8c0", line_width=1)
    fig.update_layout(
        height=390, margin=dict(l=4,r=4,t=8,b=4),
        paper_bgcolor="#030d19", plot_bgcolor="#030d19",
        xaxis=dict(visible=False, range=[0,1], fixedrange=True),
        yaxis=dict(visible=False, range=[0,1], fixedrange=True),
        showlegend=False, hovermode="closest"
    )
    return fig

def candle_figure(d, analysis):
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=.03,
                        row_heights=[.78,.22])
    fig.add_trace(go.Candlestick(
        x=d.index, open=d["Open"], high=d["High"], low=d["Low"], close=d["Close"],
        name="Price", increasing_line_color="#00e6a8", decreasing_line_color="#ff477e"
    ), row=1, col=1)
    if "Volume" in d:
        colors = ["#00b991" if c >= o else "#e83d70" for o,c in zip(d["Open"],d["Close"])]
        fig.add_trace(go.Bar(x=d.index,y=d["Volume"],marker_color=colors,opacity=.65,name="Volume"),row=2,col=1)
    if analysis:
        for low, high, color, label in [
            (analysis["Bull OB Low"],analysis["Bull OB High"],"rgba(0,255,190,.18)","Bullish OB (heuristic)"),
            (analysis["Bear OB Low"],analysis["Bear OB High"],"rgba(255,55,120,.18)","Bearish OB (heuristic)")
        ]:
            if pd.notna(low) and pd.notna(high):
                fig.add_hrect(y0=low,y1=high,fillcolor=color,line_color=color,annotation_text=label,annotation_font_color="#c8e9ff",row=1,col=1)
        fig.add_hline(y=analysis["Support"],line_dash="dot",line_color="#16a7ff",annotation_text="Support",row=1,col=1)
        fig.add_hline(y=analysis["Resistance"],line_dash="dot",line_color="#f5b942",annotation_text="Resistance",row=1,col=1)
    fig.update_layout(
        height=360, margin=dict(l=5,r=5,t=12,b=5), paper_bgcolor="#030d19",plot_bgcolor="#030d19",
        font=dict(color="#c5d8ed",size=10), xaxis_rangeslider_visible=False,
        legend=dict(orientation="h",y=1.02,x=0), showlegend=False
    )
    fig.update_xaxes(gridcolor="#102538", zerolinecolor="#102538")
    fig.update_yaxes(gridcolor="#102538", zerolinecolor="#102538")
    return fig

# --------------------------- Header ---------------------------
st.markdown("""
<div class="jarves-brand">
  <div class="jarves-logo">↗</div>
  <div><div class="jarves-title">JARVES</div><div class="jarves-sub">T R A D I N G</div></div>
  <div style="margin-left:auto"><span class="live-pill">● MARKET FLOW</span></div>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## ⚙️ Scanner Settings")
    scan_limit = st.selectbox("Scan universe", ["First 100 NSE shares (faster)", "First 250 NSE shares", "All available NSE EQ shares"], index=0)
    interval = st.selectbox("Chart timeframe", ["5m", "15m", "30m", "1h", "1d"], index=1)
    refresh = st.selectbox("Refresh interval", ["Manual", "60 seconds", "3 minutes"], index=0)
    st.caption("Market data provider in this prototype: Yahoo Finance. Kotak Neo API connection is not yet activated by this file.")
    if st.button("Refresh market data"):
        st.cache_data.clear()
        st.rerun()

# NSE index data is separately attempted. yfinance may be delayed.
index_values = {}
for label, ticker in [("NIFTY 50","^NSEI"),("BANKNIFTY","^NSEBANK"),("SENSEX","^BSESN")]:
    try:
        q = yf.download(ticker, period="5d", interval="1d", progress=False, auto_adjust=True)
        if not q.empty and len(q) >= 2:
            c = q["Close"].dropna()
            index_values[label] = (float(c.iloc[-1]), (float(c.iloc[-1])/float(c.iloc[-2])-1)*100)
    except Exception:
        pass

symbols = get_nse_symbols()
if scan_limit.startswith("First 100"):
    symbols = symbols[:100]
elif scan_limit.startswith("First 250"):
    symbols = symbols[:250]

with st.spinner(f"Loading market data for up to {len(symbols)} NSE shares…"):
    raw_data = download_market_data(tuple(symbols), period="5d", interval=interval)
rows = []
for sym, data in raw_data.items():
    a = analyze_one(sym, data)
    if a:
        rows.append(a)
market = pd.DataFrame(rows)

# Header metrics
if index_values:
    cols = st.columns(3)
    for col, label in zip(cols, ["NIFTY 50","BANKNIFTY","SENSEX"]):
        with col:
            if label in index_values:
                value, change = index_values[label]
                st.markdown(f"""<div class="metric-card"><div class="metric-name">{label}</div>
                <div class="metric-value">{value:,.2f}</div><div class="metric-change">{pct_html(change)}</div></div>""", unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="metric-card"><div class="metric-name">{label}</div><div class="metric-value">Unavailable</div><div class="metric-change muted">Provider returned no data</div></div>', unsafe_allow_html=True)
else:
    st.info("Index data unavailable from the current provider. The app will not create fake market prices.")

st.write("")
tab_market, tab_flow, tab_top, tab_bottom, tab_ob = st.tabs(["MARKET", "FLOW", "▲ TOP", "▼ BOTTOM", "ORDER BLOCKS"])

if market.empty:
    st.warning("Market data abhi load nahi hua. Internet/provider rate limit ho sakta hai. Refresh karke dobara try karein. Is prototype mein fake prices nahi dikhaye jaate.")
    st.stop()

gainers = market.sort_values("Change %", ascending=False)
losers = market.sort_values("Change %")
active = market.sort_values("Volume", ascending=False)
bullish = market[(market["Trend"]=="UPTREND") & (market["Change %"]>0)].sort_values(["Change %","Vol Ratio"],ascending=False)
bearish = market[(market["Trend"]=="DOWNTREND") & (market["Change %"]<0)].sort_values("Change %")
volume_break = market[market["Vol Ratio"]>=1.5].sort_values("Vol Ratio",ascending=False)
orderblocks = market[market["Bull OB Low"].notna() | market["Bear OB Low"].notna()].copy()

with tab_market:
    left, right = st.columns([1.7,1], gap="small")
    with left:
        st.markdown('<div class="panel"><div class="panel-title">〰 LIVE MARKET FLOW</div><div class="panel-sub">Green = positive move • Red = negative move • Decorative flow lines are based on scanned % change</div></div>',unsafe_allow_html=True)
        st.plotly_chart(flow_figure(market), use_container_width=True, config={"displayModeBar":False})
        st.markdown('<div class="panel-title">SECTOR / MARKET PULSE</div>',unsafe_allow_html=True)
        st.caption("Sector heatmap is not included yet; the scanner below ranks individual shares.")
    with right:
        st.markdown('<div class="panel"><div class="panel-title">◉ LIVE MARKET MOVERS</div><div class="panel-sub">Tap a share name below to open its chart and order-block analysis</div></div>',unsafe_allow_html=True)
        view = st.radio("Mover list",["Gainers","Losers","Most Active"],horizontal=True,label_visibility="collapsed",key="mover_radio")
        view_df = gainers.head(10) if view=="Gainers" else (losers.head(10) if view=="Losers" else active.head(10))
        for _, r in view_df.iterrows():
            sign_class = "green" if r["Change %"] >= 0 else "red"
            st.markdown(f"""<div class="stock-row"><div><div class="stock-name">{r['Symbol']}</div><div class="stock-price">{money(r['Price'])} · Vol {r['Vol Ratio']:.1f}×</div></div><div class="stock-pct {sign_class}">{r['Change %']:+.2f}%</div></div>""",unsafe_allow_html=True)
        st.markdown('<br><span class="tag">UPTREND</span> <span class="tag tag-red">DOWNTREND</span>',unsafe_allow_html=True)
    st.markdown("### 📊 Full NSE scan results")
    st.caption(f"Successfully received data for {len(market)} of up to {len(symbols)} requested shares. Data provider may omit or throttle some symbols.")
    display = market[["Symbol","Price","Change %","Trend","Vol Ratio","Support","Resistance"]].copy()
    display["Price"] = display["Price"].map(lambda x: round(x,2))
    display["Change %"] = display["Change %"].map(lambda x: round(x,2))
    display["Vol Ratio"] = display["Vol Ratio"].map(lambda x: round(x,2))
    st.dataframe(display, use_container_width=True, hide_index=True, height=340)

with tab_flow:
    st.markdown("### LIVE MARKET FLOW")
    st.caption("This visualization ranks market movers. It is not exchange order-book depth and does not predict guaranteed price direction.")
    st.plotly_chart(flow_figure(market), use_container_width=True, config={"displayModeBar":False})
    a,b,c = st.columns(3)
    a.metric("Shares scanned", len(market))
    b.metric("Positive movers", int((market["Change %"]>0).sum()))
    c.metric("Negative movers", int((market["Change %"]<0).sum()))

with tab_top:
    st.markdown("### ▲ TOP MOVERS")
    st.dataframe(gainers[["Symbol","Price","Change %","Trend","Vol Ratio","Volume"]].head(30).round(2),use_container_width=True,hide_index=True)

with tab_bottom:
    st.markdown("### ▼ BOTTOM MOVERS")
    st.dataframe(losers[["Symbol","Price","Change %","Trend","Vol Ratio","Volume"]].head(30).round(2),use_container_width=True,hide_index=True)

with tab_ob:
    st.markdown("### ORDER BLOCK CANDIDATES")
    st.caption("Basic candle heuristic only. These are possible zones, not validated institutional order blocks or trade recommendations.")
    if orderblocks.empty:
        st.info("Abhi available candles se potential order-block zone nahi mili.")
    else:
        st.dataframe(orderblocks[["Symbol","Price","Change %","Trend","Bull OB Low","Bull OB High","Bear OB Low","Bear OB High","Support","Resistance"]].round(2),use_container_width=True,hide_index=True)

st.markdown("---")
st.markdown("## 🔎 Open a share — chart + order-block zones")
options = market.sort_values("Change %",ascending=False)["Symbol"].tolist()
default_symbol = options[0] if options else symbols[0]
selected = st.selectbox("Select / search stock", options, index=options.index(default_symbol) if default_symbol in options else 0)
selected_data = raw_data.get(selected)
selected_row = market[market["Symbol"]==selected]
analysis = selected_row.iloc[0].to_dict() if not selected_row.empty else None

if selected_data is not None and not selected_data.empty:
    st.markdown(f'<div class="panel"><div class="panel-title">{selected} · NSE</div><div class="panel-sub">Selected share chart, possible order-block zones and support/resistance</div></div>',unsafe_allow_html=True)
    m1,m2,m3,m4 = st.columns(4)
    if analysis:
        m1.metric("Price",money(analysis["Price"]),f'{analysis["Change %"]:+.2f}%')
        m2.metric("Trend",analysis["Trend"])
        m3.metric("Volume ratio",f'{analysis["Vol Ratio"]:.2f}×')
        m4.metric("Support / Resistance",f'{analysis["Support"]:.2f} / {analysis["Resistance"]:.2f}')
    st.plotly_chart(candle_figure(selected_data,analysis),use_container_width=True,config={"displayModeBar":False})
    if analysis:
        ob1,ob2,setup = st.columns(3)
        with ob1:
            st.markdown("#### 🟢 Bullish order-block candidate")
            if pd.notna(analysis["Bull OB Low"]):
                st.success(f'{analysis["Bull OB Low"]:.2f} – {analysis["Bull OB High"]:.2f}')
            else:
                st.caption("No candidate found in current candles.")
        with ob2:
            st.markdown("#### 🔴 Bearish order-block candidate")
            if pd.notna(analysis["Bear OB Low"]):
                st.error(f'{analysis["Bear OB Low"]:.2f} – {analysis["Bear OB High"]:.2f}')
            else:
                st.caption("No candidate found in current candles.")
        with setup:
            st.markdown("#### 📌 Planning levels")
            st.write(f'**Support:** {analysis["Support"]:.2f}')
            st.write(f'**Resistance:** {analysis["Resistance"]:.2f}')
            st.caption("Entry, stop-loss and targets should be calculated only after your setup rules and risk per trade are defined.")
else:
    st.warning("Selected share ka candle data available nahi hai.")

st.markdown("---")
st.caption("JARVES TRADING • UI prototype • Market data can be delayed. Order-block zones are heuristic estimates, not financial advice. Never place a trade from these signals without checking the live chart and risk.")
