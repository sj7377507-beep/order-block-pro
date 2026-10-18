import streamlit as st

# Page configuration
st.set_page_config(page_title="Jarves Trading Dashboard", layout="wide")

# HTML and Tailwind Dashboard Code
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

    </main>
</body>
</html>
"""

# Render in Streamlit
st.markdown(html_code, unsafe_allow_html=True)
