import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time

# 1. Page Config
st.set_page_config(
    page_title="Order Block Terminal Pro",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Exact Order-Block.com Futuristic Theme & Glow CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    .stApp {
        background-color: #05070c;
        color: #f3f4f6;
        font-family: 'Inter', sans-serif;
    }
    
    /* Top Header Navbar */
    .top-nav {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #0b0f19;
        padding: 10px 16px;
        border-radius: 8px;
        border: 1px solid #1a2234;
        margin-bottom: 15px;
    }
    
    .nav-tabs {
        display: flex;
        gap: 18px;
        font-size: 13px;
        font-weight: 600;
    }
    
    .tab-active-green { color: #00ff87; border-bottom: 2px solid #00ff87; padding-bottom: 4px; text-shadow: 0 0 8px rgba(0,255,135,0.6); }
    .tab-active-red { color: #ff1744; border-bottom: 2px solid #ff1744; padding-bottom: 4px; text-shadow: 0 0 8px rgba(255,23,68,0.6); }
    .tab-inactive { color: #9ca3af; cursor: pointer; }

    /* Futuristic Setup Cards */
    .card-bullish {
        background: linear-gradient(135deg, rgba(0, 255, 135, 0.05) 0%, rgba(11, 15, 25, 0.9) 100%);
        border: 1px solid rgba(0, 255, 135, 0.4);
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 0 15px rgba(0, 255, 135, 0.15);
        margin-bottom: 15px;
    }
    
    .card-bearish {
        background: linear-gradient(135deg, rgba(255, 23, 68, 0.05) 0%, rgba(11, 15, 25, 0.9) 100%);
        border: 1px solid rgba(255, 23, 68, 0.4);
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 0 15px rgba(255, 23, 68, 0.15);
        margin-bottom: 15px;
    }

    .badge-bull {
        background: rgba(0, 255, 135, 0.15);
        color: #00ff87;
        border: 1px solid #00ff87;
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.5px;
    }

    .badge-bear {
        background: rgba(255, 23, 68, 0.15);
        color: #ff1744;
        border: 1px solid #ff1744;
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.5px;
    }

    .info-grid {
        display: flex;
        justify-content: space-between;
        font-size: 11px;
        color: #9ca3af;
        margin-top: 10px;
        padding-top: 8px;
        border-top: 1px solid rgba(255,255,255,0.05);
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# 3. Top Header & Navigation
st.markdown("""
<div class="top-nav">
    <div style="font-weight: 700; font-size: 16px; color: #ffffff; display: flex; align-items: center; gap: 8px;">
        ⚡ Order Block <span style="width: 8px; height: 8px; background: #00ff87; border-radius: 50%; display: inline-block; box-shadow: 0 0 10px #00ff87;"></span>
    </div>
    <div class="nav-tabs">
        <span class="tab-inactive">MARKET</span>
        <span class="tab-active-green">FLOW</span>
        <span class="tab-inactive">▲ TOP</span>
        <span class="tab-inactive">▼ TOP</span>
    </div>
    <div>
        <span style="background: linear-gradient(135deg, #3b82f6, #1d4ed8); padding: 5px 14px; border-radius: 6px; font-size: 12px; color: #ffffff; font-weight: 600;">Unlock Pro</span>
    </div>
</div>
""", unsafe_allow_html=True)

# 4. Flow Network Section (Matching Order-Block.com Sankey Diagram)[span_6](start_span)[span_6](end_span)
st.markdown("<div style='font-size: 12px; font-weight: 600; color: #9ca3af; margin-bottom: 5px;'>FLOW &bull; LIQUIDITY & ORDER BLOCKS</div>", unsafe_allow_html=True)

# Generate Sankey Flow Chart
labels = ["Market Pool", "RELIANCE", "TCS", "INFY", "HDFCBANK", "SBIN", "ICICIBANK", "Bullish Pool", "Bearish Pool"]
sources = [0, 0, 0, 0, 0, 0, 1, 2, 3, 4, 5, 6]
targets = [1, 2, 3, 4, 5, 6, 7, 7, 8, 8, 7, 8]
values  = [10, 8, 7, 9, 6, 8, 10, 8, 7, 9, 6, 8]
colors  = [
    "rgba(0,255,135,0.3)", "rgba(0,255,135,0.3)", "rgba(255,23,68,0.3)", 
    "rgba(0,255,135,0.3)", "rgba(255,23,68,0.3)", "rgba(0,255,135,0.3)",
    "rgba(0,255,135,0.5)", "rgba(0,255,135,0.5)", "rgba(255,23,68,0.5)",
    "rgba(255,23,68,0.5)", "rgba(0,255,135,0.5)", "rgba(255,23,68,0.5)"
]

fig = go.Figure(data=[go.Sankey(
    node=dict(
        pad=12,
        thickness=15,
        line=dict(color="#000000", width=0.5),
        label=labels,
        color=["#3b82f6"] + ["#1e293b"]*6 + ["#00ff87", "#ff1744"]
    ),
    link=dict(
        source=sources,
        target=targets,
        value=values,
        color=colors
    )
)])

fig.update_layout(
    template="plotly_dark",
    paper_bgcolor="#05070c",
    plot_bgcolor="#05070c",
    height=380,
    margin=dict(l=10, r=10, t=10, b=10)
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("<hr style='border: 0.5px solid #1a2234; margin: 15px 0;'>", unsafe_allow_html=True)

# 5. Detailed Setups & Mini Price Charts (Matching Screenshots)[span_7](start_span)[span_7](end_span)[span_8](start_span)[span_8](end_span)[span_9](start_span)[span_9](end_span)
st.markdown("<div style='font-size: 13px; font-weight: 700; color: #ffffff; margin-bottom: 12px;'>⚡ TOP BULLISH & BEARISH SETUPS</div>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="card-bullish">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <span class="badge-bull">BULLISH</span>
            <span style="font-size: 12px; color: #00ff87; font-weight: 600;">RELIANCE &bull; +2.45%</span>
        </div>
        <div style="font-size: 12px; color: #e5e7eb; font-weight: 600; margin-bottom: 6px;">LONG BUILD-UP</div>
    """, unsafe_allow_html=True)
    
    # Mini Candlestick Chart inside Card
    fig_mini1 = go.Figure(data=[go.Candlestick(
        x=[1,2,3,4,5], open=[100,102,101,105,108], high=[103,104,106,108,110], 
        low=[99,101,100,104,106], close=[102,101,105,108,109],
        increasing_line_color='#00ff87', decreasing_line_color='#ff1744'
    )])
    fig_mini1.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=150, margin=dict(l=0,r=0,t=0,b=0), xaxis_visible=False, yaxis_visible=False)
    st.plotly_chart(fig_mini1, use_container_width=True)
    
    st.markdown("""
        <div class="info-grid">
            <span>ZONE: ₹2,450 - ₹2,480</span>
            <span>SUPPORT: ₹2,420</span>
            <span style="color: #00ff87;">R:R 1:2.5</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="card-bearish">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <span class="badge-bear">BEARISH</span>
            <span style="font-size: 12px; color: #ff1744; font-weight: 600;">INFY &bull; -1.85%</span>
        </div>
        <div style="font-size: 12px; color: #e5e7eb; font-weight: 600; margin-bottom: 6px;">SHORT BUILD-UP</div>
    """, unsafe_allow_html=True)
    
    # Mini Candlestick Chart inside Card
    fig_mini2 = go.Figure(data=[go.Candlestick(
        x=[1,2,3,4,5], open=[150,148,149,145,142], high=[151,149,150,146,143], 
        low=[147,144,145,141,139], close=[148,149,145,142,140],
        increasing_line_color='#00ff87', decreasing_line_color='#ff1744'
    )])
    fig_mini2.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=150, margin=dict(l=0,r=0,t=0,b=0), xaxis_visible=False, yaxis_visible=False)
    st.plotly_chart(fig_mini2, use_container_width=True)
    
    st.markdown("""
        <div class="info-grid">
            <span>ZONE: ₹1,510 - ₹1,530</span>
            <span>RESISTANCE: ₹1,550</span>
            <span style="color: #ff1744;">R:R 1:2.0</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Auto-refresh loop for live flow animation
time.sleep(20)
st.rerun()
