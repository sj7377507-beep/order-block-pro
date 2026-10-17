import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import yfinance as yf
import time

# 1. Page Config
st.set_page_config(
    page_title="OrderBlock.com Clone - Live Market Flow",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Glowing Neon CSS & OrderBlock.com Design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    .stApp {
        background-color: #05070c;
        color: #e5e7eb;
        font-family: 'Inter', sans-serif;
    }
    
    /* Neon Glow & Pulse Animations */
    @keyframes pulse-green {
        0% { box-shadow: 0 0 5px #00ff87, 0 0 10px #00ff87; }
        50% { box-shadow: 0 0 15px #00ff87, 0 0 25px #00ff87; }
        100% { box-shadow: 0 0 5px #00ff87, 0 0 10px #00ff87; }
    }
    
    @keyframes pulse-red {
        0% { box-shadow: 0 0 5px #ff1744, 0 0 10px #ff1744; }
        50% { box-shadow: 0 0 15px #ff1744, 0 0 25px #ff1744; }
        100% { box-shadow: 0 0 5px #ff1744, 0 0 10px #ff1744; }
    }

    .glow-bullish {
        background: rgba(0, 255, 135, 0.08);
        border: 1px solid #00ff87;
        box-shadow: 0 0 12px rgba(0, 255, 135, 0.3);
        border-radius: 10px;
        padding: 12px;
        text-align: center;
    }

    .glow-bearish {
        background: rgba(255, 23, 68, 0.08);
        border: 1px solid #ff1744;
        box-shadow: 0 0 12px rgba(255, 23, 68, 0.3);
        border-radius: 10px;
        padding: 12px;
        text-align: center;
    }
    
    .metric-title {
        font-size: 11px;
        letter-spacing: 1px;
        text-transform: uppercase;
        color: #9ca3af;
    }
    
    .metric-value-bull {
        font-size: 26px;
        font-weight: 700;
        color: #00ff87;
        text-shadow: 0 0 10px rgba(0,255,135,0.6);
    }
    
    .metric-value-bear {
        font-size: 26px;
        font-weight: 700;
        color: #ff1744;
        text-shadow: 0 0 10px rgba(255,23,68,0.6);
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# 3. Top Header Bar
head1, head2, head3 = st.columns([3, 2, 2])
with head1:
    st.markdown("### ⚡ **ORDER BLOCK** <span style='font-size:12px; color:#00ff87; background:rgba(0,255,135,0.1); padding:3px 8px; border-radius:4px; border:1px solid #00ff87;'>MARKET FLOW PRO</span>", unsafe_allow_html=True)

with head2:
    market_index = st.selectbox("Market Universe", ["NIFTY 50 / F&O TOP STOCKS", "NIFTY BANK", "NIFTY IT"], label_visibility="collapsed")

with head3:
    st.markdown("<div style='text-align:right; font-size:12px; color:#00ff87; padding-top:8px;'>● LIVE LIQUIDITY FLOW SCANNER</div>", unsafe_allow_html=True)

# 4. Stock Universe Definition
MARKET_STOCKS = [
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "SBIN.NS", 
    "ICICIBANK.NS", "AXISBANK.NS", "M&M.NS", "FEDERALBNK.NS", "DRREDDY.NS", 
    "NTPC.NS", "CANBK.NS", "SUZLON.NS", "TATALTY.NS", "DIVISLAB.NS", 
    "PAYTM.NS", "EICHERMOT.NS", "BHARTIARTL.NS", "LT.NS", "TATAMOTORS.NS"
]

@st.cache_data(ttl=30)
def scan_whole_market():
    results = []
    bullish_count = 0
    bearish_count = 0
    
    # Download batch data for market
    data = yf.download(MARKET_STOCKS, period="5d", interval="15m", group_by='ticker', progress=False)
    
    for symbol in MARKET_STOCKS:
        try:
            df = data[symbol].dropna()
            if df.empty:
                continue
            
            close = df['Close'].iloc[-1]
            prev_close = df['Close'].iloc[-2]
            pct_change = ((close - prev_close) / prev_close) * 100
            
            vol = df['Volume'].iloc[-1]
            vol_avg = df['Volume'].mean()
            
            # Smart Order Block Signal Logic
            if close > df['High'].iloc[-2] and vol > vol_avg:
                signal = "BULLISH_OB"
                bullish_count += 1
            elif close < df['Low'].iloc[-2] and vol > vol_avg:
                signal = "BEARISH_OB"
                bearish_count += 1
            else:
                signal = "NEUTRAL"
                if pct_change >= 0:
                    bullish_count += 1
                else:
                    bearish_count += 1
                    
            results.append({
                "Symbol": symbol.replace(".NS", ""),
                "Price": close,
                "Change": pct_change,
                "Signal": signal,
                "Volume": vol
            })
        except Exception:
            continue
            
    return pd.DataFrame(results), bullish_count, bearish_count

df_market, bull_cnt, bear_cnt = scan_whole_market()

# 5. Live Glowing Order Block Dashboard Counters
c1, c2, c3, c4 = st.columns(4)
c1.markdown(f"<div class='glow-bullish'><div class='metric-title'>BULLISH ORDER BLOCKS</div><div class='metric-value-bull'>{bull_cnt}</div></div>", unsafe_allow_html=True)
c2.markdown(f"<div class='glow-bearish'><div class='metric-title'>BEARISH ORDER BLOCKS</div><div class='metric-value-bear'>{bear_cnt}</div></div>", unsafe_allow_html=True)
c3.markdown(f"<div class='glow-bullish'><div class='metric-title'>NET MARKET BIAS</div><div class='metric-value-bull'>{'BULLISH 🚀' if bull_cnt >= bear_cnt else 'BEARISH ⚠️'}</div></div>", unsafe_allow_html=True)
c4.markdown(f"<div class='glow-bullish'><div class='metric-title'>SCANNED STOCKS</div><div class='metric-value-bull'>{len(df_market)}</div></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 6. OrderBlock.com Style Flow Network Graph (Sankey Flow Chart)
if not df_market.empty:
    st.subheader("🌐 Whole Market Order Block Liquidity Flow")
    
    # Prepare Sankey Flow Data
    labels = ["Market Pool"] + list(df_market['Symbol']) + ["Bullish OB Pool", "Bearish OB Pool"]
    market_pool_idx = 0
    bull_pool_idx = len(labels) - 2
    bear_pool_idx = len(labels) - 1
    
    sources = []
    targets = []
    values = []
    link_colors = []
    
    for idx, row in df_market.iterrows():
        stock_node_idx = idx + 1
        
        # Source to Stock
        sources.append(market_pool_idx)
        targets.append(stock_node_idx)
        val = max(abs(row['Change']), 0.5)
        values.append(val)
        
        if row['Change'] >= 0:
            link_colors.append("rgba(0, 255, 135, 0.25)")
            # Stock to Bullish Pool
            sources.append(stock_node_idx)
            targets.append(bull_pool_idx)
            values.append(val)
            link_colors.append("rgba(0, 255, 135, 0.45)")
        else:
            link_colors.append("rgba(255, 23, 68, 0.25)")
            # Stock to Bearish Pool
            sources.append(stock_node_idx)
            targets.append(bear_pool_idx)
            values.append(val)
            link_colors.append("rgba(255, 23, 68, 0.45)")

    fig_sankey = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=18,
            line=dict(color="#000000", width=0.5),
            label=labels,
            color=["#3b82f6"] + ["#1e293b"]*len(df_market) + ["#00ff87", "#ff1744"]
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color=link_colors
        )
    )])
    
    fig_sankey.update_layout(
        template="plotly_dark",
        paper_bgcolor="#05070c",
        plot_bgcolor="#05070c",
        height=520,
        margin=dict(l=10, r=10, t=20, b=20)
    )
    
    st.plotly_chart(fig_sankey, use_container_width=True)

# 7. Real-Time Market Order Block Heatmap Table
st.subheader("🔥 Real-Time Order Block Scanner Table")
st.dataframe(
    df_market.style.format({"Price": "₹{:.2f}", "Change": "{:+.2f}%"}),
    use_container_width=True,
    height=300
)

# Auto-refresh every 20 seconds for live flow animation
time.sleep(20)
st.rerun()
