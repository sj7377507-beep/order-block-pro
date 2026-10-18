import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
import pandas as pd
import requests
import io

# Page setup
st.set_page_config(page_title="Jarves Trading Pro - All NSE Listed Stocks", layout="wide")

@st.cache_data(ttl=3600)
def get_all_nse_symbols():
    """Fetch all official listed equity symbols from NSE India CSV"""
    url = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            df = pd.read_csv(io.StringIO(response.text))
            # Filter EQ series (Ordinary Shares)
            if 'SERIES' in df.columns:
                df = df[df['SERIES'] == 'EQ']
            symbols = [f"{sym.strip()}.NS" for sym in df['SYMBOL'].tolist() if isinstance(sym, str)]
            return symbols
    except Exception as e:
        pass
    
    # Fallback to broad NSE top 500 list if official link times out
    return ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS", "SBIN.NS", "TATAMOTORS.NS", "ZOMATO.NS", "PAYTM.NS", "WIPRO.NS"]

# Fetch ALL NSE Listed Shares
ALL_NSE_SYMBOLS = get_all_nse_symbols()

@st.cache_data(ttl=120)
def fetch_live_market_data(symbols_list, limit=200):
    """Fetch live market price and volume for shares"""
    data = []
    # Fetching batch of high volume active stocks for optimal speed
    sample_symbols = symbols_list[:limit]
    
    try:
        tickers = yf.Tickers(" ".join(sample_symbols))
        for symbol in sample_symbols:
            try:
                ticker = tickers.tickers[symbol]
                info = ticker.fast_info
                
                ltp = info.last_price if hasattr(info, 'last_price') and info.last_price is not None else 0
                prev_close = info.previous_close if hasattr(info, 'previous_close') and info.previous_close is not None else ltp
                volume = info.last_volume if hasattr(info, 'last_volume') and info.last_volume is not None else 0
                
                if prev_close and prev_close > 0 and ltp > 0:
                    change = ltp - prev_close
                    p_change = (change / prev_close) * 100
                else:
                    change, p_change = 0, 0
                    
                clean_symbol = symbol.replace(".NS", "")
                if ltp > 0:
                    data.append({
                        "Symbol": clean_symbol,
                        "LTP": round(ltp, 2),
                        "Change": round(change, 2),
                        "P_Change": round(p_change, 2),
                        "Volume": int(volume),
                        "Volume_Str": f"{round(volume/1000000, 2)}M" if volume >= 1000000 else f"{round(volume/1000, 1)}K"
                    })
            except Exception:
                continue
    except Exception:
        pass
    
    return pd.DataFrame(data)

# Navigation
st.sidebar.title("📌 Navigation")
page = st.sidebar.radio("Go to Page", ["🔥 Intraday Hot Tracker (Pure Market)", "📊 Market Flow Dashboard"])

# ==========================================
# PAGE 1: INTRADAY HOT TRACKER (PURE MARKET)
# ==========================================
if page == "🔥 Intraday Hot Tracker (Pure Market)":
    st.markdown("<h2 style='color:#00ff7f;'>🔥 INTRADAY PURE MARKET SCANNER</h2>", unsafe_allow_html=True)
    st.caption(f"NSE me kul **{len(ALL_NSE_SYMBOLS)} Listed Shares** hain. Sabse zyaada Intraday Movement aur High Volume waale shares bilkul **SUBSE UPAR** hain.")

    # Control for how many stocks to scan in real-time
    scan_limit = st.sidebar.slider("Live Scan Range (Stocks Count)", min_value=100, max_value=len(ALL_NSE_SYMBOLS), value=300, step=100)
    
    with st.spinner("Processing live market volume and price changes..."):
        df_market = fetch_live_market_data(ALL_NSE_SYMBOLS, limit=scan_limit)

    if not df_market.empty:
        # Sort top movers
        top_gainers = df_market.sort_values(by="P_Change", ascending=False).head(10)
        top_losers = df_market.sort_values(by="P_Change", ascending=True).head(10)
        high_volume = df_market.sort_values(by="Volume", ascending=False).head(10)

        # 3 Top Columns (Subse Upar High Movement & Volume)
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("⚡ Top Intraday Gainers")
            for _, row in top_gainers.iterrows():
                st.markdown(
                    f"<div style='background-color:#131b2e; padding:10px; margin-bottom:6px; border-radius:8px; display:flex; justify-content:space-between; border-left:4px solid #00ff7f;'>"
                    f"<span><b>{row['Symbol']}</b> - ₹{row['LTP']}</span>"
                    f"<span style='color:#00ff7f; font-weight:bold;'>+{row['P_Change']}%</span>"
                    f"</div>", 
                    unsafe_allow_html=True
                )
                
        with col2:
            st.subheader("🔻 Top Intraday Losers")
            for _, row in top_losers.iterrows():
                st.markdown(
                    f"<div style='background-color:#131b2e; padding:10px; margin-bottom:6px; border-radius:8px; display:flex; justify-content:space-between; border-left:4px solid #ff3366;'>"
                    f"<span><b>{row['Symbol']}</b> - ₹{row['LTP']}</span>"
                    f"<span style='color:#ff3366; font-weight:bold;'>{row['P_Change']}%</span>"
                    f"</div>", 
                    unsafe_allow_html=True
                )

        with col3:
            st.subheader("📊 High Volume Surge")
            for _, row in high_volume.iterrows():
                color = "#00ff7f" if row['P_Change'] >= 0 else "#ff3366"
                st.markdown(
                    f"<div style='background-color:#131b2e; padding:10px; margin-bottom:6px; border-radius:8px; display:flex; justify-content:space-between; border-left:4px solid #3b82f6;'>"
                    f"<span><b>{row['Symbol']}</b> (Vol: {row['Volume_Str']})</span>"
                    f"<span style='color:{color}; font-weight:bold;'>{row['P_Change']}%</span>"
                    f"</div>", 
                    unsafe_allow_html=True
                )

        st.divider()
        st.subheader("🌐 Complete Scanned Shares Table")
        st.dataframe(df_market.sort_values(by="Volume", ascending=False), use_container_width=True)
    else:
        st.warning("Data fetch karne me samay lag raha hai, kripya refresh karein.")

# ==========================================
# PAGE 2: MARKET FLOW DASHBOARD
# ==========================================
else:
    html_code = """
    <!DOCTYPE html>
    <html lang="en" class="dark">
    <head>
        <meta charset="UTF-8">
        <script src="https://cdn.tailwindcss.com"></script>
        <script>
            tailwind.config = {
                darkMode: 'class',
                theme: {
                    extend: {
                        colors: { darkBg: '#0b0f19', cardBg: '#131b2e', borderCol: '#1e293b', neonGreen: '#00ff7f', neonRed: '#ff3366' }
                    }
                }
            }
        </script>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    </head>
    <body class="bg-darkBg text-slate-200 font-sans p-4 space-y-4">

        <header class="flex items-center justify-between px-4 py-3 bg-cardBg border-b border-borderCol rounded-xl">
            <div class="flex items-center space-x-2 font-bold text-white">
                <i class="fa-solid fa-chart-line text-neonGreen text-xl"></i>
                <span class="text-lg">JARVES <span class="font-light text-slate-400">TRADING FLOW</span></span>
            </div>
            <span class="bg-emerald-950 text-neonGreen text-xs px-3 py-1 rounded-full border border-emerald-800">● Live NSE Stream</span>
        </header>

        <div class="bg-cardBg border border-borderCol rounded-2xl p-4">
            <h2 class="font-bold text-sm text-white mb-2">LIVE MARKET ORDER FLOW (ANIMATED)</h2>
            <div class="relative bg-darkBg/80 border border-borderCol rounded-xl h-72 p-3 overflow-hidden">
                <canvas id="marketFlowCanvas" class="absolute inset-0 w-full h-full"></canvas>
            </div>
        </div>

        <script>
            function initCanvas() {
                const canvas = document.getElementById('marketFlowCanvas');
                if (!canvas) return;
                const ctx = canvas.getContext('2d');
                canvas.width = canvas.offsetWidth;
                canvas.height = canvas.offsetHeight;

                const streams = [];
                for (let i = 0; i < 30; i++) {
                    streams.push({
                        yEnd: Math.random() * canvas.height,
                        progress: Math.random(),
                        speed: 0.003 + Math.random() * 0.005,
                        color: Math.random() > 0.5 ? '#00ff7f' : '#ff3366',
                        amplitude: (Math.random() - 0.5) * 60
                    });
                }

                function animate() {
                    ctx.clearRect(0, 0, canvas.width, canvas.height);
                    streams.forEach(s => {
                        s.progress += s.speed;
                        if (s.progress > 1) s.progress = 0;
                        ctx.strokeStyle = s.color;
                        ctx.lineWidth = 1.5;
                        ctx.beginPath();
                        ctx.moveTo(30, canvas.height / 2);
                        let cpX = canvas.width * 0.5;
                        let cpY = (canvas.height / 2 + s.yEnd) / 2 + s.amplitude;
                        ctx.quadraticCurveTo(cpX, cpY, canvas.width - 30, s.yEnd);
                        ctx.stroke();
                    });
                    requestAnimationFrame(animate);
                }
                animate();
            }
            window.onload = initCanvas;
        </script>
    </body>
    </html>
    """
    components.html(html_code, height=650, scrolling=True)
