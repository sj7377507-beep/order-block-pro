import streamlit as st
import pandas as pd
import yfinance as yf
import json
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Order Block Terminal Pro",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container { padding: 0rem !important; max-width: 100% !important; }
    .stApp { background-color: #030508; }
</style>
""", unsafe_allow_html=True)

# Fetch Live NSE Market Data
@st.cache_data(ttl=20)
def fetch_live_data():
    symbols = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "SBIN.NS", 
               "ICICIBANK.NS", "AXISBANK.NS", "M&M.NS", "FEDERALBNK.NS", "DRREDDY.NS",
               "NTPC.NS", "CANBK.NS", "SUZLON.NS", "DIVISLAB.NS", "PAYTM.NS", "BHARTIARTL.NS"]
    
    data = yf.download(symbols, period="2d", interval="15m", group_by='ticker', progress=False)
    stock_list = []
    
    for s in symbols:
        try:
            df = data[s].dropna()
            if not df.empty:
                c = df['Close'].iloc[-1]
                p = df['Close'].iloc[-2]
                pct = ((c - p) / p) * 100
                v = df['Volume'].iloc[-1]
                
                if pct > 0.5:
                    setup = "LONG BUILD-UP"
                elif pct > 0:
                    setup = "ACCUMULATION"
                elif pct < -0.5:
                    setup = "SHORT BUILD-UP"
                else:
                    setup = "LONG UNWINDING"
                    
                stock_list.append({
                    "name": s.replace(".NS", ""),
                    "price": round(float(c), 2),
                    "pct": round(float(pct), 2),
                    "setup": setup,
                    "volume": int(v)
                })
        except Exception:
            continue
            
    stock_list = sorted(stock_list, key=lambda x: x['pct'], reverse=True)
    return stock_list

live_stocks = fetch_live_data()
bulls_cnt = len([s for s in live_stocks if s['pct'] >= 0])
bears_cnt = len([s for s in live_stocks if s['pct'] < 0])

stocks_json = json.dumps(live_stocks)

# Inject Clean High-Graphics Canvas UI (Without Unlock Button)
html_code = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', sans-serif; user-select: none; }}
        body {{ background-color: #04060a; color: #d1d5db; overflow-x: hidden; padding: 10px; }}

        /* Top Header */
        .header {{
            display: flex; justify-content: space-between; align-items: center;
            background: rgba(13, 17, 26, 0.85); border: 1px solid rgba(255, 255, 255, 0.08);
            backdrop-filter: blur(12px); padding: 10px 16px; border-radius: 12px; margin-bottom: 12px;
        }}
        .brand {{ display: flex; align-items: center; gap: 8px; font-weight: 800; font-size: 15px; color: #ffffff; }}
        .live-dot {{ width: 8px; height: 8px; background-color: #00ff87; border-radius: 50%; box-shadow: 0 0 10px #00ff87; animation: pulse 1.5s infinite; }}
        @keyframes pulse {{ 0% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(0, 255, 135, 0.7); }} 70% {{ transform: scale(1); box-shadow: 0 0 0 8px rgba(0, 255, 135, 0); }} 100% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(0, 255, 135, 0); }} }}

        .tabs {{ display: flex; gap: 18px; font-size: 12px; font-weight: 700; letter-spacing: 0.5px; }}
        .tab {{ color: #6b7280; cursor: pointer; }}
        .tab.active {{ color: #00ff87; border-bottom: 2px solid #00ff87; text-shadow: 0 0 8px rgba(0, 255, 135, 0.5); }}

        /* Flow Chart Container */
        .flow-container {{
            background: #060910; border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 12px; padding: 12px; position: relative; margin-bottom: 15px;
        }}
        .flow-header {{ display: flex; justify-content: space-between; font-size: 11px; font-weight: 700; color: #9ca3af; margin-bottom: 8px; }}

        canvas {{ width: 100%; height: 420px; display: block; border-radius: 8px; background: radial-gradient(circle at center, #080d18 0%, #030509 100%); }}

        /* Contenders Section */
        .section-title {{ font-size: 11px; font-weight: 800; color: #00ff87; margin-bottom: 10px; letter-spacing: 1px; }}
        .grid-container {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 10px; margin-bottom: 15px; }}

        .c-card {{
            background: rgba(10, 15, 26, 0.85); border: 1px solid rgba(0, 255, 135, 0.3);
            border-radius: 8px; padding: 10px; position: relative; overflow: hidden;
            box-shadow: 0 0 10px rgba(0, 255, 135, 0.08);
        }}
        .c-card.bear {{ border-color: rgba(255, 23, 68, 0.3); box-shadow: 0 0 10px rgba(255, 23, 68, 0.08); }}
        .c-card::before {{ content: ''; position: absolute; top: 0; left: 0; width: 3px; height: 100%; background: #00ff87; }}
        .c-card.bear::before {{ background: #ff1744; }}

        .c-header {{ display: flex; justify-content: space-between; align-items: center; }}
        .c-name {{ font-size: 12px; font-weight: 800; color: #ffffff; }}
        .c-pct {{ font-size: 11px; font-weight: 700; color: #00ff87; }}
        .c-card.bear .c-pct {{ color: #ff1744; }}
        
        .c-price {{ font-size: 13px; font-weight: 700; color: #d1d5db; margin: 4px 0 2px 0; }}
        .c-status {{ font-size: 9px; color: #9ca3af; font-weight: 600; letter-spacing: 0.5px; }}

        .c-bars {{ display: flex; gap: 2px; margin-top: 8px; }}
        .bar {{ height: 4px; flex: 1; background: #00ff87; border-radius: 1px; opacity: 0.8; box-shadow: 0 0 4px #00ff87; }}
        .c-card.bear .bar {{ background: #ff1744; box-shadow: 0 0 4px #ff1744; }}
    </style>
</head>
<body>

    <!-- Header (Clean without Unlock) -->
    <div class="header">
        <div class="brand">
            <span>Order Block</span>
            <div class="live-dot"></div>
        </div>
        <div class="tabs">
            <div class="tab">MARKET</div>
            <div class="tab active">FLOW</div>
            <div class="tab" style="color:#00ff87;">▲ TOP</div>
            <div class="tab" style="color:#ff1744;">▼ TOP</div>
        </div>
    </div>

    <!-- Canvas -->
    <div class="flow-container">
        <div class="flow-header">
            <span>FLOW &bull; LIVE WHOLE MARKET ORDER BLOCKS</span>
            <span style="color:#00ff87;">▲ BULLISH: {bulls_cnt} &nbsp; <span style="color:#ff1744;">▼ BEARISH: {bears_cnt}</span></span>
        </div>
        <canvas id="flowCanvas"></canvas>
    </div>

    <!-- Live Stock Grid -->
    <div class="section-title">▲ BULLISH & BEARISH CONTENDERS (LIVE DATA)</div>
    <div class="grid-container" id="stockGrid"></div>

    <script>
        const stocks = {stocks_json};
        
        const grid = document.getElementById('stockGrid');
        grid.innerHTML = stocks.map(s => `
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

        function resizeCanvas() {{
            canvas.width = canvas.offsetWidth;
            canvas.height = canvas.offsetHeight;
        }}
        resizeCanvas();
        window.addEventListener('resize', resizeCanvas);

        let offset = 0;

        function drawAnimatedFlow() {{
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            const w = canvas.width;
            const h = canvas.height;
            const centerY = h / 2;

            ctx.beginPath();
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.3)';
            ctx.lineWidth = 1;
            ctx.setLineDash([4, 4]);
            ctx.moveTo(0, centerY);
            ctx.lineTo(w, centerY);
            ctx.stroke();
            ctx.setLineDash([]);

            const bulls = stocks.filter(s => s.pct >= 0);
            const bears = stocks.filter(s => s.pct < 0);

            bulls.forEach((s, i) => {{
                const endY = 25 + (i * (centerY - 30) / Math.max(bulls.length, 1));
                ctx.beginPath();
                ctx.strokeStyle = `rgba(0, 255, 135, ${{0.25 + (i % 3) * 0.25}})`;
                ctx.lineWidth = 1.5;

                const cp1x = w * 0.3;
                const cp1y = centerY - (i * 2) - Math.sin((offset + i) * 0.05) * 10;
                const cp2x = w * 0.7;
                const cp2y = endY + Math.cos((offset + i) * 0.05) * 10;

                ctx.moveTo(20, centerY);
                ctx.bezierCurveTo(cp1x, cp1y, cp2x, cp2y, w - 120, endY);
                ctx.stroke();

                ctx.fillStyle = '#00ff87';
                ctx.font = 'bold 10px Inter';
                ctx.fillText(`${{s.name}} (${{s.pct >= 0 ? '+' : ''}}${{s.pct}}%)`, w - 110, endY + 3);
            }});

            bears.forEach((s, i) => {{
                const endY = h - 25 - (i * (centerY - 30) / Math.max(bears.length, 1));
                ctx.beginPath();
                ctx.strokeStyle = `rgba(255, 23, 68, ${{0.25 + (i % 3) * 0.25}})`;
                ctx.lineWidth = 1.5;

                const cp1x = w * 0.3;
                const cp1y = centerY + (i * 2) + Math.sin((offset + i) * 0.05) * 10;
                const cp2x = w * 0.7;
                const cp2y = endY - Math.cos((offset + i) * 0.05) * 10;

                ctx.moveTo(20, centerY);
                ctx.bezierCurveTo(cp1x, cp1y, cp2x, cp2y, w - 120, endY);
                ctx.stroke();

                ctx.fillStyle = '#ff1744';
                ctx.font = 'bold 10px Inter';
                ctx.fillText(`${{s.name}} (${{s.pct}}%)`, w - 110, endY + 3);
            }});

            for (let p = 0; p < 8; p++) {{
                let progress = ((offset * 0.7 + p * 20) % 100) / 100;
                let px = 20 + progress * (w - 140);
                let pyBull = centerY - (progress * (centerY - 35));
                let pyBear = centerY + (progress * (centerY - 35));

                ctx.beginPath();
                ctx.fillStyle = '#00ff87';
                ctx.arc(px, pyBull, 3, 0, Math.PI * 2);
                ctx.fill();

                ctx.beginPath();
                ctx.fillStyle = '#ff1744';
                ctx.arc(px, pyBear, 3, 0, Math.PI * 2);
                ctx.fill();
            }}

            offset += 0.8;
            requestAnimationFrame(drawAnimatedFlow);
        }}

        drawAnimatedFlow();
    </script>
</body>
</html>
"""

components.html(html_code, height=850, scrolling=True)
