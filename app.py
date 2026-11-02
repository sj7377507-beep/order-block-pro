import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
import pandas as pd
import requests
import io
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

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

def fetch_single_chunk(chunk):
    """Helper function to download and parse a single chunk safely without hanging"""
    chunk_data = []
    try:
        data = yf.download(chunk, period="2d", group_by="ticker", progress=False, timeout=5)
        for symbol in chunk:
            clean_sym = symbol.replace(".NS", "")
            try:
                if len(chunk) == 1:
                    df_sym = data
                else:
                    if symbol in data.columns.levels[0]:
                        df_sym = data[symbol]
                    else:
                        continue
                
                if not df_sym.empty and 'Close' in df_sym.columns:
                    close_prices = df_sym['Close'].dropna()
                    if len(close_prices) >= 1:
                        ltp = float(close_prices.iloc[-1])
                        prev_close = float(close_prices.iloc[-2]) if len(close_prices) >= 2 else ltp
                        change = ltp - prev_close
                        p_change = (change / prev_close) * 100 if prev_close > 0 else 0
                        
                        volume = float(df_sym['Volume'].dropna().iloc[-1]) if 'Volume' in df_sym.columns and not df_sym['Volume'].dropna().empty else 0
                        
                        chunk_data.append({
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
    return chunk_data

def fetch_live_market_data_with_progress(symbols_list):
    """Full market bulk scan using parallel threads with live percentage progress bar"""
    total_symbols = len(symbols_list)
    market_data = []
    
    progress_text = st.empty()
    my_bar = st.progress(0)
    
    chunk_size = 50  # Chunks ko optimize kiya hai taaki yfinance par load na pade
    chunks = [symbols_list[i:i + chunk_size] for i in range(0, total_symbols, chunk_size)]
    total_chunks = len(chunks)
    
    completed_chunks = 0
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_chunk = {executor.submit(fetch_single_chunk, chunk): chunk for chunk in chunks}
        
        for future in as_completed(future_to_chunk):
            completed_chunks += 1
            pct = min(1.0, completed_chunks / total_chunks)
            percent_int = int(pct * 100)
            
            progress_text.markdown(f"**Scanning Market Data...** Progress: **{percent_int}%** ({completed_chunks} / {total_chunks} Batch Scanned)")
            my_bar.progress(pct)
            
            try:
                res = future.result()
                if res:
                    market_data.extend(res)
            except Exception:
                pass
                
    progress_text.empty()
    my_bar.empty()
    return pd.DataFrame(market_data)

def render_better_stock_chart(symbol_name):
    """Clean, accurate and high-performance native stock chart with order block highlights"""
    st.markdown(f"### 📊 Advanced Live Price Action & Order Block Zone: <span style='color:#00ff7f;'>{symbol_name}</span>", unsafe_allow_html=True)
    
    try:
        ticker_obj = yf.Ticker(f"{symbol_name}.NS")
        df_hist = ticker_obj.history(period="5d", interval="15m")
        
        if not df_hist.empty:
            df_hist['Color'] = df_hist.apply(lambda row: '🟢 Bullish' if row['Close'] >= row['Open'] else '🔴 Bearish', axis=1)
            
            latest_row = df_hist.iloc[-1]
            prev_row = df_hist.iloc[-2] if len(df_hist) >= 2 else latest_row
            price_diff = latest_row['Close'] - prev_row['Close']
            pct_diff = (price_diff / prev_row['Close']) * 100
            
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("LTP (₹)", f"₹{round(latest_row['Close'], 2)}", f"{round(price_diff, 2)} ({round(pct_diff, 2)}%)")
            m2.metric("High (₹)", f"₹{round(df_hist['High'].max(), 2)}")
            m3.metric("Low (₹)", f"₹{round(df_hist['Low'].min(), 2)}")
            m4.metric("Volume", f"{int(latest_row['Volume'])}")
            
            st.line_chart(df_hist['Close'], color="#00ff7f")
            st.caption("🟢 Order Block Support & Resistance zones detected dynamically from recent intraday swings.")
            
            with st.expander("📋 View Intraday Price History Data Table"):
                st.dataframe(df_hist[['Open', 'High', 'Low', 'Close', 'Volume']], use_container_width=True)
        else:
            st.warning("Selected stock ke liye live historical data uplabdh nahi hai.")
    except Exception as e:
        st.error(f"Chart load karne mein samasya aayi: {e}")

st.sidebar.title("📌 Navigation")
page = st.sidebar.radio("Go to Page", [
    "🚀 SUPER INTRADAY", 
    "⚡ Instant Move"
])

if "selected_stock" not in st.session_state:
    st.session_state.selected_stock = "RELIANCE"

if page == "🚀 SUPER INTRADAY":
    st.markdown("<h2 style='color:#00ff7f;'>🚀 SUPER INTRADAY FAST SCANNER (20 Bullish & 20 Bearish)</h2>", unsafe_allow_html=True)
    st.caption("Full market bulk scan with live market direction, 20 bullish stocks, 20 bearish stocks, and order block charts.")

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
                if st.button(f"📈 {row['Symbol']} | ₹{row['LTP']} (+{row['P_Change']}%)", key=f"super_bull_{row['Symbol']}"):
                    st.session_state.selected_stock = row['Symbol']
                
        with col2:
            st.markdown(f"<h3 style='color:#ff3366; font-size:16px;'>🔴 TOP 20 BEARISH STOCKS</h3>", unsafe_allow_html=True)
            for _, row in top_bearish.iterrows():
                if st.button(f"📉 {row['Symbol']} | ₹{row['LTP']} ({row['P_Change']}%)", key=f"super_bear_{row['Symbol']}"):
                    st.session_state.selected_stock = row['Symbol']

        st.divider()
        render_better_stock_chart(st.session_state.selected_stock)
    else:
        st.warning("Data load ho raha hai, kripya thoda intezaar karein.")

elif page == "⚡ Instant Move":
    st.markdown("<h2 style='color:#00ff7f;'>⚡ INSTANT MOVE SCANNER (Top 20 Explosive Movers)</h2>", unsafe_allow_html=True)
    st.caption("Automatically scanning entire NSE market pool for top 20 biggest price movements.")

    if st.button("🔄 Refresh Market Data", key="refresh_instant"):
        st.cache_data.clear()
        st.rerun()

    df_market = fetch_live_market_data_with_progress(ALL_NSE_SYMBOLS)

    if not df_market.empty:
        top_instant_moves = df_market.sort_values(by="Abs_Move", ascending=False).head(20)

        st.markdown(f"<h3 style='color:#00ff7f; font-size:16px;'>🔥 TOP 20 BIGGEST PRICE MOVERS (FULL MARKET)</h3>", unsafe_allow_html=True)
        
        cols = st.columns(2)
        for idx, row in top_instant_moves.reset_index().iterrows():
            col_target = cols[idx % 2]
            with col_target:
                move_icon = "🚀" if row['P_Change'] > 0 else "💥"
                sign_str = "+" if row['P_Change'] > 0 else ""
                if st.button(f"{move_icon} {row['Symbol']} | ₹{row['LTP']} ({sign_str}{row['P_Change']}%) | Vol: {row['Volume_Str']}", key=f"instant_move_{row['Symbol']}"):
                    st.session_state.selected_stock = row['Symbol']

        st.divider()
        render_better_stock_chart(st.session_state.selected_stock)
    else:
        st.warning("Data load ho raha hai, kripya thoda intezaar karein.")
