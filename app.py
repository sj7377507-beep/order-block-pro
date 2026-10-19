import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
import pandas as pd
import requests
import io
import time

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

def fetch_live_market_data_with_progress(symbols_list):
    """Full market bulk scan with live progress bar and percentage tracking"""
    total_symbols = len(symbols_list)
    market_data = []
    
    progress_text = st.empty()
    my_bar = st.progress(0)
    
    chunk_size = 100
    for i in range(0, total_symbols, chunk_size):
        chunk = symbols_list[i:i + chunk_size]
        pct = min(1.0, (i + len(chunk)) / total_symbols)
        percent_int = int(pct * 100)
        
        progress_text.markdown(f"**Scanning Market Data...** Progress: **{percent_int}%** ({i + len(chunk)} / {total_symbols} Shares Scanned)")
        my_bar.progress(pct)
        
        try:
            data = yf.download(chunk, period="2d", group_by="ticker", progress=False, threads=True)
            for symbol in chunk:
                clean_sym = symbol.replace(".NS", "")
                try:
                    if len(chunk) == 1:
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
                            high_val = float(df_sym['High'].max())
                            low_val = float(df_sym['Low'].min())
                            
                            market_data.append({
                                "Symbol": clean_sym,
                                "LTP": round(ltp, 2),
                                "Change": round(change, 2),
                                "P_Change": round(p_change, 2),
                                "Volume": int(volume),
                                "Volume_Str": f"{round(volume/1000000, 2)}M" if volume >= 1000000 else f"{round(volume/1000, 1)}K",
                                "High": round(high_val, 2),
                                "Low": round(low_val, 2),
                                "Abs_Move": abs(p_change),
                                "OI_Score": round(p_change * 1.5, 2),
                                "Status": "LONG BUILD-UP" if p_change > 0 else "SHORT BUILD-UP",
                                "Zone": f"{round(ltp * 0.98, 1)} - {round(ltp * 0.99, 1)}",
                                "R1": round(ltp * 1.02, 2),
                                "R2": round(ltp * 1.04, 2),
                                "S1": round(ltp * 0.97, 2)
                            })
                except Exception:
                    continue
        except Exception:
            continue
            
    progress_text.empty()
    my_bar.empty()
    return pd.DataFrame(market_data)

def render_advanced_order_block_card(row_data):
    """Renders futuristic dark-neon HUD card matching order-block.com reference layout"""
    is_bullish = row_data['P_Change'] >= 0
    badge_bg = "rgba(0, 255, 127, 0.15)" if is_bullish else "rgba(255, 51, 102, 0.15)"
    badge_color = "#00ff7f" if is_bullish else "#ff3366"
    sign_str = "+" if is_bullish else ""
    
    card_html = f"""
    <div style="background: linear-gradient(135deg, #0f172a 0%, #0b0f19 100%); border: 1px solid #1e293b; border-radius: 16px; padding: 18px; margin-bottom: 15px; box-shadow: 0 4px 20px rgba(0,0,0,0.5);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <div>
                <span style="font-size: 18px; font-weight: bold; color: #ffffff;">{row_data['Symbol']}</span>
                <span style="font-size: 14px; color: #94a3b8; margin-left: 10px;">₹{row_data['LTP']}</span>
            </div>
            <div style="background-color: {badge_bg}; color: {badge_color}; border: 1px solid {badge_color}; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: bold;">
                {sign_str}{row_data['P_Change']}%
            </div>
        </div>
        
        <div style="display: flex; gap: 10px; margin-bottom: 12px;">
            <div style="background: rgba(30, 41, 59, 0.7); padding: 4px 10px; border-radius: 6px; font-size: 11px; color: #38bdf8; font-weight: bold;">
                ⚡ {row_data['Status']}
            </div>
            <div style="background: rgba(30, 41, 59, 0.7); padding: 4px 10px; border-radius: 6px; font-size: 11px; color: #cbd5e1;">
                Vol: {row_data['Volume_Str']}
            </div>
        </div>
        
        <div style="background: #060911; border: 1px dashed #1e293b; border-radius: 10px; padding: 10px; font-size: 12px; display: flex; justify-content: space-between; color: #94a3b8;">
            <div>SUPPORT ZONE: <span style="color: #00ff7f; font-weight: bold;">{row_data['Zone']}</span></div>
            <div>S1: <span style="color: #facc15;">{row_data['S1']}</span></div>
            <div>R1: <span style="color: #ff3366;">{row_data['R1']}</span></div>
            <div>R2: <span style="color: #ff3366;">{row_data['R2']}</span></div>
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

# Navigation
st.sidebar.title("📌 Navigation")
page = st.sidebar.radio("Go to Page", [
    "🚀 SUPER INTRADAY", 
    "⚡ Instant Move", 
    "📊 Top Volume Stocks", 
    "🔥 Intraday Hot Tracker (Pure Market)", 
    "📊 Market Flow Dashboard"
])

if "selected_stock" not in st.session_state:
    st.session_state.selected_stock = "RELIANCE"

# ==========================================
# PAGE 1: SUPER INTRADAY
# ==========================================
if page == "🚀 SUPER INTRADAY":
    st.markdown("<h2 style='color:#00ff7f;'>🚀 SUPER INTRADAY FAST SCANNER (20 Bullish & 20 Bearish)</h2>", unsafe_allow_html=True)
    st.caption("Full market bulk scan with live market direction, order block zones, and futuristic cards.")

    if st.button("🔄 Refresh Market Data", key="refresh_super"):
        st.cache_data.clear()
        st.rerun()

    df_market = fetch_live_market_data_with_progress(ALL_NSE_SYMBOLS)

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
                render_advanced_order_block_card(row)
                if st.button(f"📊 Select & View Chart: {row['Symbol']}", key=f"super_bull_{row['Symbol']}"):
                    st.session_state.selected_stock = row['Symbol']
                
        with col2:
            st.markdown(f"<h3 style='color:#ff3366; font-size:16px;'>🔴 TOP 20 BEARISH STOCKS</h3>", unsafe_allow_html=True)
            for _, row in top_bearish.iterrows():
                render_advanced_order_block_card(row)
                if st.button(f"📊 Select & View Chart: {row['Symbol']}", key=f"super_bear_{row['Symbol']}"):
                    st.session_state.selected_stock = row['Symbol']

        st.divider()
        st.markdown(f"### 📈 Selected Stock Price Trend: <span style='color:#00ff7f;'>{st.session_state.selected_stock}</span>", unsafe_allow_html=True)
        try:
            ticker_obj = yf.Ticker(f"{st.session_state.selected_stock}.NS")
            df_hist = ticker_obj.history(period="5d", interval="15m")
            if not df_hist.empty:
                st.line_chart(df_hist['Close'], color="#00ff7f")
        except Exception:
            pass
    else:
        st.warning("Data load ho raha hai, kripya thoda intezaar karein.")

# ==========================================
# PAGE 2: INSTANT MOVE
# ==========================================
elif page == "⚡ Instant Move":
    st.markdown("<h2 style='color:#00ff7f;'>⚡ INSTANT MOVE SCANNER (Top 20 Explosive Movers)</h2>", unsafe_allow_html=True)
    st.caption("Automatically scanning entire NSE market pool for top 20 biggest price movements with order block HUD.")

    if st.button("🔄 Refresh Market Data", key="refresh_instant"):
        st.cache_data.clear()
        st.rerun()

    df_market = fetch_live_market_data_with_progress(ALL_NSE_SYMBOLS)

    if not df_market.empty:
        top_instant_moves = df_market.sort_values(by="Abs_Move", ascending=False).head(20)

        st.markdown(f"<h3 style='color:#00ff7f; font-size:16px;'>🔥 TOP 20 BIGGEST PRICE MOVERS (FULL MARKET)</h3>", unsafe_allow_html=True)
        
        for _, row in top_instant_moves.iterrows():
            render_advanced_order_block_card(row)
            if st.button(f"📊 Select & View Chart: {row['Symbol']}", key=f"instant_card_{row['Symbol']}"):
                st.session_state.selected_stock = row['Symbol']

        st.divider()
        st.markdown(f"### 📈 Selected Stock Price Trend: <span style='color:#00ff7f;'>{st.session_state.selected_stock}</span>", unsafe_allow_html=True)
        try:
            ticker_obj = yf.Ticker(f"{st.session_state.selected_stock}.NS")
            df_hist = ticker_obj.history(period="5d", interval="15m")
            if not df_hist.empty:
                st.line_chart(df_hist['Close'], color="#00ff7f")
        except Exception:
            pass
    else:
        st.warning("Data load ho raha hai, kripya thoda intezaar karein.")

# ==========================================
# PAGE 3: TOP VOLUME STOCKS
# ==========================================
elif page == "📊 Top Volume Stocks":
    st.markdown("<h2 style='color:#38bdf8;'>📊 TOP 20 HIGH VOLUME STOCKS SCANNER</h2>", unsafe_allow_html=True)
    st.caption("Dedicated full market scan for top 20 stocks with highest trading volume and order block zones.")

    if st.button("🔄 Refresh Market Data", key="refresh_volume"):
        st.cache_data.clear()
        st.rerun()

    df_market = fetch_live_market_data_with_progress(ALL_NSE_SYMBOLS)

    if not df_market.empty:
        top_volume_stocks = df_market.sort_values(by="Volume", ascending=False).head(20)

        st.markdown(f"<h3 style='color:#38bdf8; font-size:16px;'>📊 TOP 20 HIGH VOLUME STOCKS (FULL MARKET)</h3>", unsafe_allow_html=True)
        
        for _, row in top_volume_stocks.iterrows():
            render_advanced_order_block_card(row)
            if st.button(f"📊 Select & View Chart: {row['Symbol']}", key=f"vol_card_{row['Symbol']}"):
                st.session_state.selected_stock = row['Symbol']

        st.divider()
        st.markdown(f"### 📈 Selected Stock Price Trend: <span style='color:#00ff7f;'>{st.session_state.selected_stock}</span>", unsafe_allow_html=True)
        try:
            ticker_obj = yf.Ticker(f"{st.session_state.selected_stock}.NS")
            df_hist = ticker_obj.history(period="5d", interval="15m")
            if not df_hist.empty:
                st.line_chart(df_hist['Close'], color="#00ff7f")
        except Exception:
            pass
    else:
        st.warning("Data load ho raha hai, kripya thoda intezaar karein.")

# ==========================================
# PAGE 4: INTRADAY HOT TRACKER (PURE MARKET)
# ==========================================
elif page == "🔥 Intraday Hot Tracker (Pure Market)":
    if st.button("🔄 Refresh Market Data", key="refresh_hot"):
        st.cache_data.clear()
        st.rerun()

    df_market = fetch_live_market_data_with_progress(ALL_NSE_SYMBOLS)

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
        top_gainers = df_market.sort_values(by="P_Change", ascending=False).head(5)
        for _, row in top_gainers.iterrows():
            render_advanced_order_block_card(row)

        st.divider()
        st.subheader("🌐 Complete Scanned Shares Table")
        st.dataframe(df_market.sort_values(by="Volume", ascending=False), use_container_width=True)

# ==========================================
# PAGE 5: MARKET FLOW DASHBOARD
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
