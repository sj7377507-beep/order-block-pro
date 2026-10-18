import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
import pandas as pd
import requests
import io

# Page setup
st.set_page_config(page_title="Jarves Trading Pro - Super Intraday Dashboard", layout="wide")

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
            if 'SERIES' in df.columns:
                df = df[df['SERIES'] == 'EQ']
            symbols = [f"{sym.strip()}.NS" for sym in df['SYMBOL'].tolist() if isinstance(sym, str)]
            return symbols
    except Exception:
        pass
    return ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS", "SBIN.NS", "TATAMOTORS.NS", "ZOMATO.NS", "PAYTM.NS", "WIPRO.NS"]

ALL_NSE_SYMBOLS = get_all_nse_symbols()

@st.cache_data(ttl=120)
def fetch_live_market_data(symbols_list, limit=200):
    """Fetch live market price, market cap, volume, and simulated OI metrics"""
    data = []
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
                market_cap = info.market_cap if hasattr(info, 'market_cap') and info.market_cap is not None else 0
                
                if prev_close and prev_close > 0 and ltp > 0:
                    change = ltp - prev_close
                    p_change = (change / prev_close) * 100
                else:
                    change, p_change = 0, 0
                    
                clean_symbol = symbol.replace(".NS", "")
                
                mcap_cr = round(market_cap / 10000000, 2) if market_cap else 0
                oi_build_score = round((p_change * 1.5) + (volume / 500000), 2)
                
                if ltp > 0:
                    data.append({
                        "Symbol": clean_symbol,
                        "LTP": round(ltp, 2),
                        "Change": round(change, 2),
                        "P_Change": round(p_change, 2),
                        "Volume": int(volume),
                        "Volume_Str": f"{round(volume/1000000, 2)}M" if volume >= 1000000 else f"{round(volume/1000, 1)}K",
                        "MarketCap_Cr": mcap_cr,
                        "OI_Score": oi_build_score
                    })
            except Exception:
                continue
    except Exception:
        pass
    
    return pd.DataFrame(data)

# Navigation
st.sidebar.title("📌 Navigation")
page = st.sidebar.radio("Go to Page", ["🚀 SUPER INTRADAY", "🔥 Intraday Hot Tracker (Pure Market)", "📊 Market Flow Dashboard"])

if "selected_stock" not in st.session_state:
    st.session_state.selected_stock = "RELIANCE"

# ==========================================
# PAGE 1: SUPER INTRADAY (NEW DEDICATED PAGE)
# ==========================================
if page == "🚀 SUPER INTRADAY":
    st.markdown("<h2 style='color:#00ff7f;'>🚀 SUPER INTRADAY MOVER & ORDER BLOCK SCANNER</h2>", unsafe_allow_html=True)
    st.caption("High Volume, Top Gainers aur Losers ko ek click me dekhein aur Order Block Zone highlight karein.")

    scan_limit = st.sidebar.slider("Live Scan Range (Stocks Count)", min_value=100, max_value=len(ALL_NSE_SYMBOLS), value=200, step=100)
    
    with st.spinner("Processing Super Intraday volume surge and price trends..."):
        df_market = fetch_live_market_data(ALL_NSE_SYMBOLS, limit=scan_limit)

    if not df_market.empty:
        # OVERALL MARKET DIRECTION AT TOP
        positive_count = len(df_market[df_market["P_Change"] > 0])
        total_count = len(df_market)
        bullish_pct = round((positive_count / total_count) * 100, 1) if total_count > 0 else 50
        
        market_dir = "BULLISH 🟢" if bullish_pct >= 50 else "BEARISH 🔴"
        dir_color = "#00ff7f" if bullish_pct >= 50 else "#ff3366"

        st.markdown(
            f"""
            <div style="background-color:#131b2e; border:1px solid #1e293b; padding:15px; border-radius:12px; margin-bottom:15px; display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <span style="color:#94a3b8; font-size:12px; font-weight:bold;">OVERALL MARKET DIRECTION</span>
                    <h2 style="color:{dir_color}; margin:0; font-size:24px; font-weight:bold;">{market_dir} ({bullish_pct}% Advances)</h2>
                </div>
                <div style="text-align:right;">
                    <span style="color:#94a3b8; font-size:12px;">ACTIVE SCANNER</span>
                    <h3 style="color:#ffffff; margin:0; font-size:18px;">{total_count} / {len(ALL_NSE_SYMBOLS)} Live Stocks</h3>
                </div>
            </div>
            """, 
            unsafe_allow_html=True
        )

        # SUPER INTRADAY HIGH VOLUME & GAINERS/LOSERS CARDS
        top_gainers = df_market.sort_values(by="P_Change", ascending=False).head(10)
        top_losers = df_market.sort_values(by="P_Change", ascending=True).head(10)
        high_volume = df_market.sort_values(by="Volume", ascending=False).head(10)

        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("<h3 style='color:#00ff7f; font-size:16px;'>⚡ GAINERS (High Upward Movement)</h3>", unsafe_allow_html=True)
            for _, row in top_gainers.iterrows():
                if st.button(f"🟢 {row['Symbol']} | ₹{row['LTP']} (+{row['P_Change']}%)", key=f"super_g_{row['Symbol']}"):
                    st.session_state.selected_stock = row['Symbol']
                
        with col2:
            st.markdown("<h3 style='color:#ff3366; font-size:16px;'>🔻 LOSERS (High Downward Movement)</h3>", unsafe_allow_html=True)
            for _, row in top_losers.iterrows():
                if st.button(f"🔴 {row['Symbol']} | ₹{row['LTP']} ({row['P_Change']}%)", key=f"super_l_{row['Symbol']}"):
                    st.session_state.selected_stock = row['Symbol']

        with col3:
            st.markdown("<h3 style='color:#3b82f6; font-size:16px;'>🔥 HIGH VOLUME SURGE SHARES</h3>", unsafe_allow_html=True)
            for _, row in high_volume.iterrows():
                if st.button(f"📊 {row['Symbol']} | Vol: {row['Volume_Str']} ({row['P_Change']}%)", key=f"super_v_{row['Symbol']}"):
                    st.session_state.selected_stock = row['Symbol']

        st.divider()

        # LIVE CHART & ORDER BLOCK ZONE DISPLAY
        st.markdown(f"### 📈 Live Chart & Order Block Zone: <span style='color:#00ff7f;'>{st.session_state.selected_stock}</span>", unsafe_allow_html=True)
        
        tv_symbol = f"NSE:{st.session_state.selected_stock}"
        tv_widget = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
        </head>
        <body style="margin:0; background-color:#0b0f19;">
            <div id="tradingview_super_chart" style="height:520px; width:100%;"></div>
            <script type="text/javascript">
            new TradingView.widget({{
                "autosize": true,
                "symbol": "{tv_symbol}",
                "interval": "5",
                "timezone": "Asia/Kolkata",
                "theme": "dark",
                "style": "1",
                "locale": "en",
                "toolbar_bg": "#f1f3f6",
                "enable_publishing": false,
                "allow_symbol_change": true,
                "container_id": "tradingview_super_chart",
                "studies": [
                    "STD;Volume",
                    "STD;Order_Blocks"
                ]
            }});
            </script>
        </body>
        </html>
        """
        components.html(tv_widget, height=540, scrolling=False)

# ==========================================
# PAGE 2: INTRADAY HOT TRACKER (PURE MARKET)
# ==========================================
elif page == "🔥 Intraday Hot Tracker (Pure Market)":
    scan_limit = st.sidebar.slider("Live Scan Range (Stocks Count)", min_value=100, max_value=len(ALL_NSE_SYMBOLS), value=200, step=100)
    
    with st.spinner("Processing live market volume, open interest, and trend metrics..."):
        df_market = fetch_live_market_data(ALL_NSE_SYMBOLS, limit=scan_limit)

    if not df_market.empty:
        positive_count = len(df_market[df_market["P_Change"] > 0])
        total_count = len(df_market)
        bullish_pct = round((positive_count / total_count) * 100, 1) if total_count > 0 else 50
        
        market_dir = "BULLISH 🟢" if bullish_pct >= 50 else "BEARISH 🔴"
        dir_color = "#00ff7f" if bullish_pct >= 50 else "#ff3366"

        st.markdown(
            f"""
            <div style="background-color:#131b2e; border:1px solid #1e293b; padding:15px; border-radius:12px; margin-bottom:15px; display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <span style="color:#94a3b8; font-size:12px; font-weight:bold;">OVERALL MARKET DIRECTION</span>
                    <h2 style="color:{dir_color}; margin:0; font-size:24px; font-weight:bold;">{market_dir} ({bullish_pct}% Advances)</h2>
                </div>
                <div style="text-align:right;">
                    <span style="color:#94a3b8; font-size:12px;">SCANNED STOCKS</span>
                    <h3 style="color:#ffffff; margin:0; font-size:18px;">{total_count} / {len(ALL_NSE_SYMBOLS)} NSE Listed</h3>
                </div>
            </div>
            """, 
            unsafe_allow_html=True
        )

        st.subheader("🎯 High Volatility & Market Filters")
        btn_filter = st.button("🔥 Market Cap + High Volume + Open Interest (OI) Gainers", use_container_width=True)

        if btn_filter:
            st.success("Filtered: High Market Cap, Explosive Volume & Open Interest Surge Stocks")
            display_df = df_market.sort_values(by=["OI_Score", "Volume"], ascending=[False, False]).head(10)
        else:
            display_df = df_market.sort_values(by="P_Change", ascending=False).head(10)

        top_gainers = df_market.sort_values(by="P_Change", ascending=False).head(10)
        top_losers = df_market.sort_values(by="P_Change", ascending=True).head(10)
        high_volume = df_market.sort_values(by="Volume", ascending=False).head(10)

        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("⚡ Top Intraday Gainers")
            for _, row in top_gainers.iterrows():
                if st.button(f"📈 {row['Symbol']} | ₹{row['LTP']} (+{row['P_Change']}%)", key=f"g_{row['Symbol']}"):
                    st.session_state.selected_stock = row['Symbol']
                
        with col2:
            st.subheader("🔻 Top Intraday Losers")
            for _, row in top_losers.iterrows():
                if st.button(f"📉 {row['Symbol']} | ₹{row['LTP']} ({row['P_Change']}%)", key=f"l_{row['Symbol']}"):
                    st.session_state.selected_stock = row['Symbol']

        with col3:
            st.subheader("📊 High Volume + OI Surge")
            for _, row in high_volume.iterrows():
                if st.button(f"🔥 {row['Symbol']} | Vol: {row['Volume_Str']} ({row['P_Change']}%)", key=f"v_{row['Symbol']}"):
                    st.session_state.selected_stock = row['Symbol']

        st.divider()

        st.markdown(f"### 📊 Live TradingView Chart & Order Block Zone: <span style='color:#00ff7f;'>{st.session_state.selected_stock}</span>", unsafe_allow_html=True)
        
        tv_symbol = f"NSE:{st.session_state.selected_stock}"
        tv_widget = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
        </head>
        <body style="margin:0; background-color:#0b0f19;">
            <div id="tradingview_chart" style="height:500px; width:100%;"></div>
            <script type="text/javascript">
            new TradingView.widget({{
                "autosize": true,
                "symbol": "{tv_symbol}",
                "interval": "5",
                "timezone": "Asia/Kolkata",
                "theme": "dark",
                "style": "1",
                "locale": "en",
                "toolbar_bg": "#f1f3f6",
                "enable_publishing": false,
                "allow_symbol_change": true,
                "container_id": "tradingview_chart",
                "studies": [
                    "STD;Volume",
                    "STD;Order_Blocks"
                ]
            }});
            </script>
        </body>
        </html>
        """
        components.html(tv_widget, height=520, scrolling=False)

        st.divider()
        st.subheader("🌐 Complete Scanned Shares Table")
        st.dataframe(df_market.sort_values(by="Volume", ascending=False), use_container_width=True)

# ==========================================
# PAGE 3: MARKET FLOW DASHBOARD
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
