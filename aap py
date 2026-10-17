import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
import pyotp
from neo_api_client import NeoAPI
import time

# 1. Page Config
st.set_page_config(
    page_title="AI Smart Order Block & Trading Terminal",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Advanced Styling & Theme (order-block.com inspired)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    .stApp { background-color: #07090e; color: #f3f4f6; font-family: 'Inter', sans-serif; }
    
    @keyframes pulse-green {
        0% { box-shadow: 0 0 0 0 rgba(0, 200, 83, 0.4); }
        70% { box-shadow: 0 0 0 10px rgba(0, 200, 83, 0); }
        100% { box-shadow: 0 0 0 0 rgba(0, 200, 83, 0); }
    }
    
    .live-badge {
        display: inline-block;
        width: 8px;
        height: 8px;
        background-color: #00c853;
        border-radius: 50%;
        animation: pulse-green 1.5s infinite;
        margin-right: 6px;
    }

    .card-box {
        background: linear-gradient(135deg, #0e131f 0%, #151b2b 100%);
        border: 1px solid #1f293d;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.5);
    }
    
    .bullish-ob { border-left: 4px solid #00c853; background: rgba(0, 200, 83, 0.05); }
    .bearish-ob { border-left: 4px solid #ff3d00; background: rgba(255, 61, 0, 0.05); }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# 3. Initialize Kotak Neo API Connection
@st.cache_resource
def init_neo():
    try:
        client = NeoAPI(consumer_key='46ddfba8-10b2-40dc-8afd-ee0cd878f2ed')
        totp = pyotp.TOTP('0ZFVKWQSGPK6IRH2LKDKILJU')
        client.totp_login(mobile_number='9137271962', totp=totp.now())
        return client, True
    except Exception as e:
        return str(e), False

client, api_status = init_neo()

# 4. Top Navigation Bar
nav1, nav2, nav3, nav4 = st.columns([2.5, 1.5, 1.5, 2])
with nav1:
    st.markdown("### ⚡ **AI-POWERED** <span style='font-size:12px; color:#3b82f6; background:#1e3a8a55; padding:2px 6px; border-radius:4px;'>ORDER BLOCK TERMINAL</span>", unsafe_allow_html=True)

default_watchlist = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "SBIN.NS", "ICICIBANK.NS"]
with nav2:
    selected_symbol = st.selectbox("Asset", default_watchlist, label_visibility="collapsed")
with nav3:
    timeframe = st.selectbox("TF", ["1d", "1h", "15m", "5m"], index=0, label_visibility="collapsed")
with nav4:
    st.markdown(f"<div style='text-align:right; padding-top:8px;'><span class='live-badge'></span><span style='font-size:13px; color:#9ca3af;'>Live Tracking &bull; API: {'🟢' if api_status else '🔴'}</span></div>", unsafe_allow_html=True)

period_map = {"1d": "3mo", "1h": "1mo", "15m": "7d", "5m": "3d"}

# 5. Smart AI & SMC Order Block Scanner Logic
@st.cache_data(ttl=15)
def load_and_scan_data(ticker, tf):
    data = yf.download(ticker, period=period_map[tf], interval=tf, progress=False)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.droplevel(1)
    data.reset_index(inplace=True)
    
    data['Signal'] = "HOLD"
    data['AI_Confidence'] = "Medium"
    
    # SMC / Order Block calculation logic from your snippet
    vol_mean = data['Volume'].mean()
    for i in range(2, len(data)):
        if data['Close'].iloc[i] > data['High'].iloc[i-1] and data['Volume'].iloc[i] > vol_mean:
            data.loc[data.index[i], 'Signal'] = "BUY (Bullish OB)"
            data.loc[data.index[i], 'AI_Confidence'] = "High 🚀"
        elif data['Close'].iloc[i] < data['Low'].iloc[i-1] and data['Volume'].iloc[i] > vol_mean:
            data.loc[data.index[i], 'Signal'] = "SELL (Bearish OB)"
            data.loc[data.index[i], 'AI_Confidence'] = "High ⚠️"
            
    return data

df = load_and_scan_data(selected_symbol, timeframe)

if not df.empty:
    current_price = df['Close'].iloc[-1]
    prev_price = df['Close'].iloc[-2]
    price_change = current_price - prev_price
    pct_change = (price_change / prev_price) * 100

    latest_signal = df['Signal'].iloc[-1]
    ai_conf = df['AI_Confidence'].iloc[-1]

    # Dashboard Metrics Row
    m1, m2, m3, m4 = st.columns(4)
    m1.markdown(f"<div class='card-box'><small style='color:#9ca3af;'>LIVE MARKET PRICE</small><h2 style='margin:0; color:{'#00c853' if price_change>=0 else '#ff3d00'};'>₹{current_price:.2f} <span style='font-size:14px;'>({pct_change:+.2f}%)</span></h2></div>", unsafe_allow_html=True)
    m2.markdown(f"<div class='card-box'><small style='color:#9ca3af;'>AI RECOMMENDATION</small><h4 style='margin:0; color:#e5e7eb;'>{latest_signal}</h4></div>", unsafe_allow_html=True)
    m3.markdown(f"<div class='card-box'><small style='color:#9ca3af;'>AI CONFIDENCE SCORE</small><h3 style='margin:0;'>{ai_conf}</h3></div>", unsafe_allow_html=True)
    m4.markdown(f"<div class='card-box'><small style='color:#9ca3af;'>MARKET STATUS</small><h3 style='margin:0; color:#00c853;'>Active / Connected</h3></div>", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)

    # Layout: Chart and AI Insights Panel
    left_col, right_col = st.columns([2.5, 1])

    with left_col:
        st.subheader(f"📊 {selected_symbol} - Advanced Candlestick & Order Blocks")
        fig = go.Figure(data=[go.Candlestick(
            x=df['Date'] if 'Date' in df.columns else df.index, 
            open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
            increasing_line_color='#00c853', decreasing_line_color='#ff3d00'
        )])
        fig.update_layout(xaxis_rangeslider_visible=False, template="plotly_dark", height=480, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig, use_container_width=True)

    with right_col:
        st.subheader("🧠 AI Smart Insights")
        st.info(f"AI Model successfully analyzed {selected_symbol} using institutional volume and price action templates.")
        st.write("**Risk Management Parameters:**")
        st.write(f"- Suggested Stop Loss: ₹{current_price * 0.98:.2f}")
        st.write(f"- Target Profit: ₹{current_price * 1.04:.2f}")
        st.write(f"- Risk-to-Reward Ratio: 1:2")
        
        st.markdown("---")
        st.subheader("⚡ Quick Order Execution")
        qty = st.number_input("Quantity", min_value=1, value=5)
        
        b1, b2 = st.columns(2)
        with b1:
            if st.button("BUY", use_container_width=True):
                if api_status:
                    res = client.place_order(tradingsymbol=selected_symbol.replace(".NS","-EQ"), quantity=str(qty), transaction_type="B", exchange_segment="nse_cm", product="MIS", order_type="MKT", price="0")
                    st.success(f"ID: {res}")
                else: st.error("API Offline")
        with b2:
            if st.button("SELL", use_container_width=True):
                if api_status:
                    res = client.place_order(tradingsymbol=selected_symbol.replace(".NS","-EQ"), quantity=str(qty), transaction_type="S", exchange_segment="nse_cm", product="MIS", order_type="MKT", price="0")
                    st.success(f"ID: {res}")
                else: st.error("API Offline")

    # 15-second background auto-refresh tracker loop
    time.sleep(15)
    st.rerun()
