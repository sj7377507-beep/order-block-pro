import io
import time
import warnings
from datetime import datetime

import pandas as pd
import requests
import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf

warnings.filterwarnings("ignore")

# ============================================================
# ORDERBLOCK KARKHANA - STREAMLIT APP
# Existing dashboard + AI Sudden Momentum & Breakout Detector
# Data source in this version: Yahoo Finance (yfinance).
# This is not a broker-grade real-time feed.
# ============================================================

st.set_page_config(
    page_title="OrderBlock Karkhana - Trading Dashboard",
    page_icon="📈",
    layout="wide",
)

st.markdown("""
<style>
    .stApp { background: #080d18; color: #e5e7eb; }
    [data-testid="stSidebar"] { background: #101827; }
    div[data-testid="stMetric"] {
        background: #111c2e; border: 1px solid #263449;
        padding: 12px; border-radius: 10px;
    }
    .positive { color: #00e676; }
    .negative { color: #ff526b; }
</style>
""", unsafe_allow_html=True)


# -------------------- NSE SYMBOL UNIVERSE --------------------

@st.cache_data(ttl=3600, show_spinner=False)
def get_all_nse_symbols():
    url = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 Chrome/120.0 Safari/537.36"
        )
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        df = pd.read_csv(io.StringIO(response.text))
        if "SYMBOL" not in df.columns:
            raise ValueError("NSE symbol column not found")
        if "SERIES" in df.columns:
            df = df[df["SERIES"].astype(str).str.strip().eq("EQ")]
        symbols = (
            df["SYMBOL"].dropna().astype(str).str.strip()
            .loc[lambda x: x.ne("")]
            .drop_duplicates().tolist()
        )
        return [f"{s}.NS" for s in symbols]
    except Exception:
        return [
            "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS",
            "ICICIBANK.NS", "SBIN.NS", "TATAMOTORS.NS",
            "WIPRO.NS", "ITC.NS", "BHARTIARTL.NS",
            "LT.NS", "AXISBANK.NS", "KOTAKBANK.NS",
        ]


ALL_NSE_SYMBOLS = get_all_nse_symbols()


def _extract_symbol_frame(downloaded, symbol, symbols):
    """Handle yfinance single-symbol and multi-symbol output formats."""
    if downloaded is None or downloaded.empty:
        return pd.DataFrame()
    if len(symbols) == 1:
        frame = downloaded.copy()
    else:
        try:
            frame = downloaded[symbol].copy()
        except Exception:
            try:
                frame = downloaded.xs(symbol, axis=1, level=0).copy()
            except Exception:
                try:
                    frame = downloaded.xs(symbol, axis=1, level=1).copy()
                except Exception:
                    return pd.DataFrame()
    if isinstance(frame.columns, pd.MultiIndex):
        frame.columns = frame.columns.get_level_values(0)
    frame = frame.loc[:, ~frame.columns.duplicated()]
    needed = ["Open", "High", "Low", "Close", "Volume"]
    if not all(c in frame.columns for c in needed):
        return pd.DataFrame()
    return frame[needed].dropna(subset=["Open", "High", "Low", "Close"])


# -------------------- ORIGINAL MARKET SCANNER --------------------

@st.cache_data(ttl=180, show_spinner=False)
def fetch_market_snapshot(symbols):
    records = []
    chunk_size = 80
    total_symbols = max(len(symbols), 1)
    progress_text = st.empty()
    progress_bar = st.progress(0)

    for start in range(0, len(symbols), chunk_size):
        chunk = symbols[start:start + chunk_size]
        scanned = min(start + len(chunk), total_symbols)
        percentage = int(scanned / total_symbols * 100)
        progress_text.markdown(
            f"**Scanning NSE Market Data: {percentage}%** "
            f"({scanned:,} / {total_symbols:,} stocks)"
        )
        progress_bar.progress(percentage)

        try:
            raw = yf.download(
                chunk, period="5d", interval="1d",
                group_by="ticker", progress=False,
                threads=True, auto_adjust=True,
            )
            for symbol in chunk:
                frame = _extract_symbol_frame(raw, symbol, chunk)
                if frame.empty:
                    continue
                close = frame["Close"].dropna()
                if len(close) < 1:
                    continue
                ltp = float(close.iloc[-1])
                previous = float(close.iloc[-2]) if len(close) > 1 else ltp
                change = ltp - previous
                pct = (change / previous * 100) if previous else 0
                volume = int(frame["Volume"].fillna(0).iloc[-1])
                records.append({
                    "Symbol": symbol.replace(".NS", ""),
                    "LTP": round(ltp, 2),
                    "Change": round(change, 2),
                    "P_Change": round(pct, 2),
                    "Volume": volume,
                    "Volume_Str": (
                        f"{volume / 1_000_000:.2f}M" if volume >= 1_000_000
                        else f"{volume / 1_000:.1f}K"
                    ),
                    "Abs_Move": abs(pct),
                })
        except Exception:
            continue

    progress_text.markdown("**Scanning NSE Market Data: 100% — Complete**")
    progress_bar.progress(100)
    time.sleep(0.2)
    progress_text.empty()
    progress_bar.empty()
    return pd.DataFrame(records)


def render_better_stock_chart(symbol_name):
    st.markdown(f"### 📊 Price Chart: **{symbol_name}**")
    try:
        ticker = yf.Ticker(f"{symbol_name}.NS")
        hist = ticker.history(period="1mo", interval="15m", auto_adjust=True)
        if hist.empty:
            hist = ticker.history(period="6mo", interval="1d", auto_adjust=True)
        if hist.empty:
            st.warning("Is stock ka chart data available nahi hai.")
            return
        latest = hist.iloc[-1]
        previous = hist.iloc[-2] if len(hist) > 1 else latest
        diff = float(latest["Close"] - previous["Close"])
        pct = diff / float(previous["Close"]) * 100 if previous["Close"] else 0
        a, b, c, d = st.columns(4)
        a.metric("LTP", f"₹{latest['Close']:.2f}", f"{diff:.2f} ({pct:.2f}%)")
        b.metric("Period High", f"₹{hist['High'].max():.2f}")
        c.metric("Period Low", f"₹{hist['Low'].min():.2f}")
        d.metric("Latest Volume", f"{int(latest['Volume']):,}")
        st.line_chart(hist["Close"], color="#00e676")
        with st.expander("Price history"):
            st.dataframe(hist[["Open", "High", "Low", "Close", "Volume"]], use_container_width=True)
    except Exception as exc:
        st.error(f"Chart load error: {exc}")


# -------------------- TECHNICAL INDICATORS --------------------

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / period, adjust=False).mean()
    loss = -delta.clip(upper=0).ewm(alpha=1 / period, adjust=False).mean()
    rs = gain / loss.replace(0, pd.NA)
    result = 100 - (100 / (1 + rs))
    return result.fillna(50)


def resample_ohlcv(frame, rule):
    if frame.empty:
        return pd.DataFrame()
    return frame.resample(rule).agg({
        "Open": "first", "High": "max", "Low": "min",
        "Close": "last", "Volume": "sum",
    }).dropna(subset=["Open", "High", "Low", "Close"])


def timeframe_direction(frame):
    if len(frame) < 5:
        return "N/A"
    close = frame["Close"]
    ema_fast = close.ewm(span=9, adjust=False).mean().iloc[-1]
    ema_slow = close.ewm(span=21, adjust=False).mean().iloc[-1]
    if ema_fast > ema_slow and close.iloc[-1] > ema_fast:
        return "BULLISH"
    if ema_fast < ema_slow and close.iloc[-1] < ema_fast:
        return "BEARISH"
    return "NEUTRAL"


def analyze_one_stock(intraday, daily, symbol):
    """Use only closed historical bars available from yfinance where possible."""
    if intraday.empty or daily.empty or len(intraday) < 30 or len(daily) < 6:
        return None

    intraday = intraday.copy().sort_index()
    daily = daily.copy().sort_index()

    # Avoid relying on the newest still-forming 5-minute candle.
    if len(intraday) > 2:
        bars = intraday.iloc[:-1].copy()
    else:
        bars = intraday.copy()

    if len(bars) < 25:
        return None

    latest = bars.iloc[-1]
    previous_bars = bars.iloc[-21:-1]
    if len(previous_bars) < 15:
        return None

    ltp = float(latest["Close"])
    prior_resistance = float(previous_bars["High"].max())
    prior_support = float(previous_bars["Low"].min())
    avg_vol = float(previous_bars["Volume"].mean())
    current_vol = float(latest["Volume"]) if pd.notna(latest["Volume"]) else 0
    rvol = current_vol / avg_vol if avg_vol > 0 else 0

    candle_range = float(latest["High"] - latest["Low"])
    body = abs(float(latest["Close"] - latest["Open"]))
    body_pct = (body / candle_range * 100) if candle_range > 0 else 0
    bullish_candle = latest["Close"] > latest["Open"]
    bearish_candle = latest["Close"] < latest["Open"]

    rsi = float(calculate_rsi(bars["Close"]).iloc[-1])

    # Daily consolidation: use prior completed sessions, excluding today's bar.
    completed_daily = daily.iloc[:-1] if len(daily) > 2 else daily
    base = completed_daily.tail(5)
    if len(base) < 3:
        return None
    base_high = float(base["High"].max())
    base_low = float(base["Low"].min())
    base_range_pct = ((base_high - base_low) / base_low * 100) if base_low > 0 else 999
    daily_consolidating = base_range_pct <= 6.0

    # Bollinger bandwidth and ATR contraction (daily data).
    daily_close = completed_daily["Close"]
    mid = daily_close.rolling(20).mean()
    std = daily_close.rolling(20).std()
    bb_width = ((4 * std / mid) * 100).iloc[-1] if len(mid.dropna()) else None

    tr = pd.concat([
        completed_daily["High"] - completed_daily["Low"],
        (completed_daily["High"] - completed_daily["Close"].shift()).abs(),
        (completed_daily["Low"] - completed_daily["Close"].shift()).abs(),
    ], axis=1).max(axis=1)
    atr = tr.rolling(14).mean()
    atr_pct = (atr.iloc[-1] / daily_close.iloc[-1] * 100) if len(atr.dropna()) else None

    # Multi-timeframe trend confirmations derived from 5-minute bars.
    tf15 = timeframe_direction(resample_ohlcv(bars, "15min"))
    tf30 = timeframe_direction(resample_ohlcv(bars, "30min"))
    tf60 = timeframe_direction(resample_ohlcv(bars, "60min"))
    tfd = timeframe_direction(completed_daily)

    # Intraday breakout levels: previous 20 completed 5-minute bars.
    bullish_break = ltp > prior_resistance and bullish_candle and body_pct >= 45 and rvol >= 2
    bearish_break = ltp < prior_support and bearish_candle and body_pct >= 45 and rvol >= 2

    # Early warnings close to the range edge with volume beginning to expand.
    near_resistance = ltp >= prior_resistance * 0.995
    near_support = ltp <= prior_support * 1.005
    bullish_warning = daily_consolidating and near_resistance and rvol >= 1.3 and bullish_candle
    bearish_warning = daily_consolidating and near_support and rvol >= 1.3 and bearish_candle

    # Confirm direction across timeframes; these are confirmations, not guarantees.
    bull_tf = sum(x == "BULLISH" for x in [tf15, tf30, tf60, tfd])
    bear_tf = sum(x == "BEARISH" for x in [tf15, tf30, tf60, tfd])

    if bullish_break and rsi >= 52:
        signal, direction = "BREAKOUT CONFIRMED", "BULLISH"
    elif bearish_break and rsi <= 48:
        signal, direction = "BREAKDOWN CONFIRMED", "BEARISH"
    elif bullish_warning:
        signal, direction = "POSSIBLE BREAKOUT", "BULLISH"
    elif bearish_warning:
        signal, direction = "POSSIBLE BREAKDOWN", "BEARISH"
    elif daily_consolidating:
        signal, direction = "WATCH - CONSOLIDATION", "SIDEWAYS"
    elif rvol >= 2 and bullish_candle:
        signal, direction = "UNUSUAL BUYING VOLUME", "BULLISH"
    elif rvol >= 2 and bearish_candle:
        signal, direction = "UNUSUAL SELLING VOLUME", "BEARISH"
    else:
        signal, direction = "NORMAL", "NEUTRAL"

    # Transparent heuristic score; not a probability or guaranteed confidence.
    score = min(100, int(
        min(rvol / 3, 1) * 35
        + min(body_pct / 100, 1) * 20
        + (20 if daily_consolidating else 0)
        + (15 if (bullish_break or bearish_break) else 0)
        + (10 if ((direction == "BULLISH" and bull_tf >= 2) or
                  (direction == "BEARISH" and bear_tf >= 2)) else 0)
    ))

    return {
        "Symbol": symbol.replace(".NS", ""),
        "LTP": round(ltp, 2),
        "Signal": signal,
        "Direction": direction,
        "Change % (5m)": round(float(
            (ltp / float(previous_bars["Close"].iloc[-1]) - 1) * 100
        ), 2) if float(previous_bars["Close"].iloc[-1]) else 0,
        "RVOL": round(rvol, 2),
        "RSI": round(rsi, 1),
        "Daily Base Range %": round(base_range_pct, 2),
        "Support": round(prior_support, 2),
        "Resistance": round(prior_resistance, 2),
        "Momentum Score": score,
        "15m": tf15,
        "30m": tf30,
        "1H": tf60,
        "Daily": tfd,
        "BB Width %": round(float(bb_width), 2) if pd.notna(bb_width) else None,
        "ATR %": round(float(atr_pct), 2) if pd.notna(atr_pct) else None,
    }


@st.cache_data(ttl=180, show_spinner=False)
def scan_momentum_market(symbols):
    """Bulk download in chunks to avoid one HTTP request per ticker."""
    results = []
    errors = 0
    chunk_size = 35

    progress_text = st.empty()
    progress = st.progress(0)
    total_symbols = max(len(symbols), 1)

    for start in range(0, len(symbols), chunk_size):
        chunk = symbols[start:start + chunk_size]
        scanned = min(start + len(chunk), total_symbols)
        percentage = int(scanned / total_symbols * 100)
        progress_text.markdown(
            f"**AI Momentum Scanner: {percentage}%** "
            f"({scanned:,} / {total_symbols:,} stocks)"
        )
        progress.progress(percentage)

        try:
            intraday_raw = yf.download(
                chunk, period="5d", interval="5m",
                group_by="ticker", progress=False, threads=True,
                auto_adjust=True, prepost=False,
            )
            daily_raw = yf.download(
                chunk, period="3mo", interval="1d",
                group_by="ticker", progress=False, threads=True,
                auto_adjust=True, prepost=False,
            )

            for symbol in chunk:
                try:
                    intraday = _extract_symbol_frame(intraday_raw, symbol, chunk)
                    daily = _extract_symbol_frame(daily_raw, symbol, chunk)
                    row = analyze_one_stock(intraday, daily, symbol)
                    if row:
                        results.append(row)
                except Exception:
                    errors += 1
        except Exception:
            errors += len(chunk)

    progress_text.markdown("**AI Momentum Scanner: 100% — Complete**")
    progress.progress(100)
    time.sleep(0.2)
    progress_text.empty()
    progress.empty()
    result = pd.DataFrame(results)
    return result, errors


# -------------------- SESSION STATE --------------------

if "selected_stock" not in st.session_state:
    st.session_state.selected_stock = "RELIANCE"
if "momentum_results" not in st.session_state:
    st.session_state.momentum_results = pd.DataFrame()
if "market_results" not in st.session_state:
    st.session_state.market_results = pd.DataFrame()


# -------------------- NAVIGATION --------------------

st.sidebar.title("📌 OrderBlock Karkhana")
page = st.sidebar.radio("Go to Page", [
    "🚀 SUPER INTRADAY",
    "⚡ Instant Move",
    "📊 Top Volume Stocks",
    "🔥 Intraday Hot Tracker (Pure Market)",
    "📊 Market Flow Dashboard",
    "🧠 AI MOMENTUM & BREAKOUT DETECTOR",
])

st.sidebar.caption(f"NSE symbols loaded: {len(ALL_NSE_SYMBOLS)}")
st.sidebar.caption("Data: Yahoo Finance / yfinance")


def load_market_data():
    with st.spinner("Loading NSE market snapshot..."):
        df = fetch_market_snapshot(ALL_NSE_SYMBOLS)
    st.session_state.market_results = df
    return df


def stock_buttons(frame, prefix, label_type="price"):
    if frame.empty:
        st.info("No stocks available in this section.")
        return
    for _, row in frame.iterrows():
        if label_type == "volume":
            label = f"📊 {row['Symbol']} | Vol {row['Volume_Str']} | ₹{row['LTP']} ({row['P_Change']:+.2f}%)"
        else:
            label = f"{row['Symbol']} | ₹{row['LTP']} ({row['P_Change']:+.2f}%)"
        if st.button(label, key=f"{prefix}_{row['Symbol']}", use_container_width=True):
            st.session_state.selected_stock = row["Symbol"]


# ============================================================
# PAGE 1 - SUPER INTRADAY
# ============================================================

if page == "🚀 SUPER INTRADAY":
    st.title("🚀 SUPER INTRADAY FAST SCANNER")
    st.caption("Top NSE gainers and losers based on latest available daily data.")
    if st.button("🔄 Refresh Market Data", key="refresh_super"):
        fetch_market_snapshot.clear()
        st.rerun()

    df = load_market_data()
    if not df.empty:
        advances = int((df["P_Change"] > 0).sum())
        breadth = advances / len(df) * 100
        market_dir = "BULLISH 🟢" if breadth >= 50 else "BEARISH 🔴"
        a, b, c = st.columns(3)
        a.metric("Market Breadth", market_dir)
        b.metric("Advances", advances)
        c.metric("Scanned", len(df))
        left, right = st.columns(2)
        with left:
            st.subheader("🟢 TOP 20 BULLISH STOCKS")
            stock_buttons(df.sort_values("P_Change", ascending=False).head(20), "super_bull")
        with right:
            st.subheader("🔴 TOP 20 BEARISH STOCKS")
            stock_buttons(df.sort_values("P_Change").head(20), "super_bear")
        st.divider()
        render_better_stock_chart(st.session_state.selected_stock)
    else:
        st.warning("Market data unavailable. Please retry later.")


# ============================================================
# PAGE 2 - INSTANT MOVE
# ============================================================

elif page == "⚡ Instant Move":
    st.title("⚡ INSTANT MOVE SCANNER")
    st.caption("Largest absolute daily price movers from the available NSE universe.")
    if st.button("🔄 Refresh", key="refresh_instant"):
        fetch_market_snapshot.clear()
        st.rerun()
    df = load_market_data()
    if not df.empty:
        movers = df.sort_values("Abs_Move", ascending=False).head(20)
        stock_buttons(movers, "instant_move")
        st.divider()
        render_better_stock_chart(st.session_state.selected_stock)
    else:
        st.warning("Market data unavailable.")


# ============================================================
# PAGE 3 - TOP VOLUME
# ============================================================

elif page == "📊 Top Volume Stocks":
    st.title("📊 TOP 20 HIGH VOLUME STOCKS")
    if st.button("🔄 Refresh", key="refresh_volume"):
        fetch_market_snapshot.clear()
        st.rerun()
    df = load_market_data()
    if not df.empty:
        stock_buttons(df.sort_values("Volume", ascending=False).head(20), "volume", "volume")
        st.divider()
        render_better_stock_chart(st.session_state.selected_stock)
    else:
        st.warning("Market data unavailable.")


# ============================================================
# PAGE 4 - INTRADAY HOT TRACKER
# ============================================================

elif page == "🔥 Intraday Hot Tracker (Pure Market)":
    st.title("🔥 INTRADAY HOT TRACKER")
    if st.button("🔄 Refresh", key="refresh_hot"):
        fetch_market_snapshot.clear()
        st.rerun()
    df = load_market_data()
    if not df.empty:
        advances = int((df["P_Change"] > 0).sum())
        breadth = advances / len(df) * 100
        st.metric("Market Breadth", f"{breadth:.1f}% advances")
        a, b, c = st.columns(3)
        with a:
            st.subheader("⚡ Top Gainers")
            stock_buttons(df.sort_values("P_Change", ascending=False).head(10), "hot_gain")
        with b:
            st.subheader("🔻 Top Losers")
            stock_buttons(df.sort_values("P_Change").head(10), "hot_loss")
        with c:
            st.subheader("📊 Highest Volume")
            stock_buttons(df.sort_values("Volume", ascending=False).head(10), "hot_vol", "volume")
        st.divider()
        st.subheader("Complete scanned market")
        st.dataframe(df.sort_values("Volume", ascending=False), use_container_width=True, hide_index=True)
        render_better_stock_chart(st.session_state.selected_stock)
    else:
        st.warning("Market data unavailable.")


# ============================================================
# PAGE 5 - MARKET FLOW DASHBOARD
# ============================================================

elif page == "📊 Market Flow Dashboard":
    st.title("📊 JARVES TRADING FLOW")
    st.caption("Animated visual only; it is not a live order-flow feed.")
    html_code = """
    <!DOCTYPE html><html><head>
    <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body style="background:#080d18;color:#e5e7eb;font-family:Arial;padding:18px">
      <div style="background:#111c2e;border:1px solid #263449;border-radius:14px;padding:18px">
        <h3 style="font-weight:bold;margin-bottom:12px">MARKET FLOW VISUAL</h3>
        <canvas id="flow" style="width:100%;height:300px"></canvas>
        <p style="color:#94a3b8;font-size:12px">
          Decorative animation only. Connect a broker feed for genuine order-flow data.
        </p>
      </div>
      <script>
        const c=document.getElementById('flow'),x=c.getContext('2d');
        function size(){c.width=c.clientWidth*devicePixelRatio;c.height=300*devicePixelRatio}
        size();window.addEventListener('resize',size);
        let t=0;
        function draw(){
          x.clearRect(0,0,c.width,c.height);t+=0.012;
          for(let i=0;i<9;i++){
            x.beginPath();let col=i%2?'#ff526b':'#00e676';
            x.strokeStyle=col;x.globalAlpha=.55;x.lineWidth=2;
            for(let p=0;p<=100;p++){
              let xx=p/100*c.width;
              let yy=c.height/2+Math.sin(p*.075+t+i)*((15+i*3)*devicePixelRatio)+
                Math.cos(p*.025+t*.7+i)*20*devicePixelRatio;
              if(p===0)x.moveTo(xx,yy);else x.lineTo(xx,yy);
            }x.stroke();
          }x.globalAlpha=1;requestAnimationFrame(draw);
        }draw();
      </script>
    </body></html>
    """
    components.html(html_code, height=390, scrolling=False)


# ============================================================
# PAGE 6 - AI MOMENTUM & BREAKOUT DETECTOR
# ============================================================

else:
    st.title("🧠 AI SUDDEN MOMENTUM & BREAKOUT DETECTOR")
    st.caption(
        "Find possible breakouts and breakdowns after consolidation. "
        "Signals are rule-based technical screens, not AI predictions."
    )

    left, right = st.columns([1, 3])
    with left:
        scan_limit = st.selectbox(
            "Scan universe",
            ["Full NSE list", "First 300 symbols", "First 100 symbols"],
            index=0,
        )
    with right:
        st.info(
            "Full NSE scan can take several minutes and may be rate-limited by Yahoo Finance. "
            "Use a smaller universe to test first."
        )

    symbols_to_scan = ALL_NSE_SYMBOLS
    if scan_limit == "First 300 symbols":
        symbols_to_scan = ALL_NSE_SYMBOLS[:300]
    elif scan_limit == "First 100 symbols":
        symbols_to_scan = ALL_NSE_SYMBOLS[:100]

    if st.button("🚀 SCAN NSE FOR SUDDEN MOVES", type="primary", use_container_width=True):
        scan_momentum_market.clear()
        with st.spinner("Downloading intraday and daily candles. Please wait..."):
            result, errors = scan_momentum_market(symbols_to_scan)
        st.session_state.momentum_results = result
        st.session_state.momentum_scan_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        st.session_state.momentum_errors = errors

    df = st.session_state.momentum_results

    if not df.empty:
        st.caption(
            f"Last scan: {st.session_state.get('momentum_scan_time', 'N/A')} | "
            f"Analysed: {len(df)} | Data errors/skips: "
            f"{st.session_state.get('momentum_errors', 0)}"
        )

        bullish = df[df["Direction"] == "BULLISH"].sort_values("Momentum Score", ascending=False)
        bearish = df[df["Direction"] == "BEARISH"].sort_values("Momentum Score", ascending=False)
        sideways = df[df["Direction"] == "SIDEWAYS"].sort_values("Momentum Score", ascending=False)
        early = df[df["Signal"].isin(["POSSIBLE BREAKOUT", "POSSIBLE BREAKDOWN"])].sort_values(
            "Momentum Score", ascending=False
        )
        unusual = df[df["RVOL"] >= 2].sort_values("RVOL", ascending=False)

        a, b, c, d = st.columns(4)
        a.metric("🟢 Bullish candidates", len(bullish))
        b.metric("🔴 Bearish candidates", len(bearish))
        c.metric("🟡 Consolidating", len(sideways))
        d.metric("⚡ Early warnings", len(early))

        st.subheader("🚀 TOP 10 BULLISH BREAKOUT / MOMENTUM")
        st.dataframe(
            bullish.head(10), use_container_width=True, hide_index=True
        )

        st.subheader("🔻 TOP 10 BEARISH BREAKDOWN / MOMENTUM")
        st.dataframe(
            bearish.head(10), use_container_width=True, hide_index=True
        )

        st.subheader("⚠️ EARLY BREAKOUT / BREAKDOWN WARNINGS")
        st.dataframe(
            early.head(20), use_container_width=True, hide_index=True
        )

        st.subheader("🔥 UNUSUAL VOLUME (RVOL ≥ 2)")
        st.dataframe(
            unusual.head(20), use_container_width=True, hide_index=True
        )

        st.subheader("📦 CONSOLIDATION WATCHLIST")
        st.dataframe(
            sideways.head(20), use_container_width=True, hide_index=True
        )

        st.divider()
        st.subheader("🔎 Detailed stock chart")
        available = sorted(df["Symbol"].dropna().unique().tolist())
        default_index = available.index(st.session_state.selected_stock) if st.session_state.selected_stock in available else 0
        selected = st.selectbox("Choose scanned stock", available, index=default_index)
        st.session_state.selected_stock = selected
        render_better_stock_chart(selected)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download scanner results (CSV)",
            data=csv,
            file_name="orderblock_karkhana_momentum_scan.csv",
            mime="text/csv",
        )
    else:
        st.info("Scanner abhi run nahi hua. NSE scan shuru karne ke liye button dabayein.")

    st.warning(
        "Important: yfinance intraday data delayed, incomplete, unavailable, or rate-limited ho sakta hai. "
        "Latest 5-minute candle ko analysis se exclude kiya gaya hai, lekin results ko broker ke live "
        "chart par verify karein. Scanner automatic buy/sell advice nahi deta."
    )
