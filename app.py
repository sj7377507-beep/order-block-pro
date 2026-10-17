import streamlit as st
import pandas as pd
import yfinance as yf
import json
import streamlit.components.v1 as components

# 1. Page Configuration
st.set_page_config(
    page_title="OrderBlock.com Exact Flow Clone",
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

# 2. Live Market Data
@st.cache_data(ttl=20)
def fetch_exact_flow_data():
    left_symbols = ["TCS.NS", "RELIANCE.NS", "INFY.NS", "HDFCBANK.NS", "SBIN.NS", "ICICIBANK.NS", "AXISBANK.NS", "LT.NS"]
    right_symbols = ["EICHERMOT.NS", "M&M.NS", "FEDERALBNK.NS", "DRREDDY.NS", "NTPC.NS", "CANBK.NS", "SUZLON.NS", "DIVISLAB.NS"]
    
    symbols = list(set(left_symbols + right_symbols))
    try:
        data = yf.download(symbols, period="2d", interval="15m", group_by='ticker', progress=False)
    except Exception:
        data = pd.DataFrame()

    def parse_symbol(s):
        try:
            if not data.empty and s in data:
                df = data[s].dropna()
                c = float(df['Close'].iloc[-1])
                p = float(df['Close'].iloc[-2])
                pct = round(((c - p) / p) * 100, 2)
            else:
                c, pct = 2500.0, 1.45
        except Exception:
            c, pct = 2500.0, 0.85
        return {"name": s.replace(".NS", ""), "price": round(c, 2), "pct": pct}

    left_stocks = [parse_symbol(s) for s in left_symbols]
    right_stocks = [parse_symbol(s) for s in right_symbols]

    return left_stocks, right_stocks

left_data, right_data = fetch_exact_flow_data()
left_json = json.dumps(left_data)
right_json = json.dumps(right_data)

# 3. Exact HTML5 WebGL/Canvas Replication
html_code = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', sans-serif; user-select: none; }}
        body {{ background-color: #04060a; color: #d1d5db; overflow: hidden; padding: 5px; }}

        /* Top Header Navbar */
        .header {{
            display: flex; justify-content: space-between; align-items: center;
            background: rgba(13, 17, 26, 0.95); border: 1px solid rgba(255, 255, 255, 0.08);
            backdrop-filter: blur(12px); padding: 6px 12px; border-radius: 8px; margin-bottom: 6px;
        }}
        .brand {{ display: flex; align-items: center; gap: 6px; font-weight: 800; font-size: 13px; color: #ffffff; }}
        .live-dot {{ width: 7px; height: 7px; background-color: #00ff87; border-radius: 50%; box-shadow: 0 0 8px #00ff87; animation: pulse 1.5s infinite; }}
        @keyframes pulse {{ 0% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(0, 255, 135, 0.7); }} 70% {{ transform: scale(1); box-shadow: 0 0 0 6px rgba(0, 255, 135, 0); }} 100% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(0, 255, 135, 0); }} }}

        .tabs {{ display: flex; gap: 12px; font-size: 11px; font-weight: 700; }}
        .tab {{ color: #6b7280; cursor: pointer; padding: 2px 5px; border-radius: 4px; }}
        .tab.active {{ color: #00ff87; border-bottom: 2px solid #00ff87; text-shadow: 0 0 8px rgba(0, 255, 135, 0.5); }}

        .counters {{ display: flex; gap: 12px; font-size: 11px; font-weight: 800; }}
        .c-bull {{ color: #00ff87; text-shadow: 0 0 6px rgba(0,255,135,0.4); }}
        .c-bear {{ color: #ff1744; text-shadow: 0 0 6px rgba(255,23,68,0.4); }}

        /* Flow Container */
        .flow-container {{
            background: #060910; border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 10px; padding: 6px; position: relative; width: 100%; height: calc(100vh - 50px);
        }}

        canvas {{ width: 100%; height: 100%; display: block; border-radius: 6px; background: #030508; }}
    </style>
</head>
<body>

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
        <div class="counters">
            <span class="c-bull">▲ BULLISH 172</span>
            <span class="c-bear">▼ BEARISH 41</span>
        </div>
    </div>

    <div class="flow-container">
        <canvas id="flowCanvas"></canvas>
    </div>

    <script>
        const leftStocks = {left_json};
        const rightStocks = {right_json};

        const canvas = document.getElementById('flowCanvas');
        const ctx = canvas.getContext('2d');

        function resizeCanvas() {{
            canvas.width = canvas.offsetWidth;
            canvas.height = canvas.offsetHeight;
        }}
        resizeCanvas();
        window.addEventListener('resize', resizeCanvas);

        let offset = 0;

        function drawFullOrderBlockFlow() {{
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            const w = canvas.width;
            const h = canvas.height;

            const leftX = 110;
            const rightX = w - 120;
            const poolX1 = w * 0.52;
            const poolX2 = w * 0.65;
            const poolY1 = 80;
            const poolY2 = h - 80;

            // 1. Draw Blue Support/Resistance Level Lines
            ctx.strokeStyle = 'rgba(59, 130, 246, 0.35)';
            ctx.lineWidth = 1;
            [h * 0.35, h * 0.52, h * 0.72].forEach(y => {{
                ctx.beginPath();
                ctx.moveTo(leftX, y);
                ctx.lineTo(rightX, y);
                ctx.stroke();
            }});

            // 2. Draw Central Order Block Pool Container
            ctx.strokeStyle = 'rgba(0, 255, 135, 0.4)';
            ctx.lineWidth = 1.5;
            ctx.strokeRect(poolX1, poolY1, poolX2 - poolX1, poolY2 - poolY1);

            // Internal horizontal stacked lines inside Pool
            ctx.strokeStyle = 'rgba(0, 255, 135, 0.15)';
            ctx.lineWidth = 0.8;
            for (let y = poolY1 + 10; y < poolY2; y += 8) {{
                ctx.beginPath();
                ctx.moveTo(poolX1, y);
                ctx.lineTo(poolX2, y);
                ctx.stroke();
            }}

            // 3. Draw Left Stocks & Input Flow Curves
            const leftStep = (h - 60) / Math.max(leftStocks.length, 1);
            leftStocks.forEach((s, i) => {{
                const startY = 30 + i * leftStep;

                // Label
                ctx.fillStyle = s.pct >= 0 ? '#00ff87' : '#ff1744';
                ctx.font = 'bold 10px Inter';
                ctx.fillText(`${{s.name}} (${{s.pct >= 0 ? '+' : ''}}${{s.pct}}%)`, 10, startY + 4);

                // Multiple Wavy Trajectory Lines per Stock
                for (let k = 0; k < 3; k++) {{
                    const targetY = poolY1 + ((i * 3 + k) * (poolY2 - poolY1) / 24);
                    
                    ctx.beginPath();
                    ctx.strokeStyle = s.pct >= 0 ? `rgba(0, 255, 135, ${{0.15 + k * 0.1}})` : `rgba(255, 23, 68, ${{0.15 + k * 0.1}})`;
                    ctx.lineWidth = 1;

                    const cp1x = leftX + (poolX1 - leftX) * 0.4;
                    const cp1y = startY + Math.sin((offset + i + k) * 0.04) * 15;
                    const cp2x = leftX + (poolX1 - leftX) * 0.8;
                    const cp2y = targetY - Math.cos((offset + i + k) * 0.04) * 15;

                    ctx.moveTo(leftX, startY);
                    ctx.bezierCurveTo(cp1x, cp1y, cp2x, cp2y, poolX1, targetY);
                    ctx.stroke();
                }}
            }});

            // 4. Draw Outflow Lines & Right Stocks
            const rightStep = (h - 60) / Math.max(rightStocks.length, 1);
            rightStocks.forEach((s, i) => {{
                const endY = 30 + i * rightStep;
                const poolTargetY = poolY1 + (i * (poolY2 - poolY1) / Math.max(rightStocks.length, 1));

                // Lines from Pool to Right Node
                ctx.beginPath();
                ctx.strokeStyle = s.pct >= 0 ? 'rgba(0, 255, 135, 0.25)' : 'rgba(255, 23, 68, 0.25)';
                ctx.lineWidth = 1.2;

                const cp1x = poolX2 + (rightX - poolX2) * 0.3;
                const cp1y = poolTargetY;
                const cp2x = poolX2 + (rightX - poolX2) * 0.7;
                const cp2y = endY;

                ctx.moveTo(poolX2, poolTargetY);
                ctx.bezierCurveTo(cp1x, cp1y, cp2x, cp2y, rightX, endY);
                ctx.stroke();

                // Right Label
                ctx.fillStyle = s.pct >= 0 ? '#00ff87' : '#ff1744';
                ctx.font = 'bold 10px Inter';
                ctx.fillText(`${{s.name}} (${{s.pct >= 0 ? '+' : ''}}${{s.pct}}%)`, rightX + 8, endY + 4);
            }});

            // 5. Moving Particle Animation
            for (let p = 0; p < 12; p++) {{
                let progress = ((offset * 0.8 + p * 15) % 100) / 100;
                let px = leftX + progress * (poolX1 - leftX);
                let py = (h / 2) - (progress * (h / 3)) + Math.sin(progress * 4) * 10;

                ctx.beginPath();
                ctx.fillStyle = '#00ff87';
                ctx.arc(px, py, 2, 0, Math.PI * 2);
                ctx.fill();
            }}

            offset += 0.8;
            requestAnimationFrame(drawFullOrderBlockFlow);
        }}

        drawFullOrderBlockFlow();
    </script>
</body>
</html>
"""

components.html(html_code, height=750, scrolling=False)
