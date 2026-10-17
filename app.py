import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import requests
import io
import time
import json
from datetime import datetime
import streamlit.components.v1 as components

# =====================================================
# JARVES TRADING + ORDER BLOCK VISUAL TERMINAL
# =====================================================

st.set_page_config(
    page_title="Jarves Order Block Flow Terminal",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container { padding: 0rem !important; max-width: 100% !important; }
    .stApp { background-color: #030508; color: #e5e7eb; }
</style>
""", unsafe_allow_html=True)

# NSE List Loader
NSE_LIST_URL = "https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv"

@st.cache_data(ttl=3600, show_spinner=False)
def load_nse_symbols():
    headers = {"User-Agent": "Mozilla/5.0", "Accept": "text/csv,*/*", "Referer": "https://www.nseindia.com/"}
    try:
        response = requests.get(NSE_LIST_URL, headers=headers, timeout=10)
        response.raise_for_status()
        df = pd.read_csv(io.BytesIO(response.content))
        df.columns = [c.strip().upper() for c in df.columns]
        if "SERIES" in df.columns:
            df = df[df["SERIES"].astype(str).str.strip() == "EQ"]
        symbols = df["SYMBOL"].dropna().astype(str).str.strip().drop_duplicates().tolist()
        return sorted([s + ".NS" for s in symbols if s])
    except Exception:
        return ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "SBIN.NS", "ICICIBANK.NS", "AXISBANK.NS", "M&M.NS"]

@st.cache_data(ttl=30, show_spinner=False)
def fetch_market_flow_data():
    symbols = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "SBIN.NS", "ICICIBANK.NS", "AXISBANK.NS", "M&M.NS", "FEDERALBNK.NS", "DRREDDY.NS", "NTPC.NS", "SUZLON.NS", "DIVISLAB.NS", "PAYTM.NS", "BHARTIARTL.NS", "EICHERMOT.NS"]
    
    try:
        data = yf.download(symbols, period="2d", interval="15m", group_by='ticker', progress=False)
    except Exception:
        data = pd.DataFrame()

    results = []
    for s in symbols:
        try:
            if not data.empty and s in data:
                df = data[s].dropna()
                c = float(df['Close'].iloc[-1])
                p = float(df['Close'].iloc[-2])
                pct = round(((c - p) / p) * 100, 2)
                v = int(df['Volume'].iloc[-1])
            else:
                c, pct, v = 1500.0, 0.8, 10000

            setup = "LONG BUILD-UP" if pct > 0.5 else ("ACCUMULATION" if pct >= 0 else ("SHORT BUILD-UP" if pct < -0.5 else "LONG UNWINDING"))
            results.append({
                "name": s.replace(".NS", ""),
                "price": round(c, 2),
                "pct": pct,
                "setup": setup,
                "volume": v
            })
        except Exception:
            continue
            
    return sorted(results, key=lambda x: x['pct'], reverse=True)

stocks_data = fetch_market_flow_data()
bulls_cnt = len([s for s in stocks_data if s['pct'] >= 0])
bears_cnt = len([s for s in stocks_data if s['pct'] < 0])
stocks_json = json.dumps(stocks_data)

# Visual Canvas Renderer
html_code = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', sans-serif; user-select: none; }}
        body {{ background-color: #04060a; color: #d1d5db; overflow-x: hidden; padding: 8px; }}

        .header {{
            display: flex; justify-content: space-between; align-items: center;
            background: rgba(13, 17, 26, 0.9); border: 1px solid rgba(255, 255, 255, 0.08);
            padding: 8px 14px; border-radius: 10px; margin-bottom: 10px;
        }}
        .brand {{ display: flex; align-items: center; gap: 8px; font-weight: 800; font-size: 14px; color: #ffffff; }}
        .live-dot {{ width: 8px; height: 8px; background-color: #00ff87; border-radius: 50%; box-shadow: 0 0 10px #00ff87; animation: pulse 1.5s infinite; }}
        @keyframes pulse {{ 0% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(0, 255, 135, 0.7); }} 70% {{ transform: scale(1); box-shadow: 0 0 0 8px rgba(0, 255, 135, 0); }} 100% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(0, 255, 135, 0); }} }}

        .tabs {{ display: flex; gap: 14px; font-size: 11px; font-weight: 700; }}
        .tab {{ color: #6b7280; cursor: pointer; padding: 4px 6px; border-radius: 4px; }}
        .tab.active {{ color: #00ff87; background: rgba(0, 255, 135, 0.08); border-bottom: 2px solid #00ff87; }}

        .flow-container {{
            background: #060910; border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 12px; padding: 12px; position: relative; margin-bottom: 15px;
        }}
        .flow-header {{ display: flex; justify-content: space-between; font-size: 11px; font-weight: 700; color: #9ca3af; margin-bottom: 8px; }}

        canvas {{ width: 100%; height: 380px; display: block; border-radius: 8px; background: radial-gradient(circle at center, #080d18 0%, #030509 100%); }}

        .section-title {{ font-size: 11px; font-weight: 800; color: #00ff87; margin: 12px 0 8px 0; letter-spacing: 1px; }}
        .grid-container {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; margin-bottom: 15px; }}

        .c-card {{
            background: rgba(10, 15, 26, 0.85); border: 1px solid rgba(0, 255, 135, 0.3);
            border-radius: 8px; padding: 10px; position: relative; overflow: hidden;
        }}
        .c-card.bear {{ border-color: rgba(255, 23, 68, 0.3); }}
        .c-card::before {{ content: ''; position: absolute; top: 0; left: 0; width: 3px; height: 100%; background: #00ff87; }}
        .c-card.bear::before {{ background: #ff1744; }}

        .c-header {{ display: flex; justify-content: space-between; align-items: center; }}
        .c-name {{ font-size: 12px; font-weight: 800; color: #ffffff; }}
        .c-pct {{ font-size: 11px; font-weight: 700; color: #00ff87; }}
        .c-card.bear .c-pct {{ color: #ff1744; }}
        .c-price {{ font-size: 13px; font-weight: 700; color: #d1d5db; margin: 4px 0 2px 0; }}
        .c-status {{ font-size: 9px; color: #9ca3af; font-weight: 600; }}
        .c-bars {{ display: flex; gap: 2px; margin-top: 8px; }}
        .bar {{ height: 4px; flex: 1; background: #00ff87; border-radius: 1px; opacity: 0.8; }}
        .c-card.bear .bar {{ background: #ff1744; }}
    </style>
</head>
<body>

    <div class="header">
        <div class="brand">
            <span>JARVES ORDER BLOCK</span>
            <div class="live-dot"></div>
        </div>
        <div class="tabs">
            <div class="tab active">FLOW</div>
            <div class="tab" style="color:#00ff87;">▲ TOP</div>
            <div class="tab" style="color:#ff1744;">▼ TOP</div>
        </div>
    </div>

    <div class="flow-container">
        <div class="flow-header">
            <span>FLOW &bull; LIVE WHOLE MARKET ORDER BLOCKS</span>
            <span style="color:#00ff87;">▲ BULLISH: {bulls_cnt} &nbsp; <span style="color:#ff1744;">▼ BEARISH: {bears_cnt}</span></span>
        </div>
        <canvas id="flowCanvas"></canvas>
    </div>

    <div class="section-title">▲ BULLISH & BEARISH CONTENDERS (LIVE NSE DATA)</div>
    <div class="grid-container" id="grid"></div>

    <script>
        const stocks = {stocks_json};
        document.getElementById('grid').innerHTML = stocks.map(s => `
            <div class="c-card ${{s.pct < 0 ? 'bear' : ''}}">
                <div class="c-header">
                    <span class="c-name">${{s.name}}</span>
                    <span class="c-pct">${{s.pct >= 0 ? '+' : ''}}${{s.pct}}%</span>
                </div>
                <div class="c-price">₹${{s.price}}</div>
                <div class="c-status">${{s.setup}}</div>
                <div class="c-bars">
                    <div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div>
                </div>
            </div>
        `).join('');

        const canvas = document.getElementById('flowCanvas');
        const ctx = canvas.getContext('2d');

        function resizeCanvas() {{ canvas.width = canvas.offsetWidth; canvas.height = canvas.offsetHeight; }}
        resizeCanvas();
        window.addEventListener('resize', resizeCanvas);

        let offset = 0;
        function drawAnimatedFlow() {{
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            const w = canvas.width;
            const h = canvas.height;
            const centerY = h / 2;

            ctx.beginPath();
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)';
            ctx.lineWidth = 1;
            ctx.setLineDash([4, 4]);
            ctx.moveTo(0, centerY);
            ctx.lineTo(w, centerY);
            ctx.stroke();
            ctx.setLineDash([]);

            const bulls = stocks.filter(s => s.pct >= 0);
            const bears = stocks.filter(s => s.pct < 0);

            bulls.forEach((s, i) => {{
                const endY = 20 + (i * (centerY - 25) / Math.max(bulls.length, 1));
                ctx.beginPath();
                ctx.strokeStyle = `rgba(0, 255, 135, ${{0.25 + (i % 3) * 0.25}})`;
                ctx.lineWidth = 1.5;
                ctx.moveTo(15, centerY);
                ctx.bezierCurveTo(w * 0.3, centerY - (i * 2), w * 0.7, endY, w - 120, endY);
                ctx.stroke();

                ctx.fillStyle = '#00ff87';
                ctx.font = 'bold 10px Inter';
                ctx.fillText(`${{s.name}} (${{s.pct >= 0 ? '+' : ''}}${{s.pct}}%)`, w - 110, endY + 3);
            }});

            bears.forEach((s, i) => {{
                const endY = h - 20 - (i * (centerY - 25) / Math.max(bears.length, 1));
                ctx.beginPath();
                ctx.strokeStyle = `rgba(255, 23, 68, ${{0.25 + (i % 3) * 0.25}})`;
                ctx.lineWidth = 1.5;
                ctx.moveTo(15, centerY);
                ctx.bezierCurveTo(w * 0.3, centerY + (i * 2), w * 0.7, endY, w - 120, endY);
                ctx.stroke();

                ctx.fillStyle = '#ff1744';
                ctx.font = 'bold 10px Inter';
                ctx.fillText(`${{s.name}} (${{s.pct}}%)`, w - 110, endY + 3);
            }});

            offset += 0.8;
            requestAnimationFrame(drawAnimatedFlow);
        }}
        drawAnimatedFlow();
    </script>
</body>
</html>
"""

components.html(html_code, height=850, scrolling=True)
                
