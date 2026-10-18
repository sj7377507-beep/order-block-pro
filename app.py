import streamlit as st
import streamlit.components.v1 as components

# Page configuration
st.set_page_config(page_title="Jarves Trading Dashboard", layout="wide")

# Full HTML, Tailwind & Canvas Animation Dashboard Code
html_code = """
<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Jarves Trading Dashboard</title>
    <!-- Tailwind CSS CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            darkMode: 'class',
            theme: {
                extend: {
                    colors: {
                        darkBg: '#0b0f19',
                        cardBg: '#131b2e',
                        borderCol: '#1e293b',
                        neonGreen: '#00ff7f',
                        neonRed: '#ff3366',
                    }
                }
            }
        }
    </script>
    <!-- FontAwesome for Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        .glow-green { filter: drop-shadow(0 0 6px rgba(0, 255, 127, 0.8)); }
        .glow-red { filter: drop-shadow(0 0 6px rgba(255, 51, 102, 0.8)); }
    </style>
</head>
<body class="bg-darkBg text-slate-200 font-sans antialiased min-h-screen flex flex-col justify-between">

    <!-- Top Header -->
    <header class="flex items-center justify-between px-4 py-3 bg-cardBg border-b border-borderCol">
        <div class="flex items-center space-x-3">
            <button class="text-slate-300 text-xl"><i class="fa-solid fa-bars"></i></button>
            <div class="flex items-center space-x-1 font-bold tracking-wider text-white">
                <i class="fa-solid fa-chart-line text-neonGreen text-xl"></i>
                <span class="text-lg">JARVES <span class="font-light text-slate-400">TRADING</span></span>
            </div>
        </div>
        <div class="flex items-center space-x-3">
            <div class="bg-slate-800 p-1.5 rounded-full flex items-center space-x-2 text-xs">
                <i class="fa-solid fa-sun text-slate-400 px-1"></i>
                <div class="w-7 h-4 bg-neonGreen rounded-full relative p-0.5 cursor-pointer">
                    <div class="w-3 h-3 bg-darkBg rounded-full absolute right-0.5"></div>
                </div>
            </div>
            <button class="bg-gradient-to-r from-blue-600 to-indigo-600 text-white text-xs font-semibold px-3 py-1.5 rounded-full shadow-lg flex items-center space-x-1">
                <i class="fa-solid fa-lock-open text-[10px]"></i>
                <span>Unlock</span>
            </button>
            <button class="text-slate-300 relative">
                <i class="fa-regular fa-bell text-lg"></i>
                <span class="absolute top-0 right-0 w-2 h-2 bg-neonRed rounded-full"></span>
            </button>
        </div>
    </header>

    <!-- Navigation Tabs -->
    <nav class="flex items-center justify-between px-4 bg-cardBg border-b border-borderCol text-sm overflow-x-auto whitespace-nowrap">
        <div class="flex space-x-6">
            <a href="#" class="py-2.5 text-slate-400 hover:text-white font-medium">MARKET</a>
            <a href="#" class="py-2.5 text-neonGreen border-b-2 border-neonGreen font-semibold">FLOW</a>
            <a href="#" class="py-2.5 text-slate-400 hover:text-white font-medium flex items-center space-x-1"><span class="text-neonGreen">&#9650;</span> <span>TOP</span></a>
            <a href="#" class="py-2.5 text-slate-400 hover:text-white font-medium flex items-center space-x-1"><span class="text-neonRed">&#9660;</span> <span>TOP</span></a>
        </div>
        <div class="flex items-center space-x-4 text-slate-300">
            <i class="fa-solid fa-magnifying-glass"></i>
            <i class="fa-solid fa-bars-staggered"></i>
        </div>
    </nav>

    <!-- Main Container -->
    <main class="p-4 space-y-4 max-w-7xl mx-auto w-full flex-grow">
        
        <!-- Ticker Cards Top Bar -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
            <div class="bg-cardBg border border-borderCol p-3 rounded-xl flex justify-between items-center">
                <div>
                    <div class="text-[11px] text-slate-400 font-medium">NIFTY 50</div>
                    <div class="text-base font-bold text-white">24,567.80</div>
                    <div class="text-xs text-neonGreen font-semibold">+142.35 (0.58%)</div>
                </div>
                <div class="text-neonGreen text-xl"><i class="fa-solid fa-chart-line"></i></div>
            </div>
            <div class="bg-cardBg border border-borderCol p-3 rounded-xl flex justify-between items-center">
                <div>
                    <div class="text-[11px] text-slate-400 font-medium">BANKNIFTY</div>
                    <div class="text-base font-bold text-white">52,314.20</div>
                    <div class="text-xs text-neonGreen font-semibold">+298.75 (0.58%)</div>
                </div>
                <div class="text-neonGreen text-xl"><i class="fa-solid fa-chart-line"></i></div>
            </div>
            <div class="bg-cardBg border border-borderCol p-3 rounded-xl flex justify-between items-center">
                <div>
                    <div class="text-[11px] text-slate-400 font-medium">SENSEX</div>
                    <div class="text-base font-bold text-white">80,756.32</div>
                    <div class="text-xs text-neonGreen font-semibold">+428.17 (0.53%)</div>
                </div>
                <div class="text-neonGreen text-xl"><i class="fa-solid fa-chart-line"></i></div>
            </div>
        </div>

        <!-- Dashboard Grid Layout -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
            
            <!-- Market Flow Chart Section with Live Animation -->
            <div class="lg:col-span-2 bg-cardBg border border-borderCol rounded-2xl p-4 flex flex-col justify-between">
                <div class="flex items-center justify-between mb-3">
                    <div class="flex items-center space-x-2">
                        <div class="text-neonGreen"><i class="fa-solid fa-chart-area text-lg"></i></div>
                        <div>
                            <h2 class="font-bold text-sm text-white">MARKET FLOW</h2>
                            <p class="text-[11px] text-slate-400">Real-time Order Flow &bull; NSE</p>
                        </div>
                    </div>
                    <div class="flex items-center space-x-2">
                        <span class="bg-emerald-950 text-neonGreen text-[10px] px-2 py-0.5 rounded-full flex items-center space-x-1 border border-emerald-800">
                            <span class="w-1.5 h-1.5 bg-neonGreen rounded-full animate-pulse"></span>
                            <span>Live</span>
                        </span>
                        <select class="bg-slate-800 text-slate-300 text-xs px-2 py-1 rounded border border-borderCol outline-none">
                            <option>NSE</option>
                            <option>BSE</option>
                        </select>
                    </div>
                </div>

                <!-- Animated Canvas Container -->
                <div class="relative bg-darkBg/80 border border-borderCol rounded-xl h-72 p-3 flex flex-col justify-between overflow-hidden">
                    <div class="absolute left-2 top-2 bottom-2 z-20 flex flex-col justify-between text-[10px] text-slate-400 font-mono pointer-events-none">
                        <span>+4.5%</span>
                        <span>+3.0%</span>
                        <span>+1.5%</span>
                        <span class="text-white font-bold">0.0%</span>
                        <span>-1.5%</span>
                        <span>-3.0%</span>
                        <span>-4.5%</span>
                    </div>
                    
                    <div class="flex justify-between items-start z-20 pl-8 pointer-events-none">
                        <span class="bg-emerald-950/80 text-neonGreen text-[10px] font-semibold px-2.5 py-1 rounded border border-emerald-800">&#9650; BULLISH ZONE</span>
                        <span class="bg-emerald-950/80 text-neonGreen text-[10px] font-semibold px-2.5 py-1 rounded border border-emerald-800">&#9650; TOP</span>
                    </div>

                    <!-- Canvas for Animated Flow Lines -->
                    <canvas id="marketFlowCanvas" class="absolute inset-0 w-full h-full pointer-events-none"></canvas>

                    <div class="flex justify-between items-end z-20 pl-8 pointer-events-none">
                        <span class="bg-rose-950/80 text-neonRed text-[10px] font-semibold px-2.5 py-1 rounded border border-rose-900">&#9660; BEARISH ZONE</span>
                        <span class="bg-rose-950/80 text-neonRed text-[10px] font-semibold px-2.5 py-1 rounded border border-rose-900">&#9660; BOTTOM</span>
                    </div>
                </div>

                <div class="flex items-center justify-between mt-3 text-xs text-slate-400">
                    <div class="flex items-center space-x-4">
                        <span class="flex items-center space-x-1.5"><span class="w-2.5 h-2.5 bg-neonGreen rounded-full"></span><span>Bullish Flow</span></span>
                        <span class="flex items-center space-x-1.5"><span class="w-2.5 h-2.5 bg-neonRed rounded-full"></span><span>Bearish Flow</span></span>
                        <span class="flex items-center space-x-1.5"><span class="w-2.5 h-2.5 bg-blue-500 rounded-full"></span><span>Support / Resistance</span></span>
                    </div>
                </div>
            </div>

            <!-- Top Movers Sidebar -->
            <div class="bg-cardBg border border-borderCol rounded-2xl p-4 flex flex-col justify-between">
                <div>
                    <div class="flex items-center justify-between mb-3">
                        <h3 class="font-bold text-sm text-white flex items-center space-x-2">
                            <i class="fa-solid fa-gear text-neonGreen text-xs"></i>
                            <span>TOP MOVERS</span>
                        </h3>
                    </div>
                    <div class="grid grid-cols-2 bg-darkBg p-1 rounded-xl mb-3 border border-borderCol text-xs font-semibold text-center">
                        <div class="bg-emerald-950 text-neonGreen py-1.5 rounded-lg border border-emerald-800 cursor-pointer">GAINERS</div>
                        <div class="text-slate-400 py-1.5 cursor-pointer hover:text-white">LOSERS</div>
                    </div>

                    <div class="space-y-1.5 text-xs max-h-72 overflow-y-auto pr-1">
                        <div class="flex justify-between text-slate-400 text-[10px] px-1 border-b border-borderCol pb-1">
                            <span># SYMBOL</span>
                            <span>%</span>
                        </div>
                        <div class="flex items-center justify-between bg-darkBg/50 p-1.5 rounded-lg border border-borderCol/50"><div class="flex items-center space-x-2 font-semibold text-white"><span class="text-slate-400 text-[10px]">1</span><span class="w-2 h-2 bg-blue-500 rounded-full"></span><span>RELIANCE</span></div><span class="text-neonGreen font-bold">+3.24% &gt;</span></div>
                        <div class="flex items-center justify-between bg-darkBg/50 p-1.5 rounded-lg border border-borderCol/50"><div class="flex items-center space-x-2 font-semibold text-white"><span class="text-slate-400 text-[10px]">2</span><span class="w-2 h-2 bg-blue-400 rounded-full"></span><span>TCS</span></div><span class="text-neonGreen font-bold">+2.87% &gt;</span></div>
                        <div class="flex items-center justify-between bg-darkBg/50 p-1.5 rounded-lg border border-borderCol/50"><div class="flex items-center space-x-2 font-semibold text-white"><span class="text-slate-400 text-[10px]">3</span><span class="w-2 h-2 bg-indigo-500 rounded-full"></span><span>HDFCBANK</span></div><span class="text-neonGreen font-bold">+2.31% &gt;</span></div>
                        <div class="flex items-center justify-between bg-darkBg/50 p-1.5 rounded-lg border border-borderCol/50"><div class="flex items-center space-x-2 font-semibold text-white"><span class="text-slate-400 text-[10px]">4</span><span class="w-2 h-2 bg-sky-500 rounded-full"></span><span>INFY</span></div><span class="text-neonGreen font-bold">+1.95% &gt;</span></div>
                        <div class="flex items-center justify-between bg-darkBg/50 p-1.5 rounded-lg border border-borderCol/50"><div class="flex items-center space-x-2 font-semibold text-white"><span class="text-slate-400 text-[10px]">5</span><span class="w-2 h-2 bg-red-400 rounded-full"></span><span>ICICIBANK</span></div><span class="text-neonGreen font-bold">+1.82% &gt;</span></div>
                        <div class="flex items-center justify-between bg-darkBg/50 p-1.5 rounded-lg border border-borderCol/50"><div class="flex items-center space-x-2 font-semibold text-white"><span class="text-slate-400 text-[10px]">6</span><span class="w-2 h-2 bg-green-500 rounded-full"></span><span>SBIN</span></div><span class="text-neonGreen font-bold">+1.76% &gt;</span></div>
                        <div class="flex items-center justify-between bg-darkBg/50 p-1.5 rounded-lg border border-borderCol/50"><div class="flex items-center space-x-2 font-semibold text-white"><span class="text-slate-400 text-[10px]">7</span><span class="w-2 h-2 bg-amber-500 rounded-full"></span><span>LT</span></div><span class="text-neonGreen font-bold">+1.62% &gt;</span></div>
                        <div class="flex items-center justify-between bg-darkBg/50 p-1.5 rounded-lg border border-borderCol/50"><div class="flex items-center space-x-2 font-semibold text-white"><span class="text-slate-400 text-[10px]">8</span><span class="w-2 h-2 bg-purple-500 rounded-full"></span><span>AXISBANK</span></div><span class="text-neonGreen font-bold">+1.49% &gt;</span></div>
                        <div class="flex items-center justify-between bg-darkBg/50 p-1.5 rounded-lg border border-borderCol/50"><div class="flex items-center space-x-2 font-semibold text-white"><span class="text-slate-400 text-[10px]">9</span><span class="w-2 h-2 bg-pink-500 rounded-full"></span><span>WIPRO</span></div><span class="text-neonGreen font-bold">+1.32% &gt;</span></div>
                        <div class="flex items-center justify-between bg-darkBg/50 p-1.5 rounded-lg border border-borderCol/50"><div class="flex items-center space-x-2 font-semibold text-white"><span class="text-slate-400 text-[10px]">10</span><span class="w-2 h-2 bg-teal-500 rounded-full"></span><span>TATAMOTORS</span></div><span class="text-neonGreen font-bold">+1.21% &gt;</span></div>
                    </div>
                </div>

                <div class="mt-4 pt-3 border-t border-borderCol">
                    <div class="text-xs font-bold text-white mb-2 flex items-center space-x-1">
                        <i class="fa-solid fa-chart-bar text-neonGreen"></i>
                        <span>MOST ACTIVE</span>
                    </div>
                    <div class="space-y-1.5 text-[11px]">
                        <div class="flex justify-between items-center text-slate-300"><span>RELIANCE</span><div class="w-20 bg-slate-800 h-1.5 rounded-full overflow-hidden"><div class="bg-neonGreen w-4/5 h-full"></div></div><span class="text-slate-400">12.4M</span></div>
                        <div class="flex justify-between items-center text-slate-300"><span>TCS</span><div class="w-20 bg-slate-800 h-1.5 rounded-full overflow-hidden"><div class="bg-neonGreen w-3/5 h-full"></div></div><span class="text-slate-400">8.9M</span></div>
                        <div class="flex justify-between items-center text-slate-300"><span>HDFCBANK</span><div class="w-20 bg-slate-800 h-1.5 rounded-full overflow-hidden"><div class="bg-neonGreen w-1/2 h-full"></div></div><span class="text-slate-400">7.6M</span></div>
                    </div>
                </div>
            </div>

        </div>

        <!-- BULLISH CONTENDERS SECTION -->
        <div class="bg-cardBg border border-borderCol rounded-2xl p-4">
            <div class="flex flex-col sm:flex-row sm:items-center justify-between mb-4 border-b border-borderCol pb-3">
                <div class="flex items-center space-x-2">
                    <div class="text-neonGreen"><i class="fa-solid fa-arrow-trend-up text-lg"></i></div>
                    <div>
                        <h2 class="font-bold text-sm text-white">BULLISH CONTENDERS</h2>
                        <p class="text-[11px] text-slate-400">Strong Flow &bull; Order Blocks &bull; Momentum</p>
                    </div>
                </div>
                <button class="mt-2 sm:mt-0 text-xs text-slate-300 bg-slate-800/80 hover:bg-slate-800 px-3 py-1.5 rounded-lg border border-borderCol flex items-center space-x-1.5">
                    <i class="fa-regular fa-hand-pointer text-[10px] text-neonGreen"></i>
                    <span>Tap a stock</span>
                    <i class="fa-solid fa-arrow-right text-[10px]"></i>
                    <span class="text-slate-400">View Details</span>
                </button>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
                <div class="space-y-2 text-xs">
                    <div class="flex items-center justify-between bg-darkBg/60 p-2.5 rounded-xl border border-borderCol"><div class="flex items-center space-x-2 font-semibold text-white"><span class="w-2.5 h-2.5 bg-blue-500 rounded-full"></span><span>RELIANCE</span></div><span class="text-neonGreen font-bold">+3.24%</span></div>
                    <div class="flex items-center justify-between bg-darkBg/60 p-2.5 rounded-xl border border-borderCol"><div class="flex items-center space-x-2 font-semibold text-white"><span class="w-2.5 h-2.5 bg-blue-400 rounded-full"></span><span>TCS</span></div><span class="text-neonGreen font-bold">+2.87%</span></div>
                    <div class="flex items-center justify-between bg-darkBg/60 p-2.5 rounded-xl border border-borderCol"><div class="flex items-center space-x-2 font-semibold text-white"><span class="w-2.5 h-2.5 bg-indigo-500 rounded-full"></span><span>HDFCBANK</span></div><span class="text-neonGreen font-bold">+2.31%</span></div>
                    <div class="flex items-center justify-between bg-darkBg/60 p-2.5 rounded-xl border border-borderCol"><div class="flex items-center space-x-2 font-semibold text-white"><span class="w-2.5 h-2.5 bg-sky-500 rounded-full"></span><span>INFY</span></div><span class="text-neonGreen font-bold">+1.95%</span></div>
                    <div class="flex items-center justify-between bg-darkBg/60 p-2.5 rounded-xl border border-borderCol"><div class="flex items-center space-x-2 font-semibold text-white"><span class="w-2.5 h-2.5 bg-red-400 rounded-full"></span><span>ICICIBANK</span></div><span class="text-neonGreen font-bold">+1.82%</span></div>
                </div>

                <div class="lg:col-span-2 relative bg-darkBg/80 border border-borderCol rounded-xl h-48 p-3 flex flex-col justify-between overflow-hidden">
                    <div class="flex justify-between items-center z-20">
                        <span class="text-[10px] font-mono text-neonGreen font-semibold tracking-wider">ORDER BLOCK ZONE</span>
                    </div>
                    <canvas id="orderBlockCanvas" class="absolute inset-0 w-full h-full pointer-events-none"></canvas>
                    <div class="absolute right-2 top-2 bottom-2 z-20 flex flex-col justify-between text-[10px] text-slate-400 font-mono text-right pointer-events-none">
                        <span>+4.5%</span>
                        <span>+3.0%</span>
                        <span>+1.5%</span>
                        <span class="text-white font-bold">0.0%</span>
                    </div>
                </div>
            </div>
        </div>

    </main>

    <!-- Bottom Navigation Bar -->
    <footer class="sticky bottom-0 bg-cardBg border-t border-borderCol py-2.5 px-6 flex justify-between items-center text-xs text-slate-400">
        <a href="#" class="flex flex-col items-center text-neonGreen">
            <i class="fa-solid fa-house text-base"></i>
            <span class="text-[10px] mt-0.5">Home</span>
        </a>
        <a href="#" class="flex flex-col items-center hover:text-white">
            <i class="fa-solid fa-magnifying-glass text-base"></i>
            <span class="text-[10px] mt-0.5">Scanner</span>
        </a>
        <a href="#" class="flex flex-col items-center hover:text-white">
            <i class="fa-regular fa-star text-base"></i>
            <span class="text-[10px] mt-0.5">Watchlist</span>
        </a>
        <a href="#" class="flex flex-col items-center hover:text-white">
            <i class="fa-solid fa-briefcase text-base"></i>
            <span class="text-[10px] mt-0.5">Portfolio</span>
        </a>
        <a href="#" class="flex flex-col items-center hover:text-white">
            <i class="fa-solid fa-gear text-base"></i>
            <span class="text-[10px] mt-0.5">Settings</span>
        </a>
    </footer>

    <!-- JavaScript for Live Flow Animation -->
    <script>
        function initCanvas(canvasId, isBicolor = true) {
            const canvas = document.getElementById(canvasId);
            if (!canvas) return;
            const ctx = canvas.getContext('2d');

            function resize() {
                canvas.width = canvas.offsetWidth;
                canvas.height = canvas.offsetHeight;
            }
            resize();
            window.addEventListener('resize', resize);

            // Generate particles/lines
            const streams = [];
            const count = 25;
            for (let i = 0; i < count; i++) {
                streams.push({
                    yStart: canvas.height / 2,
                    yEnd: Math.random() * canvas.height,
                    progress: Math.random(),
                    speed: 0.003 + Math.random() * 0.005,
                    color: isBicolor ? (Math.random() > 0.5 ? '#00ff7f' : '#ff3366') : '#00ff7f',
                    amplitude: (Math.random() - 0.5) * 50
                });
            }

            function animate() {
                ctx.clearRect(0, 0, canvas.width, canvas.height);

                // Draw central axis line
                ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)';
                ctx.lineWidth = 1;
                ctx.beginPath();
                ctx.moveTo(50, canvas.height / 2);
                ctx.lineTo(canvas.width - 50, canvas.height / 2);
                ctx.stroke();

                // Animate curves
                streams.forEach(s => {
                    s.progress += s.speed;
                    if (s.progress > 1) s.progress = 0;

                    ctx.strokeStyle = s.color;
                    ctx.lineWidth = 1.5;
                    ctx.shadowColor = s.color;
                    ctx.shadowBlur = 8;
                    
                    ctx.beginPath();
                    ctx.moveTo(50, canvas.height / 2);
                    
                    let cpX = canvas.width * 0.5;
                    let cpY = (canvas.height / 2 + s.yEnd) / 2 + s.amplitude;
                    let targetX = canvas.width - 60;
                    
                    ctx.quadraticCurveTo(cpX, cpY, targetX, s.yEnd);
                    ctx.stroke();
                    ctx.shadowBlur = 0; // reset

                    // Draw moving particle node
                    let t = s.progress;
                    let x = (1-t)*(1-t)*50 + 2*(1-t)*t*cpX + t*t*targetX;
                    let y = (1-t)*(1-t)*(canvas.height/2) + 2*(1-t)*t*cpY + t*t*s.yEnd;

                    ctx.fillStyle = '#ffffff';
                    ctx.shadowColor = s.color;
                    ctx.shadowBlur = 10;
                    ctx.beginPath();
                    ctx.arc(x, y, 2.5, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.shadowBlur = 0;
                });

                requestAnimationFrame(animate);
            }
            animate();
        }

        window.onload = () => {
            initCanvas('marketFlowCanvas', true);
            initCanvas('orderBlockCanvas', false);
        };
    </script>
</body>
</html>
"""

# Render full HTML component in Streamlit
components.html(html_code, height=1100, scrolling=True)
