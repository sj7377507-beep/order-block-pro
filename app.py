import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Order Block Terminal Pro",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Hide Streamlit default UI elements
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {
        padding: 0rem !important;
        max-width: 100% !important;
    }
    .stApp {
        background-color: #030508;
    }
</style>
""", unsafe_allow_html=True)

# Exact High-Graphics OrderBlock UI Replica Component
html_code = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Inter', sans-serif;
            user-select: none;
        }

        body {
            background-color: #04060a;
            color: #d1d5db;
            overflow-x: hidden;
            padding: 10px;
        }

        /* Header Navbar */
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: rgba(13, 17, 26, 0.8);
            border: 1px solid rgba(255, 255, 255, 0.08);
            backdrop-filter: blur(12px);
            padding: 10px 16px;
            border-radius: 12px;
            margin-bottom: 12px;
        }

        .brand {
            display: flex;
            align-items: center;
            gap: 8px;
            font-weight: 800;
            font-size: 15px;
            color: #ffffff;
        }

        .live-dot {
            width: 8px;
            height: 8px;
            background-color: #00ff87;
            border-radius: 50%;
            box-shadow: 0 0 10px #00ff87;
            animation: pulse 1.5s infinite;
        }

        @keyframes pulse {
            0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(0, 255, 135, 0.7); }
            70% { transform: scale(1); box-shadow: 0 0 0 8px rgba(0, 255, 135, 0); }
            100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(0, 255, 135, 0); }
        }

        .tabs {
            display: flex;
            gap: 16px;
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 0.5px;
        }

        .tab {
            color: #6b7280;
            cursor: pointer;
            padding-bottom: 2px;
            transition: all 0.2s;
        }

        .tab.active {
            color: #00ff87;
            border-bottom: 2px solid #00ff87;
            text-shadow: 0 0 8px rgba(0, 255, 135, 0.5);
        }

        .unlock-btn {
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            color: #fff;
            padding: 6px 14px;
            border-radius: 8px;
            font-size: 11px;
            font-weight: 700;
            box-shadow: 0 0 12px rgba(99, 102, 241, 0.4);
        }

        /* Flow Canvas Section */
        .flow-container {
            background: #060910;
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            padding: 12px;
            position: relative;
            margin-bottom: 15px;
        }

        .flow-header {
            display: flex;
            justify-content: space-between;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.5px;
            color: #9ca3af;
            margin-bottom: 8px;
        }

        canvas {
            width: 100%;
            height: 380px;
            display: block;
            border-radius: 8px;
            background: radial-gradient(circle at center, #090e18 0%, #030509 100%);
        }

        /* Contenders Grid */
        .section-title {
            font-size: 11px;
            font-weight: 800;
            color: #00ff87;
            margin-bottom: 10px;
            letter-spacing: 1px;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .contenders-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 10px;
            margin-bottom: 15px;
        }

        .c-card {
            background: rgba(10, 15, 26, 0.7);
            border: 1px solid rgba(0, 255, 135, 0.25);
            border-radius: 8px;
            padding: 10px;
            position: relative;
            overflow: hidden;
            box-shadow: 0 0 10px rgba(0, 255, 135, 0.05);
        }

        .c-card::before {
            content: '';
            position: absolute;
            top: 0; left: 0; width: 3px; height: 100%;
            background: #00ff87;
            box-shadow: 0 0 8px #00ff87;
        }

        .c-name {
            font-size: 11px;
            font-weight: 700;
            color: #ffffff;
        }

        .c-status {
            font-size: 9px;
            color: #00ff87;
            font-weight: 600;
            margin-top: 2px;
        }

        .c-bars {
            display: flex;
            gap: 2px;
            margin-top: 8px;
        }

        .bar {
            height: 4px;
            flex: 1;
            background: #00ff87;
            border-radius: 1px;
            opacity: 0.8;
            box-shadow: 0 0 4px #00ff87;
        }
    </style>
</head>
<body>

    <!-- Header Navigation -->
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
        <div class="unlock-btn">Unlock</div>
    </div>

    <!-- Flow Dynamic Canvas Chart -->
    <div class="flow-container">
        <div class="flow-header">
            <span>FLOW &bull; LIQUIDITY POOL SCANNER</span>
            <span style="color:#00ff87;">▲ TOP: 172 &nbsp; <span style="color:#ff1744;">▼ TOP: 41</span></span>
        </div>
        <canvas id="flowCanvas"></canvas>
    </div>

    <!-- Bullish Contenders Section -->
    <div class="section-title">
        ▲ BULLISH CONTENDERS
    </div>

    <div class="contenders-grid">
        <div class="c-card">
            <div class="c-name">RELIANCE</div>
            <div class="c-status">LONG BUILD-UP</div>
            <div class="c-bars">
                <div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div>
            </div>
        </div>
        <div class="c-card">
            <div class="c-name">TCS</div>
            <div class="c-status">ACCUMULATION</div>
            <div class="c-bars">
                <div class="bar"></div><div class="bar"></div><div class="bar"></div>
            </div>
        </div>
        <div class="c-card">
            <div class="c-name">HDFCBANK</div>
            <div class="c-status">ORDER BLOCK</div>
            <div class="c-bars">
                <div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div>
            </div>
        </div>
        <div class="c-card">
            <div class="c-name">ICICIBANK</div>
            <div class="c-status">BREAKOUT</div>
            <div class="c-bars">
                <div class="bar"></div><div class="bar"></div><div class="bar"></div>
            </div>
        </div>
    </div>

    <script>
        const canvas = document.getElementById('flowCanvas');
        const ctx = canvas.getContext('2d');

        function resizeCanvas() {
            canvas.width = canvas.offsetWidth;
            canvas.height = canvas.offsetHeight;
        }
        resizeCanvas();
        window.addEventListener('resize', resizeCanvas);

        let offset = 0;

        function drawAnimatedFlow() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            const w = canvas.width;
            const h = canvas.height;
            const centerY = h / 2;

            // Center Horizontal Glow Line
            ctx.beginPath();
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.4)';
            ctx.lineWidth = 1.5;
            ctx.setLineDash([4, 4]);
            ctx.moveTo(0, centerY);
            ctx.lineTo(w, centerY);
            ctx.stroke();
            ctx.setLineDash([]);

            // Draw Dynamic Bullish Lines (Green)
            for (let i = 0; i < 22; i++) {
                ctx.beginPath();
                ctx.strokeStyle = `rgba(0, 255, 135, ${0.15 + (i % 5) * 0.15})`;
                ctx.lineWidth = 1.2;

                const startY = centerY;
                const endY = 30 + (i * 7);
                const cp1x = w * 0.25;
                const cp1y = centerY - (i * 2) - Math.sin((offset + i) * 0.05) * 15;
                const cp2x = w * 0.75;
                const cp2y = endY + Math.cos((offset + i) * 0.05) * 15;

                ctx.moveTo(30, startY);
                ctx.bezierCurveTo(cp1x, cp1y, cp2x, cp2y, w - 40, endY);
                ctx.stroke();
            }

            // Draw Dynamic Bearish Lines (Red)
            for (let i = 0; i < 22; i++) {
                ctx.beginPath();
                ctx.strokeStyle = `rgba(255, 23, 68, ${0.15 + (i % 5) * 0.15})`;
                ctx.lineWidth = 1.2;

                const startY = centerY;
                const endY = h - 30 - (i * 7);
                const cp1x = w * 0.25;
                const cp1y = centerY + (i * 2) + Math.sin((offset + i) * 0.05) * 15;
                const cp2x = w * 0.75;
                const cp2y = endY - Math.cos((offset + i) * 0.05) * 15;

                ctx.moveTo(30, startY);
                ctx.bezierCurveTo(cp1x, cp1y, cp2x, cp2y, w - 40, endY);
                ctx.stroke();
            }

            // Moving Glowing Particles
            for (let p = 0; p < 12; p++) {
                let progress = ((offset * 0.8 + p * 30) % 100) / 100;
                let px = 30 + progress * (w - 70);
                let pyBull = centerY - (progress * (centerY - 40)) + Math.sin(progress * 5) * 10;
                let pyBear = centerY + (progress * (centerY - 40)) - Math.sin(progress * 5) * 10;

                // Green particle
                ctx.beginPath();
                ctx.fillStyle = '#00ff87';
                ctx.arc(px, pyBull, 2.5, 0, Math.PI * 2);
                ctx.fill();

                // Red particle
                ctx.beginPath();
                ctx.fillStyle = '#ff1744';
                ctx.arc(px, pyBear, 2.5, 0, Math.PI * 2);
                ctx.fill();
            }

            offset += 0.8;
            requestAnimationFrame(drawAnimatedFlow);
        }

        drawAnimatedFlow();
    </script>
</body>
</html>
"""

# Render full screen canvas application inside Streamlit
components.html(html_code, height=720, scrolling=True)
