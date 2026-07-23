import streamlit as st # type: ignore[import-not-found]
import streamlit.components.v1 as components # type: ignore[import-not-found]

# 1. Page Configuration
LOGO_URL = "https://96legendssquare.com/wp-content/uploads/2025/08/National-Building-Research-Organization-NBRO.webp"

st.set_page_config(
    page_title="NBRI - IHP Resettlement Progress Dashboard",
    page_icon=LOGO_URL,
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. CSS Reset for Full-screen Dashboard Layout
st.markdown("""
    <style>
        .block-container {
            padding-top: 0rem !important;
            padding-bottom: 0rem !important;
            padding-left: 0rem !important;
            padding-right: 0rem !important;
            max-width: 100% !important;
        }
        header[data-testid="stHeader"] {
            display: none !important;
        }
        footer {
            display: none !important;
        }
    </style>
""", unsafe_allow_html=True)

# 3. HTML, CSS, JS Integrated Dashboard Template
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NBRI - IHP 4700 Resettlement Progress Dashboard</title>
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- FontAwesome Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <!-- Leaflet CSS & JS -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <!-- PapaParse for Live CSV Parsing -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/PapaParse/5.4.1/papaparse.min.js"></script>

    <script>
        tailwind.config = {
            theme: {
                extend: {
                    fontFamily: {
                        sans: ['Plus Jakarta Sans', 'sans-serif'],
                    },
                    colors: {
                        darkBg: '#080a14',
                        cardBg: 'rgba(15, 20, 38, 0.85)',
                        cardBorder: 'rgba(255, 255, 255, 0.08)',
                        accentPurple: '#a855f7',
                        accentBlue: '#3b82f6',
                        accentCyan: '#06b6d4',
                        accentGreen: '#10b981',
                        accentAmber: '#f59e0b',
                    }
                }
            }
        }
    </script>

    <style>
        body {
            font-family: 'Plus Jakarta Sans', sans-serif;
            background: radial-gradient(circle at 20% 20%, #0c1021 0%, #060810 60%, #020307 100%);
            background-attachment: fixed;
            color: #e2e8f0;
            margin: 0;
            padding: 0;
        }

        .glass-panel {
            background: rgba(15, 21, 38, 0.85);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
        }

        .glass-panel-glow {
            background: rgba(20, 28, 50, 0.85);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(168, 85, 247, 0.3);
            box-shadow: 0 0 25px rgba(168, 85, 247, 0.15);
        }

        ::-webkit-scrollbar {
            width: 6px;
            height: 6px;
        }
        ::-webkit-scrollbar-track {
            background: rgba(15, 23, 42, 0.6);
        }
        ::-webkit-scrollbar-thumb {
            background: rgba(100, 116, 139, 0.5);
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: rgba(6, 182, 212, 0.7);
        }

        .glowing-pin {
            display: block;
            width: 14px;
            height: 14px;
            border-radius: 50%;
            background: #06b6d4;
            box-shadow: 0 0 0 0 rgba(6, 182, 212, 0.8);
            animation: pulse-cyan 2s infinite;
        }
        .glowing-pin.completed {
            background: #10b981;
            box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.8);
            animation: pulse-green 2s infinite;
        }
        .glowing-pin.pending {
            background: #f59e0b;
            box-shadow: 0 0 0 0 rgba(245, 158, 11, 0.8);
            animation: pulse-amber 2s infinite;
        }

        @keyframes pulse-cyan {
            0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(6, 182, 212, 0.8); }
            70% { transform: scale(1.3); box-shadow: 0 0 0 12px rgba(6, 182, 212, 0); }
            100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(6, 182, 212, 0); }
        }
        @keyframes pulse-green {
            0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.8); }
            70% { transform: scale(1.3); box-shadow: 0 0 0 12px rgba(16, 185, 129, 0); }
            100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
        }
        @keyframes pulse-amber {
            0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(245, 158, 11, 0.8); }
            70% { transform: scale(1.3); box-shadow: 0 0 0 12px rgba(245, 158, 11, 0); }
            100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(245, 158, 11, 0); }
        }

        .leaflet-container {
            background: #091224 !important;
            font-family: 'Plus Jakarta Sans', sans-serif !important;
        }
        .leaflet-popup-content-wrapper {
            background: rgba(13, 18, 36, 0.95) !important;
            color: #f8fafc !important;
            border: 1px solid rgba(56, 189, 248, 0.4);
            border-radius: 12px !important;
            backdrop-filter: blur(12px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.6);
        }
        .leaflet-popup-tip {
            background: rgba(13, 18, 36, 0.95) !important;
        }
    </style>
</head>
<body class="min-h-screen pb-10">

    <!-- TOP NAVIGATION BAR -->
    <header class="sticky top-0 z-50 glass-panel border-b border-slate-800 px-6 py-3 mb-6">
        <div class="max-w-[1750px] mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
            
            <!-- LOGO & TITLE -->
            <div class="flex items-center gap-3.5">
                <div id="logo-container" class="w-12 h-12 rounded-xl bg-slate-900 border border-slate-700 p-1 flex items-center justify-center shadow-lg shadow-cyan-500/10 overflow-hidden">
                    <img src="{{LOGO_URL}}" alt="NBRO Logo" class="w-full h-full object-contain">
                </div>
                <div>
                    <div class="flex items-center gap-2">
                        <h1 class="text-xl font-bold tracking-tight text-white">NBRI - IHP 4700 RESETTLEMENT DASHBOARD</h1>
                        <span class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                            <span class="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span> Live Tracker Sync
                        </span>
                    </div>
                    <p class="text-xs text-slate-400">Resettlement Progress & Spatial Monitoring of Plantation Estate Sectors</p>
                </div>
            </div>

            <!-- FILTERS & RELOAD -->
            <div class="flex flex-wrap items-center gap-3 w-full md:w-auto">
                <div class="relative flex-1 md:flex-initial">
                    <i class="fa-solid fa-layer-group absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-xs"></i>
                    <select id="filter-region" class="w-full bg-slate-900/90 text-xs text-slate-200 pl-8 pr-8 py-2 rounded-xl border border-slate-700 focus:border-cyan-500 focus:outline-none appearance-none cursor-pointer">
                        <option value="ALL">All Regions</option>
                    </select>
                    <i class="fa-solid fa-chevron-down absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 text-[10px]"></i>
                </div>

                <div class="relative flex-1 md:flex-initial">
                    <i class="fa-solid fa-map-location-dot absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-xs"></i>
                    <select id="filter-district" class="w-full bg-slate-900/90 text-xs text-slate-200 pl-8 pr-8 py-2 rounded-xl border border-slate-700 focus:border-cyan-500 focus:outline-none appearance-none cursor-pointer">
                        <option value="ALL">All Districts</option>
                    </select>
                    <i class="fa-solid fa-chevron-down absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 text-[10px]"></i>
                </div>

                <div class="relative flex-1 md:flex-initial">
                    <i class="fa-solid fa-magnifying-glass absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-xs"></i>
                    <input type="text" id="search-input" placeholder="Search estate or division..." class="w-full bg-slate-900/90 text-xs text-slate-200 pl-8 pr-4 py-2 rounded-xl border border-slate-700 focus:border-cyan-500 focus:outline-none placeholder-slate-500">
                </div>

                <button onclick="fetchCSVData()" class="px-3.5 py-2 bg-purple-600/30 hover:bg-purple-600/50 text-purple-200 border border-purple-500/40 rounded-xl text-xs font-medium transition flex items-center gap-2">
                    <i id="sync-icon" class="fa-solid fa-arrows-rotate"></i> Reload Live CSV
                </button>
            </div>

        </div>
    </header>

    <!-- MAIN CONTAINER -->
    <main class="max-w-[1750px] mx-auto px-4 sm:px-6">

        <!-- KPI GRID -->
        <section class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <div class="glass-panel p-5 rounded-2xl relative overflow-hidden group hover:border-cyan-500/40 transition">
                <div class="flex items-center justify-between mb-3">
                    <span class="text-xs font-medium text-slate-400 uppercase tracking-wider">Total Sites</span>
                    <div class="w-9 h-9 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400">
                        <i class="fa-solid fa-location-dot"></i>
                    </div>
                </div>
                <div class="flex items-baseline gap-3">
                    <h2 id="kpi-total-sites" class="text-3xl font-extrabold text-white">--</h2>
                    <span class="text-xs text-emerald-400 font-semibold flex items-center gap-1">Active Sites</span>
                </div>
                <p class="text-[11px] text-slate-500 mt-2">Monitored resettlement locations</p>
            </div>

            <div class="glass-panel p-5 rounded-2xl relative overflow-hidden group hover:border-blue-500/40 transition">
                <div class="flex items-center justify-between mb-3">
                    <span class="text-xs font-medium text-slate-400 uppercase tracking-wider">Total Units Planned</span>
                    <div class="w-9 h-9 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400">
                        <i class="fa-solid fa-house-chimney"></i>
                    </div>
                </div>
                <div class="flex items-baseline gap-3">
                    <h2 id="kpi-total-units" class="text-3xl font-extrabold text-white">--</h2>
                    <span class="text-xs text-cyan-400 font-semibold">Housing Units</span>
                </div>
                <p class="text-[11px] text-slate-500 mt-2">Aggregated resettlement capacity</p>
            </div>

            <div class="glass-panel p-5 rounded-2xl relative overflow-hidden group hover:border-purple-500/40 transition">
                <div class="flex items-center justify-between mb-3">
                    <span class="text-xs font-medium text-slate-400 uppercase tracking-wider">1st Report Issued</span>
                    <div class="w-9 h-9 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400">
                        <i class="fa-solid fa-file-shield"></i>
                    </div>
                </div>
                <div class="flex items-baseline gap-3">
                    <h2 id="kpi-report-issued" class="text-3xl font-extrabold text-white">--</h2>
                    <span id="kpi-report-pct" class="text-xs text-purple-400 font-semibold">--%</span>
                </div>
                <div class="w-full bg-slate-800 h-1.5 rounded-full mt-3 overflow-hidden">
                    <div id="kpi-report-bar" class="bg-gradient-to-r from-purple-500 to-indigo-500 h-full w-0 transition-all duration-700"></div>
                </div>
            </div>

            <div class="glass-panel p-5 rounded-2xl relative overflow-hidden group hover:border-emerald-500/40 transition">
                <div class="flex items-center justify-between mb-3">
                    <span class="text-xs font-medium text-slate-400 uppercase tracking-wider">BOD Completed</span>
                    <div class="w-9 h-9 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
                        <i class="fa-solid fa-circle-check"></i>
                    </div>
                </div>
                <div class="flex items-baseline gap-3">
                    <h2 id="kpi-bod-completed" class="text-3xl font-extrabold text-white">--</h2>
                    <span id="kpi-bod-pct" class="text-xs text-emerald-400 font-semibold">--%</span>
                </div>
                <p class="text-[11px] text-slate-500 mt-2">Clearance & construction handovers</p>
            </div>
        </section>

        <!-- DASHBOARD BODY -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
            
            <!-- LEFT 8 COLS -->
            <div class="lg:col-span-8 flex flex-col gap-6">
                
                <!-- GIS MAP WITH ESRI WORLD NAVIGATION MAP (DARK BLUE) -->
                <div class="glass-panel rounded-2xl p-5 relative flex flex-col">
                    <div class="flex items-center justify-between mb-4">
                        <div class="flex items-center gap-2.5">
                            <div class="w-3 h-3 rounded-full bg-cyan-400 animate-pulse"></div>
                            <h3 class="text-base font-bold text-white">Esri World Navigation Map (Dark Blue) GIS Tracker</h3>
                        </div>
                        <span id="district-tag" class="hidden text-xs px-3 py-1 rounded-lg bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-lg shadow-cyan-500/10 font-medium">
                            <i class="fa-solid fa-bullseye mr-1 animate-spin"></i> District Boundary Highlighted
                        </span>
                    </div>
                    <div class="w-full h-[450px] rounded-xl overflow-hidden relative border border-slate-800" id="map-container">
                        <div id="map" class="w-full h-full z-10"></div>
                    </div>
                </div>

                <!-- DISTRICT-WISE HOUSING UNIT DISTRIBUTION BAR CHART -->
                <div class="glass-panel rounded-2xl p-5">
                    <div class="flex items-center justify-between mb-4">
                        <div>
                            <h3 class="text-base font-bold text-white flex items-center gap-2">
                                <i class="fa-solid fa-chart-column text-cyan-400 text-sm"></i> District-wise Housing Unit Distribution Visual Chart
                            </h3>
                            <p class="text-xs text-slate-400 mt-0.5">Live graphical visualization of total capacity allocated per district</p>
                        </div>
                        <span class="text-xs font-mono text-cyan-400 bg-cyan-500/10 border border-cyan-500/30 px-2.5 py-1 rounded-lg">
                            <i class="fa-solid fa-chart-bar mr-1"></i> Interactive Chart
                        </span>
                    </div>
                    
                    <div class="relative h-[280px] w-full">
                        <canvas id="districtBarChart"></canvas>
                    </div>
                </div>

                <!-- MAIN SITE DETAILS TABLE -->
                <div class="glass-panel rounded-2xl p-5 overflow-hidden">
                    <div class="flex items-center justify-between mb-4">
                        <h3 class="text-base font-bold text-white flex items-center gap-2">
                            <i class="fa-solid fa-table-cells text-purple-400 text-sm"></i> Resettlement Site Details Registry
                        </h3>
                        <div class="text-xs text-slate-400" id="table-count">Showing 0 sites</div>
                    </div>
                    
                    <div class="max-h-[420px] overflow-y-auto pr-1 border border-slate-800/80 rounded-xl">
                        <table class="w-full text-left text-xs text-slate-300">
                            <thead class="bg-slate-900/95 sticky top-0 z-20 text-slate-400 font-semibold uppercase border-b border-slate-800 backdrop-blur-md">
                                <tr>
                                    <th class="py-3 px-3">S.No</th>
                                    <th class="py-3 px-3">Region</th>
                                    <th class="py-3 px-3">District</th>
                                    <th class="py-3 px-3">Estate / Site</th>
                                    <th class="py-3 px-3">Division</th>
                                    <th class="py-3 px-3 text-right">Units</th>
                                    <th class="py-3 px-3 text-center">1st Report</th>
                                    <th class="py-3 px-3 text-center">BOD</th>
                                    <th class="py-3 px-3 text-center">Report Link</th>
                                </tr>
                            </thead>
                            <tbody id="table-body" class="divide-y divide-slate-800/60 font-medium"></tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- RIGHT 4 COLS -->
            <div class="lg:col-span-4 flex flex-col gap-6">
                
                <!-- CONCEPTUAL LAND SUBDIVISION PLAN STATUS -->
                <div class="glass-panel rounded-2xl p-5">
                    <h3 class="text-base font-bold text-white mb-1 flex items-center gap-2">
                        <i class="fa-solid fa-sitemap text-purple-400 text-sm"></i> Conceptual Land Subdivision Layout
                    </h3>
                    <p class="text-xs text-slate-400 mb-4">Preparation of Zone-Based Resettlement Subdivisions</p>
                    <div class="relative h-[220px] flex items-center justify-center">
                        <canvas id="subdivisionChart"></canvas>
                    </div>
                </div>

                <!-- SELECTED SITE REPORT VIEWER & SPECIFICATIONS CARD -->
                <div class="glass-panel rounded-2xl p-5 border border-cyan-500/30 flex flex-col justify-between">
                    <div>
                        <div class="flex items-center justify-between mb-3">
                            <h3 class="text-sm font-bold text-white flex items-center gap-2">
                                <i class="fa-solid fa-file-pdf text-cyan-400 text-xs"></i> Selected Site Info & Drive Report Link
                            </h3>
                            <span class="text-[10px] text-cyan-300 bg-cyan-500/20 px-2 py-0.5 rounded border border-cyan-500/30">Specs</span>
                        </div>
                        <div id="report-card-content" class="bg-slate-950/80 p-4 rounded-xl border border-slate-800/80 text-xs space-y-2">
                            <p class="text-slate-400 italic">Click on any site row in the table or map pin to inspect its full technical parameters and NBRI PDF report link here.</p>
                        </div>
                    </div>
                    <div id="report-card-action" class="mt-4">
                        <button disabled class="w-full py-2.5 bg-slate-800/80 text-slate-500 rounded-xl text-xs font-semibold flex items-center justify-center gap-2 cursor-not-allowed border border-slate-700/50">
                            <i class="fa-solid fa-arrow-up-right-from-square"></i> Select a Site to Open Official Link
                        </button>
                    </div>
                </div>

                <!-- HSPTD AI ASSISTANT (MOVED TO BOTTOM AS REQUESTED) -->
                <div class="glass-panel-glow rounded-2xl p-5 flex flex-col mt-auto">
                    <div class="flex items-center gap-2.5 mb-3">
                        <div class="w-8 h-8 rounded-lg bg-gradient-to-tr from-purple-600 to-pink-500 flex items-center justify-center text-white text-xs shadow-lg shadow-purple-500/20">
                            <i class="fa-solid fa-wand-magic-sparkles"></i>
                        </div>
                        <div>
                            <h3 class="text-sm font-bold text-white">HSPTD AI Assistant</h3>
                            <p class="text-[10px] text-purple-300">Interactive Resettlement Data Query Bot</p>
                        </div>
                    </div>
                    <div id="ai-chat-box" class="h-[180px] overflow-y-auto space-y-3 p-3 bg-slate-950/80 rounded-xl border border-slate-800 text-xs mb-3">
                        <div class="flex gap-2">
                            <div class="w-6 h-6 rounded-full bg-purple-600 flex-shrink-0 flex items-center justify-center text-[10px] text-white">AI</div>
                            <div class="bg-slate-900/90 text-slate-200 p-2.5 rounded-xl border border-slate-800">
                                Ayubowan! Ask me about estate sites, Google Drive report links, or district stats.
                            </div>
                        </div>
                    </div>
                    <div class="relative">
                        <input type="text" id="ai-input" onkeypress="handleAIPress(event)" placeholder="Ask HSPTD AI..." class="w-full bg-slate-900/90 text-xs text-slate-200 pl-3 pr-10 py-2.5 rounded-xl border border-slate-700 focus:border-purple-500 focus:outline-none">
                        <button onclick="sendAIMessage()" class="absolute right-2 top-1/2 -translate-y-1/2 text-purple-400 hover:text-purple-300 p-1">
                            <i class="fa-solid fa-paper-plane text-xs"></i>
                        </button>
                    </div>
                </div>

            </div>
        </div>
    </main>

    <script>
        // Live Google Sheets published CSV URL
        const DEFAULT_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRGEDtnF-wjT39hcvY3tkA_PpRO1FM06-M267dOBvKYGYlgD-udcevC8LrWGjM_XA/pub?gid=143716875&single=true&output=csv";

        let rawData = [];
        let filteredData = [];
        let mapInstance = null;
        let markersGroup = null;
        let districtHighlightLayer = null;
        let subdivisionChartInstance = null;
        let districtBarChartInstance = null;

        const districtCoordinates = {
            "Rathnapura": { lat: 6.6828, lng: 80.3992 },
            "Badulla": { lat: 6.9934, lng: 81.0550 },
            "Kalutara": { lat: 6.5854, lng: 79.9607 },
            "Kaluthara": { lat: 6.5854, lng: 79.9607 },
            "Kegalle": { lat: 7.2513, lng: 80.3464 },
            "Kandy": { lat: 7.2906, lng: 80.6337 },
            "Nuwara Eliya": { lat: 6.9497, lng: 80.7891 },
            "N'Eliya": { lat: 6.9497, lng: 80.7891 },
            "Galle": { lat: 6.0535, lng: 80.2210 },
            "Matara": { lat: 5.9549, lng: 80.5550 },
            "Hambantota": { lat: 6.1241, lng: 81.1185 },
            "Monaragala": { lat: 6.8718, lng: 81.3487 },
            "Matale": { lat: 7.4675, lng: 80.6234 }
        };

        document.addEventListener('DOMContentLoaded', () => {
            initMap();
            initCharts();
            setupEventListeners();
            fetchCSVData();
        });

        function initMap() {
            mapInstance = L.map('map', { zoomControl: true, attributionControl: false }).setView([6.9, 80.6], 8);
            
            // ESRI WORLD NAVIGATION MAP / DARK GRAY CANVAS BASEMAP
            L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}', {
                maxZoom: 16,
                attribution: 'Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ'
            }).addTo(mapInstance);

            // Esri Reference Labels overlay
            L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Reference/MapServer/tile/{z}/{y}/{x}', {
                maxZoom: 16,
                opacity: 0.7
            }).addTo(mapInstance);

            markersGroup = L.layerGroup().addTo(mapInstance);
            districtHighlightLayer = L.layerGroup().addTo(mapInstance);
        }

        function fetchCSVData() {
            const syncIcon = document.getElementById('sync-icon');
            if (syncIcon) syncIcon.classList.add('fa-spin');

            Papa.parse(DEFAULT_CSV_URL, {
                download: true,
                header: true,
                skipEmptyLines: true,
                complete: function(results) {
                    if (syncIcon) syncIcon.classList.remove('fa-spin');
                    if (results.data && results.data.length > 0) {
                        processCSVRows(results.data);
                    }
                },
                error: function() {
                    if (syncIcon) syncIcon.classList.remove('fa-spin');
                }
            });
        }

        function processCSVRows(rows) {
            rawData = rows.map((r, idx) => {
                const region = r['Region'] || r['region'] || 'Rathnapura';
                const district = r['District'] || r['district'] || region;
                const estate = r['Estate'] || r['estate'] || `Site ${idx+1}`;
                const division = r['Division'] || r['division'] || '-';
                const ia = r["IA's"] || r["IA"] || 'SEC';
                
                let rawUnits = r['Units (2529 List)'] || r['Units (2020 List)'] || r['Units'] || '0';
                if (typeof rawUnits === 'string') rawUnits = rawUnits.replace(/[^0-9]/g, '');
                const units = parseInt(rawUnits) || 0;

                const reportIssued = (r['NBRI 1st Report - Issued'] || r['NBRI 1st Report Issued'] || 'Yes').trim();
                const reportYear = r['NBRI 1st Report - Year '] || r['NBRI 1st Report - Year'] || '2026';
                const bodCompleted = (r['BOD Completed'] || 'No').trim();
                const perimeterSurvey = r['Perimeter Survey'] || 'Yes';
                const droneSurvey = r['Drone Survey'] || 'Completed';
                const conceptualDesign = (r['NBRI Conceptual Design'] || 'In Progress').trim();
                
                // Extraction of actual Google Drive / SharePoint URL link from 'NBRI 1st Report - Link'
                const reportLinkRaw = r['NBRI 1st Report - Link'] || r['NBRI 1st Report- Link'] || r['Report Link'] || '';
                const reportLink = parseReportLink(reportLinkRaw);

                let baseCoords = districtCoordinates[district] || { lat: 6.68, lng: 80.39 };
                let lat = parseFloat(r['Lat'] || r['Latitude']) || (baseCoords.lat + (Math.random() - 0.5) * 0.12);
                let lng = parseFloat(r['Lon'] || r['Longitude']) || (baseCoords.lng + (Math.random() - 0.5) * 0.12);

                return { 
                    sno: idx + 1, region, district, estate, division, ia, units, 
                    reportIssued, reportYear, bodCompleted, perimeterSurvey, droneSurvey, 
                    conceptualDesign, reportLinkRaw, reportLink, lat, lng 
                };
            });

            populateFilterDropdowns();
            applyFilters();
        }

        // Direct Drive / SharePoint URL Link Parser
        function parseReportLink(rawText) {
            if (!rawText || rawText.trim() === '' || rawText.trim() === '-') return '';
            let cleaned = rawText.trim();
            // If raw text is already a URL
            if (cleaned.startsWith('http://') || cleaned.startsWith('https://')) return cleaned;
            // Handle google sheet hyperlink formulas if present
            const match = cleaned.match(/https?:\/\/[^\s"']+/);
            if (match) return match[0];
            return cleaned;
        }

        function populateFilterDropdowns() {
            const regionSelect = document.getElementById('filter-region');
            const districtSelect = document.getElementById('filter-district');

            const regions = [...new Set(rawData.map(d => d.region))].filter(Boolean);
            const districts = [...new Set(rawData.map(d => d.district))].filter(Boolean);

            regionSelect.innerHTML = '<option value="ALL">All Regions</option>' + regions.map(r => `<option value="${r}">${r}</option>`).join('');
            districtSelect.innerHTML = '<option value="ALL">All Districts</option>' + districts.map(d => `<option value="${d}">${d}</option>`).join('');
        }

        function applyFilters() {
            const regionVal = document.getElementById('filter-region').value;
            const districtVal = document.getElementById('filter-district').value;
            const searchVal = document.getElementById('search-input').value.toLowerCase().trim();

            filteredData = rawData.filter(item => {
                const matchRegion = (regionVal === 'ALL' || item.region === regionVal);
                const matchDistrict = (districtVal === 'ALL' || item.district === districtVal);
                const matchSearch = !searchVal || item.estate.toLowerCase().includes(searchVal) || item.division.toLowerCase().includes(searchVal);
                return matchRegion && matchDistrict && matchSearch;
            });

            updateKPIs();
            updateMapMarkers(districtVal);
            updateDistrictBarChart();
            updateCharts();
            renderMainTable();
        }

        function updateKPIs() {
            const totalSites = filteredData.length;
            const totalUnits = filteredData.reduce((acc, curr) => acc + curr.units, 0);
            const reportIssuedCount = filteredData.filter(d => d.reportIssued.toLowerCase() === 'yes').length;
            const bodCompletedCount = filteredData.filter(d => d.bodCompleted.toLowerCase() === 'yes').length;

            const reportPct = totalSites > 0 ? Math.round((reportIssuedCount / totalSites) * 100) : 0;
            const bodPct = totalSites > 0 ? Math.round((bodCompletedCount / totalSites) * 100) : 0;

            document.getElementById('kpi-total-sites').textContent = totalSites;
            document.getElementById('kpi-total-units').textContent = totalUnits.toLocaleString();
            document.getElementById('kpi-report-issued').textContent = reportIssuedCount;
            document.getElementById('kpi-report-pct').textContent = `${reportPct}%`;
            document.getElementById('kpi-report-bar').style.width = `${reportPct}%`;
            document.getElementById('kpi-bod-completed').textContent = bodCompletedCount;
            document.getElementById('kpi-bod-pct').textContent = `${bodPct}%`;
        }

        function updateMapMarkers(selectedDistrict) {
            markersGroup.clearLayers();
            districtHighlightLayer.clearLayers();

            const districtTag = document.getElementById('district-tag');

            // District Highlight Boundary Selection logic
            if (selectedDistrict !== 'ALL') {
                districtTag.classList.remove('hidden');
                
                // Get all points of selected district to highlight entire district cluster
                const districtSites = filteredData.filter(d => d.district === selectedDistrict);
                
                if (districtSites.length > 0) {
                    const lats = districtSites.map(d => d.lat);
                    const lngs = districtSites.map(d => d.lng);
                    const minLat = Math.min(...lats), maxLat = Math.max(...lats);
                    const minLng = Math.min(...lngs), maxLng = Math.max(...lngs);
                    const centerLat = (minLat + maxLat) / 2;
                    const centerLng = (minLng + maxLng) / 2;

                    // Large boundary ring covering all sites in selected district
                    L.circle([centerLat, centerLng], {
                        color: '#38bdf8',
                        fillColor: '#0284c7',
                        fillOpacity: 0.15,
                        radius: 18000,
                        weight: 3,
                        dashArray: '6, 6'
                    }).addTo(districtHighlightLayer);

                    if (mapInstance) mapInstance.flyTo([centerLat, centerLng], 10, { duration: 1.2 });
                }
            } else {
                districtTag.classList.add('hidden');
            }

            if (filteredData.length === 0) return;
            const bounds = [];

            filteredData.forEach(site => {
                const isBod = site.bodCompleted.toLowerCase() === 'yes';
                const isIssued = site.reportIssued.toLowerCase() === 'yes';
                let pinClass = isBod ? 'completed' : (isIssued ? '' : 'pending');

                const customIcon = L.divIcon({
                    className: 'custom-pin-wrapper',
                    html: `<span class="glowing-pin ${pinClass}"></span>`,
                    iconSize: [14, 14],
                    iconAnchor: [7, 7]
                });

                const marker = L.marker([site.lat, site.lng], { icon: customIcon });
                
                let linkButton = (site.reportLink && site.reportLink.startsWith('http')) 
                    ? `<a href="${site.reportLink}" target="_blank" rel="noopener noreferrer" class="inline-block mt-2 px-3 py-1.5 bg-cyan-500/30 text-cyan-200 border border-cyan-400/40 rounded-lg text-xs font-semibold hover:bg-cyan-500/50 transition"><i class="fa-solid fa-file-pdf mr-1"></i> Open NBRI PDF Report</a>`
                    : site.reportLinkRaw 
                        ? `<span class="text-[11px] text-cyan-400 font-semibold block mt-1"><i class="fa-solid fa-link mr-1"></i> ${site.reportLinkRaw}</span>`
                        : '<span class="text-[10px] text-slate-400 mt-1 block">No direct PDF link attached</span>';

                marker.bindPopup(`
                    <div style="font-family:'Plus Jakarta Sans', sans-serif; padding:4px;">
                        <h4 style="font-weight:700; color:#38bdf8; font-size:14px; margin-bottom:6px;">${site.estate}</h4>
                        <p style="font-size:11px; color:#cbd5e1; margin:2px 0;"><b>1. Division:</b> ${site.division}</p>
                        <p style="font-size:11px; color:#cbd5e1; margin:2px 0;"><b>2. Region / District:</b> ${site.region} / ${site.district}</p>
                        <p style="font-size:11px; color:#cbd5e1; margin:2px 0;"><b>3. IA:</b> <span style="color:#a855f7; font-weight:700;">${site.ia}</span></p>
                        <p style="font-size:11px; color:#cbd5e1; margin:2px 0;"><b>4. Planned Capacity:</b> <span style="color:#34d399; font-weight:700;">${site.units} Units</span></p>
                        <p style="font-size:11px; color:#cbd5e1; margin:2px 0;"><b>5. NBRI 1st Report:</b> ${site.reportIssued} (${site.reportYear})</p>
                        <p style="font-size:11px; color:#cbd5e1; margin:2px 0;"><b>6. Perimeter Survey:</b> ${site.perimeterSurvey}</p>
                        <p style="font-size:11px; color:#cbd5e1; margin:2px 0;"><b>7. Drone Survey:</b> ${site.droneSurvey}</p>
                        <p style="font-size:11px; color:#cbd5e1; margin:2px 0;"><b>8. Conceptual Subdivision:</b> ${site.conceptualDesign}</p>
                        <p style="font-size:11px; color:#cbd5e1; margin:2px 0;"><b>9. BOD Clearance:</b> ${site.bodCompleted}</p>
                        <p style="font-size:11px; color:#cbd5e1; margin:4px 0 0 0;"><b>10. Report Link:</b></p>
                        ${linkButton}
                    </div>
                `);

                marker.on('click', () => selectSiteRow(site));
                markersGroup.addLayer(marker);
                bounds.push([site.lat, site.lng]);
            });

            if (selectedDistrict === 'ALL' && bounds.length > 0) {
                mapInstance.fitBounds(bounds, { padding: [30, 30], maxZoom: 12 });
            }
        }

        function initCharts() {
            // CONCEPTUAL SUBDIVISION PLAN CHART
            const ctxSub = document.getElementById('subdivisionChart').getContext('2d');
            subdivisionChartInstance = new Chart(ctxSub, {
                type: 'doughnut',
                data: {
                    labels: ['Completed', 'In Progress', 'Not Required', 'Pending'],
                    datasets: [{
                        data: [0, 0, 0, 0],
                        backgroundColor: ['#10b981', '#06b6d4', '#f59e0b', '#8b5cf6'],
                        borderWidth: 0,
                        hoverOffset: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: '70%',
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: { color: '#cbd5e1', font: { size: 11 } }
                        }
                    }
                }
            });

            // DISTRICT VISUAL BAR CHART
            const ctxBar = document.getElementById('districtBarChart').getContext('2d');
            districtBarChartInstance = new Chart(ctxBar, {
                type: 'bar',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Total Housing Units',
                        data: [],
                        backgroundColor: '#06b6d4',
                        borderColor: '#38bdf8',
                        borderWidth: 1,
                        borderRadius: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: {
                            ticks: { color: '#94a3b8', font: { size: 11 } },
                            grid: { color: 'rgba(255, 255, 255, 0.05)' }
                        },
                        y: {
                            ticks: { color: '#94a3b8', font: { size: 11 } },
                            grid: { color: 'rgba(255, 255, 255, 0.08)' }
                        }
                    },
                    plugins: {
                        legend: { display: false }
                    }
                }
            });
        }

        function updateDistrictBarChart() {
            const districtMap = {};
            filteredData.forEach(item => {
                const dist = item.district || 'Unassigned';
                if (!districtMap[dist]) districtMap[dist] = 0;
                districtMap[dist] += item.units;
            });

            const labels = Object.keys(districtMap);
            const dataValues = Object.values(districtMap);

            districtBarChartInstance.data.labels = labels;
            districtBarChartInstance.data.datasets[0].data = dataValues;
            districtBarChartInstance.update();
        }

        function updateCharts() {
            let completed = 0, inProgress = 0, notRequired = 0, pending = 0;

            filteredData.forEach(item => {
                const status = (item.conceptualDesign || '').toLowerCase();
                if (status.includes('completed')) completed++;
                else if (status.includes('progress')) inProgress++;
                else if (status.includes('not required')) notRequired++;
                else pending++;
            });

            subdivisionChartInstance.data.datasets[0].data = [completed, inProgress, notRequired, pending];
            subdivisionChartInstance.update();
        }

        function renderMainTable() {
            const tbody = document.getElementById('table-body');
            tbody.innerHTML = '';
            document.getElementById('table-count').textContent = `Showing ${filteredData.length} sites`;

            filteredData.forEach(row => {
                const tr = document.createElement('tr');
                tr.className = 'hover:bg-slate-800/60 border-b border-slate-800/40 cursor-pointer transition';
                
                tr.onclick = () => selectSiteRow(row);

                let reportLinkHTML = (row.reportLink && row.reportLink.startsWith('http')) 
                    ? `<a href="${row.reportLink}" target="_blank" rel="noopener noreferrer" onclick="event.stopPropagation();" class="inline-flex items-center gap-1 px-2.5 py-1 rounded-md bg-cyan-500/20 text-cyan-300 hover:bg-cyan-500/40 border border-cyan-500/30 text-[11px] font-semibold transition"><i class="fa-solid fa-file-pdf"></i> View Report</a>`
                    : row.reportLinkRaw 
                        ? `<span class="text-cyan-400 font-mono text-[11px]">${row.reportLinkRaw}</span>`
                        : `<span class="text-slate-600 text-[10px]">N/A</span>`;

                tr.innerHTML = `
                    <td class="py-3 px-3 font-mono text-slate-400">${row.sno}</td>
                    <td class="py-3 px-3 font-semibold text-slate-200">${row.region}</td>
                    <td class="py-3 px-3 text-slate-300">${row.district}</td>
                    <td class="py-3 px-3 font-bold text-cyan-300">${row.estate}</td>
                    <td class="py-3 px-3 text-slate-400">${row.division}</td>
                    <td class="py-3 px-3 text-right font-bold text-emerald-400">${row.units}</td>
                    <td class="py-3 px-3 text-center">${row.reportIssued}</td>
                    <td class="py-3 px-3 text-center">${row.bodCompleted}</td>
                    <td class="py-3 px-3 text-center">${reportLinkHTML}</td>
                `;
                tbody.appendChild(tr);
            });
        }

        function selectSiteRow(site) {
            if (mapInstance && site.lat && site.lng) {
                mapInstance.setView([site.lat, site.lng], 13);
            }

            const content = document.getElementById('report-card-content');
            const action = document.getElementById('report-card-action');

            content.innerHTML = `
                <div class="border-b border-slate-800 pb-2 mb-2">
                    <h4 class="font-extrabold text-cyan-300 text-sm">${site.estate}</h4>
                    <p class="text-[11px] text-slate-400">Division: ${site.division} | IA: <span class="text-purple-300 font-bold">${site.ia}</span></p>
                </div>
                <div class="grid grid-cols-2 gap-x-2 gap-y-1.5 text-[11px] text-slate-300">
                    <div><b>1. District:</b> ${site.district}</div>
                    <div><b>2. Region:</b> ${site.region}</div>
                    <div><b>3. Housing Units:</b> <span class="text-emerald-400 font-bold">${site.units}</span></div>
                    <div><b>4. 1st Report:</b> ${site.reportIssued}</div>
                    <div><b>5. Report Year:</b> ${site.reportYear}</div>
                    <div><b>6. BOD Clearance:</b> ${site.bodCompleted}</div>
                    <div><b>7. Perimeter Survey:</b> ${site.perimeterSurvey}</div>
                    <div><b>8. Drone Survey:</b> ${site.droneSurvey}</div>
                    <div class="col-span-2"><b>9. Conceptual Layout:</b> ${site.conceptualDesign}</div>
                </div>
            `;

            if (site.reportLink && site.reportLink.startsWith('http')) {
                action.innerHTML = `
                    <a href="${site.reportLink}" target="_blank" rel="noopener noreferrer" class="w-full py-2.5 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white rounded-xl text-xs font-bold flex items-center justify-center gap-2 shadow-lg shadow-cyan-500/20 transition">
                        <i class="fa-solid fa-file-pdf"></i> Open Official NBRI PDF Report
                    </a>
                `;
            } else {
                action.innerHTML = `
                    <button disabled class="w-full py-2.5 bg-slate-800 text-slate-500 rounded-xl text-xs font-semibold flex items-center justify-center gap-2 cursor-not-allowed border border-slate-700/50">
                        <i class="fa-solid fa-circle-exclamation"></i> No PDF Link Attached
                    </button>
                `;
            }
        }

        function setupEventListeners() {
            document.getElementById('filter-region').addEventListener('change', applyFilters);
            document.getElementById('filter-district').addEventListener('change', applyFilters);
            document.getElementById('search-input').addEventListener('input', applyFilters);
        }

        function handleAIPress(e) { if (e.key === 'Enter') sendAIMessage(); }
        function sendAIMessage() {
            const input = document.getElementById('ai-input');
            const msg = input.value.trim();
            if (!msg) return;

            const chatBox = document.getElementById('ai-chat-box');
            chatBox.innerHTML += `<div class="flex justify-end mb-2"><div class="bg-purple-600/50 p-2 rounded-xl text-white">${msg}</div></div>`;
            input.value = '';

            setTimeout(() => {
                chatBox.innerHTML += `<div class="flex gap-2 mb-2"><div class="bg-slate-900 p-2 rounded-xl text-slate-200">Filtering active data: <strong>${filteredData.length} sites</strong> matching query. Click any site row or map marker to view detailed specs!</div></div>`;
                chatBox.scrollTop = chatBox.scrollHeight;
            }, 300);
        }
    </script>
</body>
</html>
"""

# 4. Inject LOGO_URL and Render Dashboard
html_dashboard = html_template.replace("{{LOGO_URL}}", LOGO_URL)
components.html(html_dashboard, height=1400, scrolling=True)
