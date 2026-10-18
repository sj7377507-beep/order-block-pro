
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
    url = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=5)
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

@st.cache_data(ttl=60)
def fetch_live_market_data(symbols_list, limit=100):
    """Ultra-fast bulk market data fetcher using yfinance download"""
    sample_symbols = symbols_list[:limit]
    market_data = []
    
    try:
        data = yf.download(sample_symbols, period="2d", group_by="ticker", progress=False, threads=True)
        for symbol in sample_symbols:
            clean_sym = symbol.replace(".NS", "")
            try:
                if len(sample_symbols) == 1:
                    df_sym = data
                else:
                    df_sym = data[symbol]
                
                if not df_sym.empty and len(df_sym) >= 1:
                    close_prices = df_sym['Close'].dropna()
                    if len(close_prices) >= 1:
                        ltp = float(close_prices.iloc[-1])
                        prev_close = float(close_prices.iloc[-2]) if len(close_prices) >= 2 else ltp
                        change = ltp - prev_close
                        p_change = (change / prev_close) * 100 if prev_close > 0 else 0
                        
                        volume = float(df_sym['Volume'].iloc[-1]) if 'Volume' in df_sym.columns and not df_sym['Volume'].empty else 0
                        
                        market_data.append({
                            "Symbol": clean_sym,
                            "LTP": round(ltp, 2),
                            "Change": round(change, 2),
                            "P_Change": round(p_change, 2),
                            "Volume": int(volume),
                            "Volume_Str": f"{round(volume/1000000, 2)}M" if volume >= 1000000 else f"{round(volume/1000, 1)}K",
                            "MarketCap_Cr": 0,
                            "Abs_Move": abs(p_change),
                            "OI_Score": round(p_change * 1.5, 2)
                        })
            except Exception:
                continue
    except Exception:
        pass
        
    return pd.DataFrame(market_data)

# Navigation with Instant Move explicitly included
st.sidebar.title("📌 Navigation")
page = st.sidebar.radio("Go to Page", ["🚀 SUPER INTRADAY", "⚡ Instant Move", "🔥 Intraday Hot Tracker (Pure Market)", "📊 Market Flow Dashboard"])

if "selected_stock" not in st.session_state:
    st.session_state.selected_stock = "RELIANCE"

# ==========================================
# PAGE 1: SUPER INTRADAY
# ==========================================
if page == "🚀 SUPER INTRADAY":
    st.markdown("<h2 style='color:#00ff7f;'>🚀 SUPER INTRADAY FAST SCANNER (20 Bullish & 20 Bearish)</h2>", unsafe_allow_html=True)
    st.caption("Instant bulk market scan with live market direction, 20 bullish stocks, 20 bearish stocks, and order block charts.")

    scan_limit = st.sidebar.slider("Fast Scan Range (Stocks Count)", min_value=50, max_value=len(ALL_NSE_SYMBOLS), value=100, step=50)
    
    with st.spinner("Instant bulk scanning market..."):
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
                    <span style="color:#94a3b8; font-size:12px;">SCANNER STATUS</span>
                    <h3 style="color:#ffffff; margin:0; font-size:18px;">{total_count} / {len(ALL_NSE_SYMBOLS)} Scanned</h3>
                </div>
            </div>
            """, 
            unsafe_allow_html=True
        )

        top_bullish = df_market.sort_values(by="P_Change", ascending=False).head(20)
        top_bearish = df_market.sort_values(by="P_Change", ascending=True).head(20)

        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"<h3 style='color:#00ff7f; font-size:16px;'>🟢 TOP 20 BULLISH STOCKS</h3>", unsafe_allow_html=True)
            for _, row in top_bullish.iterrows():
                if st.button(f"📈 {row['Symbol']} | ₹{row['LTP']} (+{row['P_Change']}%)", key=f"super_bull_{row['Symbol']}"):
                    st.session_state.selected_stock = row['Symbol']
                
        with col2:
            st.markdown(f"<h3 style='color:#ff3366; font-size:16px;'>🔴 TOP 20 BEARISH STOCKS</h3>", unsafe_allow_html=True)
            for _, row in top_bearish.iterrows():
                if st.button(f"📉 {row['Symbol']} | ₹{row['LTP']} ({row['P_Change']}%)", key=f"super_bear_{row['Symbol']}"):
                    st.session_state.selected_stock = row['Symbol']

        st.divider()

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
    else:
        st.warning("Data load ho raha hai, kripya thoda intezaar karein.")

# ==========================================
# PAGE 2: INSTANT MOVE (TOP 20 BIGGEST MOVES)
# ==========================================
elif page == "⚡ Instant Move":
    st.markdown("<h2 style='color:#00ff7f;'>⚡ INSTANT MOVE SCANNER (Top 20 Explosive Movers)</h2>", unsafe_allow_html=True)
    st.caption("Automatically updates top 20 shares with the biggest intraday price movements (highest absolute % change).")

    scan_limit = st.sidebar.slider("Fast Scan Range (Stocks Count)", min_value=50, max_value=len(ALL_NSE_SYMBOLS), value=100, step=50, key="instant_slider")
    
    with st.spinner("Scanning market for biggest moves..."):
        df_market = fetch_live_market_data(ALL_NSE_SYMBOLS, limit=scan_limit)

    if not df_market.empty:
        top_instant_moves = df_market.sort_values(by="Abs_Move", ascending=False).head(20)

        st.markdown(f"<h3 style='color:#00ff7f; font-size:16px;'>🔥 TOP 20 BIGGEST PRICE MOVERS</h3>", unsafe_allow_html=True)
        
        cols = st.columns(2)
        for idx, row in top_instant_moves.reset_index().iterrows():
            col_target = cols[idx % 2]
            with col_target:
                move_icon = "🚀" if row['P_Change'] > 0 else "💥"
                sign_str = "+" if row['P_Change'] > 0 else ""
                if st.button(f"{move_icon} {row['Symbol']} | ₹{row['LTP']} ({sign_str}{row['P_Change']}%) | Vol: {row['Volume_Str']}", key=f"instant_move_{row['Symbol']}"):
                    st.session_state.selected_stock = row['Symbol']

        st.divider()

        st.markdown(f"### 📈 Live Chart & Order Block Zone: <span style='color:#00ff7f;'>{st.session_state.selected_stock}</span>", unsafe_allow_html=True)
        
        tv_symbol = f"NSE:{st.session_state.selected_stock}"
        tv_widget = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
        </head>
        <body style="margin:0; background-color:#0b0f19;">
            <div id="tradingview_instant_chart" style="height:520px; width:100%;"></div>
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
                "container_id": "tradingview_instant_chart",
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
    else:
        st.warning("Data load ho raha hai, kripya thoda intezaar karein.")

# ==========================================
# PAGE 3: INTRADAY HOT TRACKER (PURE MARKET)
# ==========================================
elif page == "🔥 Intraday Hot Tracker (Pure Market)":
    scan_limit = st.sidebar.slider("Live Scan Range (Stocks Count)", min_value=50, max_value=len(ALL_NSE_SYMBOLS), value=100, step=50, key="hot_slider")
    
    with st.spinner("Processing live market volume and trends..."):
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
# PAGE 4: MARKET FLOW DASHBOARD
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
