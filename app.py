import streamlit as st
import streamlit.components.v1 as components

# Page configuration
st.set_page_config(page_title="Jarves Trading Dashboard", layout="wide")

# Full HTML and Tailwind Dashboard Code
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
    <nav class="flex space-x-6 px-4 bg-cardBg border-b border-borderCol text-sm overflow-x-auto whitespace-nowrap">
        <a href="#" class="py-2.5 text-slate-400 hover:text-white font-medium">MARKET</a>
        <a href="#" class="py-2.5 text-neonGreen border-b-2 border-neonGreen font-semibold">FLOW</a>
        <a href="#" class="py-2.5 text-slate-400 hover:text-white font-medium flex items-center space-x-1"><span class="text-neonGreen">&#9650;</span> <span>TOP</span></a>
        <a href="#" class="py-2.5 text-slate-400 hover:text-white font-medium flex items-center space-x-1"><span class="text-neonRed">&#9660;</span> <span>TOP</span></a>
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
            
            <!-- Market Flow Chart Section -->
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

                <div class="relative bg-darkBg/60 border border-borderCol rounded-xl h-64 p-3 flex flex-col justify-between overflow-hidden">
                    <div class="absolute left-2 top-2 bottom-2 flex flex-col justify-between text-[10px] text-slate-400 font-mono">
                        <span>+4.5%</span>
                        <span>+3.0%</span>
                        <span>+1.5%</span>
                        <span class="text-white font-bold">0.0%</span>
                        <span>-1.5%</span>
                        <span>-3.0%</span>
                        <span>-4.5%</span>
                    </div>
                    
                    <div class="flex justify-between items-start z-10 pl-8">
                        <span class="bg-emerald-950/80 text-neonGreen text-[10px] font-semibold px-2.5 py-1 rounded border border-emerald-800">&#9650; BULLISH ZONE</span>
                        <span class="bg-emerald-950/80 text-neonGreen text-[10px] font-semibold px-2.5 py-1 rounded border border-emerald-800">&#9650; TOP</span>
                    </div>

                    <div class="flex justify-between items-end z-10 pl-8">
                        <span class="bg-rose-950/80 text-neonRed text-[10px] font-semibold px-2.5 py-1 rounded border border-rose-900">&#9660; BEARISH ZONE</span>
                        <span class="bg-rose-950/80 text-neonRed text-[10px] font-semibold px-2.5 py-1 rounded border border-rose-900">&#9660; BOTTOM</span>
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

                    <div class="space-y-2 text-xs">
                        <div class="flex justify-between text-slate-400 text-[10px] px-1 border-b border-borderCol pb-1">
                            <span># SYMBOL</span>
                            <span>%</span>
                        </div>
                        <div class="flex items-center justify-between bg-darkBg/50 p-2 rounded-lg border border-borderCol/50">
                            <div class="flex items-center space-x-2 font-semibold text-white">
                                <span class="text-slate-400 text-[10px]">1</span>
                                <span class="w-2 h-2 bg-blue-500 rounded-full"></span>
                                <span>RELIANCE</span>
                            </div>
                            <span class="text-neonGreen font-bold">+3.24%</span>
                        </div>
                        <div class="flex items-center justify-between bg-darkBg/50 p-2 rounded-lg border border-borderCol/50">
                            <div class="flex items-center space-x-2 font-semibold text-white">
                                <span class="text-slate-400 text-[10px]">2</span>
                                <span class="w-2 h-2 bg-blue-400 rounded-full"></span>
                                <span>TCS</span>
                            </div>
                            <span class="text-neonGreen font-bold">+2.87%</span>
                        </div>
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

</body>
</html>
"""

# Render full HTML component in Streamlit
components.html(html_code, height=900, scrolling=True)
