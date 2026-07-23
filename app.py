import streamlit as st  # type: ignore[import-not-found]
import streamlit.components.v1 as components  # type: ignore[import-not-found]

# 1. Page Configuration
LOGO_URL = "https://96legendssquare.com/wp-content/uploads/2025/08/National-Building-Research-Organization-NBRO.webp"

st.set_page_config(
    page_title="NBRI - IHP Progress Dashboard",
    page_icon=LOGO_URL,
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Remove default Streamlit whitespace/padding
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

# 3. HTML, CSS, JS Dashboard Template
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NBRI - IHP 4700 Resettlement & Progress Dashboard</title>
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
    <!-- PapaParse for CSV handling -->
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
                        cardBg: 'rgba(18, 24, 43, 0.8)',
                        cardBorder: 'rgba(255, 255, 255, 0.08)',
                        accentPurple: '#a855f7',
                        accentBlue: '#3b82f6',
                        accentCyan: '#06b6d4',
                        accentGreen: '#10b981',
                    }
                }
            }
        }
    </script>

    <style>
        body {
            font-family: 'Plus Jakarta Sans', sans-serif;
            background: radial-gradient(circle at 20% 20%, #0d1226 0%, #080a14 60%, #04050a 100%);
            background-attachment: fixed;
            color: #e2e8f0;
            margin: 0;
            padding: 0;
        }

        .glass-panel {
            background: rgba(15, 20, 38, 0.85);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
        }

        .glass-panel-glow {
            background: rgba(20, 26, 48, 0.85);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(168, 85, 247, 0.25);
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
            background: rgba(168, 85, 247, 0.7);
        }

        .glowing-pin {
            display: block;
            width: 14px;
            height: 14px;
            border-radius: 50%;
            background: #06b6d4;
            box-shadow: 0 0 0 0 rgba(6, 182, 212, 0.7);
            animation: pulse-cyan 2s infinite;
        }
        .glowing-pin.completed {
            background: #10b981;
            box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
            animation: pulse-green 2s infinite;
        }
        .glowing-pin.pending {
            background: #f59e0b;
            box-shadow: 0 0 0 0 rgba(245, 158, 11, 0.7);
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

        .leaflet-container {
            background: #080d1a !important;
            font-family: 'Plus Jakarta Sans', sans-serif !important;
        }
        .leaflet-popup-content-wrapper {
            background: rgba(15, 23, 42, 0.95) !important;
            color: #f8fafc !important;
            border: 1px solid rgba(56, 189, 248, 0.3);
            border-radius: 12px !important;
            backdrop-filter: blur(10px);
        }
        .leaflet-popup-tip {
            background: rgba(15, 23, 42, 0.95) !important;
        }
    </style>
</head>
<body class="min-h-screen pb-10">

    <!-- TOP NAVIGATION BAR -->
    <header class="sticky top-0 z-50 glass-panel border-b border-slate-800/80 px-6 py-3 mb-6">
        <div class="max-w-[1700px] mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
            
            <!-- LOGO & TITLE -->
            <div class="flex items-center gap-3.5">
                <div id="logo-container" class="w-12 h-12 rounded-xl bg-slate-900 border border-slate-700/80 p-1 flex items-center justify-center shadow-lg shadow-cyan-500/10 overflow-hidden">
                    <img src="{{LOGO_URL}}" alt="NBRO Logo" class="w-full h-full object-contain">
                </div>
                <div>
                    <div class="flex items-center gap-2">
                        <h1 class="text-xl font-bold tracking-tight text-white">NBRI - IHP PROGRESS Dashboard</h1>
                        <span class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                            <span class="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span> Live Sync
                        </span>
                    </div>
                    <p class="text-xs text-slate-400">Resettlement of 4700 Families in the Estate Sector Under the Indian Housing Project (IHP)</p>
                </div>
            </div>

            <!-- FILTERS -->
            <div class="flex flex-wrap items-center gap-3 w-full md:w-auto">
                <div class="relative flex-1 md:flex-initial">
                    <i class="fa-solid fa-location-dot absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-xs"></i>
                    <select id="filter-region" class="w-full bg-slate-900/90 text-xs text-slate-200 pl-8 pr-8 py-2 rounded-xl border border-slate-700/60 focus:border-cyan-500 focus:outline-none appearance-none cursor-pointer">
                        <option value="ALL">All Regions</option>
                    </select>
                    <i class="fa-solid fa-chevron-down absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 text-[10px]"></i>
                </div>

                <div class="relative flex-1 md:flex-initial">
                    <i class="fa-solid fa-map absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-xs"></i>
                    <select id="filter-district" class="w-full bg-slate-900/90 text-xs text-slate-200 pl-8 pr-8 py-2 rounded-xl border border-slate-700/60 focus:border-cyan-500 focus:outline-none appearance-none cursor-pointer">
                        <option value="ALL">All Districts</option>
                    </select>
                    <i class="fa-solid fa-chevron-down absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 text-[10px]"></i>
                </div>

                <div class="relative flex-1 md:flex-initial">
                    <i class="fa-solid fa-magnifying-glass absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-xs"></i>
                    <input type="text" id="search-input" placeholder="Search estate or division..." class="w-full bg-slate-900/90 text-xs text-slate-200 pl-8 pr-4 py-2 rounded-xl border border-slate-700/60 focus:border-cyan-500 focus:outline-none placeholder-slate-500">
                </div>

                <button onclick="fetchCSVData()" class="px-3.5 py-2 bg-purple-600/30 hover:bg-purple-600/50 text-purple-200 border border-purple-500/40 rounded-xl text-xs font-medium transition flex items-center gap-2">
                    <i id="sync-icon" class="fa-solid fa-arrows-rotate"></i> Reload CSV
                </button>
            </div>

        </div>
    </header>

    <!-- MAIN CONTAINER -->
    <main class="max-w-[1700px] mx-auto px-4 sm:px-6">

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
                    <span class="text-xs text-emerald-400 font-semibold flex items-center gap-1">Active</span>
                </div>
                <p class="text-[11px] text-slate-500 mt-2">Monitored resettlement locations</p>
            </div>

            <div class="glass-panel p-5 rounded-2xl relative overflow-hidden group hover:border-blue-500/40 transition">
                <div class="flex items-center justify-between mb-3">
                    <span class="text-xs font-medium text-slate-400 uppercase tracking-wider">Total Units Planned</span>
                    <div class="w-9 h-9 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400">
                        <i class="fa-solid fa-building"></i>
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
                        <i class="fa-solid fa-file-invoice"></i>
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
                <!-- GIS MAP -->
                <div class="glass-panel rounded-2xl p-5 relative flex flex-col">
                    <div class="flex items-center justify-between mb-4">
                        <div class="flex items-center gap-2.5">
                            <div class="w-3 h-3 rounded-full bg-cyan-400 animate-pulse"></div>
                            <h3 class="text-base font-bold text-white">Interactive Site Location GIS Map</h3>
                        </div>
                        <span id="district-tag" class="hidden text-xs px-2.5 py-1 rounded-lg bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
                            <i class="fa-solid fa-bullseye mr-1"></i> Highlighted District
                        </span>
                    </div>
                    <div class="w-full h-[400px] rounded-xl overflow-hidden relative border border-slate-800" id="map-container">
                        <div id="map" class="w-full h-full z-10"></div>
                    </div>
                </div>

                <!-- BAR CHART -->
                <div class="glass-panel rounded-2xl p-5">
                    <h3 class="text-base font-bold text-white mb-4 flex items-center gap-2">
                        <i class="fa-solid fa-chart-column text-cyan-400 text-sm"></i> Region-wise Housing Unit Distribution
                    </h3>
                    <div class="h-[270px] w-full">
                        <canvas id="barChart"></canvas>
                    </div>
                </div>

                <!-- TABLE WITH SCROLLABLE WRAPPER (Fixes right side height black space) -->
                <div class="glass-panel rounded-2xl p-5 overflow-hidden">
                    <div class="flex items-center justify-between mb-4">
                        <h3 class="text-base font-bold text-white flex items-center gap-2">
                            <i class="fa-solid fa-table text-purple-400 text-sm"></i> Resettlement Site Details
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
                                    <th class="py-3 px-3 text-center">NBRI Report</th>
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
                <!-- DOUGHNUT CHART -->
                <div class="glass-panel rounded-2xl p-5">
                    <h3 class="text-base font-bold text-white mb-1 flex items-center gap-2">
                        <i class="fa-solid fa-chart-pie text-purple-400 text-sm"></i> NBRI Report Status
                    </h3>
                    <p class="text-xs text-slate-400 mb-4">1st Clearance Report Issued vs Pending</p>
                    <div class="relative h-[210px] flex items-center justify-center">
                        <canvas id="doughnutChart"></canvas>
                    </div>
                </div>

                <!-- AI ASSISTANT -->
                <div class="glass-panel-glow rounded-2xl p-5 flex flex-col">
                    <div class="flex items-center gap-2 mb-3">
                        <div class="w-8 h-8 rounded-lg bg-gradient-to-tr from-purple-600 to-pink-500 flex items-center justify-center text-white text-xs shadow-lg shadow-purple-500/20">
                            <i class="fa-solid fa-wand-magic-sparkles"></i>
                        </div>
                        <div>
                            <h3 class="text-sm font-bold text-white">HSPTD AI Assistant</h3>
                            <p class="text-[10px] text-purple-300">Resettlement Data Bot</p>
                        </div>
                    </div>
                    <div id="ai-chat-box" class="h-[200px] overflow-y-auto space-y-3 p-3 bg-slate-950/70 rounded-xl border border-slate-800/80 text-xs mb-3">
                        <div class="flex gap-2">
                            <div class="w-6 h-6 rounded-full bg-purple-600 flex-shrink-0 flex items-center justify-center text-[10px] text-white">AI</div>
                            <div class="bg-slate-900/90 text-slate-200 p-2.5 rounded-xl border border-slate-800">
                                Ayubowan! Ask me anything about resettlement sites, report links, or district stats.
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

                <!-- SELECTED SITE REPORT VIEWER CARD (Fills remaining right-column empty space) -->
                <div class="glass-panel rounded-2xl p-5 border border-cyan-500/20 flex flex-col justify-between">
                    <div>
                        <div class="flex items-center justify-between mb-3">
                            <h3 class="text-sm font-bold text-white flex items-center gap-2">
                                <i class="fa-solid fa-file-pdf text-cyan-400 text-xs"></i> Site Report Viewer
                            </h3>
                            <span class="text-[10px] text-cyan-400 bg-cyan-500/10 px-2 py-0.5 rounded border border-cyan-500/20">Active Selection</span>
                        </div>
                        <div id="report-card-content" class="bg-slate-900/80 p-4 rounded-xl border border-slate-800 text-xs space-y-2">
                            <p class="text-slate-400 italic">Click on any site row in the table to view its NBRI 1st Report link and specific site stats here.</p>
                        </div>
                    </div>
                    <div id="report-card-action" class="mt-4">
                        <button disabled class="w-full py-2.5 bg-slate-800/80 text-slate-500 rounded-xl text-xs font-semibold flex items-center justify-center gap-2 cursor-not-allowed border border-slate-700/50">
                            <i class="fa-solid fa-arrow-up-right-from-square"></i> Select a Site to Open Report
                        </button>
                    </div>
                </div>

            </div>
        </div>
    </main>

    <script>
        const DEFAULT_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRGEDtnF-wjT39hcvY3tkA_PpRO1FM06-M267dOBvKYGYlgD-udcevC8LrWGjM_XA/pub?gid=143716875&single=true&output=csv";

        let rawData = [];
        let filteredData = [];
        let mapInstance = null;
        let markersGroup = null;
        let districtHighlightLayer = null;
        let barChartInstance = null;
        let doughnutChartInstance = null;

        const districtCoordinates = {
            "Rathnapura": { lat: 6.6828, lng: 80.3992 },
            "Badulla": { lat: 6.9934, lng: 81.0550 },
            "Kalutara": { lat: 6.5854, lng: 79.9607 },
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
            mapInstance = L.map('map', { zoomControl: true, attributionControl: false }).setView([6.75, 80.45], 9);
            
            // CARTO Dark Basemap Tile with Deep Blue styling
            L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
                maxZoom: 18,
                subdomains: 'abcd'
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
                
                // Safe parseInt cleaning non-digit characters
                let rawUnits = r['Units (2020 List)'] || r['Units'] || r['units'] || '0';
                if (typeof rawUnits === 'string') rawUnits = rawUnits.replace(/[^0-9]/g, '');
                const units = parseInt(rawUnits) || 0;

                const reportIssued = (r['NBRI 1st Report Issued'] || r['1st Report Issued'] || 'Yes').trim();
                const bodCompleted = (r['BOD Completed'] || r['BOD'] || 'None').trim();
                
                // Read 'NBRI 1st Report - Link' column
                const reportLink = r['NBRI 1st Report - Link'] || r['Report Link'] || r['NBRI Report Link'] || r['Link'] || r['report_link'] || '';

                let baseCoords = districtCoordinates[district] || { lat: 6.68, lng: 80.39 };
                let lat = parseFloat(r['Latitude']) || (baseCoords.lat + (Math.random() - 0.5) * 0.12);
                let lng = parseFloat(r['Longitude']) || (baseCoords.lng + (Math.random() - 0.5) * 0.12);

                return { sno: idx + 1, region, district, estate, division, units, reportIssued, bodCompleted, reportLink, lat, lng };
            });

            populateFilterDropdowns();
            applyFilters();
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
            updateCharts();
            renderTable();
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

            // Highlight Selected District with Blue Glow Ring
            if (selectedDistrict !== 'ALL' && districtCoordinates[selectedDistrict]) {
                const coords = districtCoordinates[selectedDistrict];
                districtTag.classList.remove('hidden');
                
                L.circle([coords.lat, coords.lng], {
                    color: '#38bdf8',
                    fillColor: '#0284c7',
                    fillOpacity: 0.18,
                    radius: 12000,
                    weight: 2,
                    dashArray: '6, 6'
                }).addTo(districtHighlightLayer);
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
                
                let linkButton = site.reportLink 
                    ? `<a href="${site.reportLink}" target="_blank" class="inline-block mt-2 px-2.5 py-1 bg-cyan-500/30 text-cyan-200 border border-cyan-400/40 rounded text-[11px] font-semibold hover:bg-cyan-500/50"><i class="fa-solid fa-file-pdf mr-1"></i> View NBRI Report</a>`
                    : '<span class="text-[10px] text-slate-400 mt-1 block">No report link attached</span>';

                marker.bindPopup(`
                    <div style="font-family:'Plus Jakarta Sans', sans-serif;">
                        <h4 style="font-weight:700; color:#38bdf8; font-size:13px; margin-bottom:4px;">${site.estate}</h4>
                        <p style="font-size:11px; color:#cbd5e1; margin:2px 0;"><b>Region:</b> ${site.region} | <b>District:</b> ${site.district}</p>
                        <p style="font-size:11px; color:#cbd5e1; margin:2px 0;"><b>Division:</b> ${site.division}</p>
                        <p style="font-size:11px; color:#cbd5e1; margin:2px 0;"><b>Housing Units:</b> <span style="color:#34d399; font-weight:700;">${site.units}</span></p>
                        ${linkButton}
                    </div>
                `);
                
                markersGroup.addLayer(marker);
                bounds.push([site.lat, site.lng]);
            });

            if (bounds.length > 0) mapInstance.fitBounds(bounds, { padding: [30, 30], maxZoom: 12 });
        }

        function initCharts() {
            // REGION-WISE BAR CHART
            const ctxBar = document.getElementById('barChart').getContext('2d');
            barChartInstance = new Chart(ctxBar, {
                type: 'bar',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Housing Units',
                        data: [],
                        backgroundColor: [
                            'rgba(6, 182, 212, 0.85)',
                            'rgba(59, 130, 246, 0.85)',
                            'rgba(168, 85, 247, 0.85)',
                            'rgba(16, 185, 129, 0.85)',
                            'rgba(245, 158, 11, 0.85)',
                            'rgba(236, 72, 153, 0.85)',
                            'rgba(99, 102, 241, 0.85)'
                        ],
                        borderColor: 'rgba(255, 255, 255, 0.1)',
                        borderWidth: 1,
                        borderRadius: 8
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        x: {
                            ticks: { color: '#94a3b8', font: { size: 11 } },
                            grid: { color: 'rgba(255, 255, 255, 0.05)' }
                        },
                        y: {
                            ticks: { color: '#94a3b8', font: { size: 11 } },
                            grid: { color: 'rgba(255, 255, 255, 0.05)' }
                        }
                    }
                }
            });

            // DOUGHNUT CHART
            const ctxDoughnut = document.getElementById('doughnutChart').getContext('2d');
            doughnutChartInstance = new Chart(ctxDoughnut, {
                type: 'doughnut',
                data: {
                    labels: ['Report Issued', 'Pending'],
                    datasets: [{
                        data: [0, 0],
                        backgroundColor: ['#06b6d4', '#f59e0b'],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: '72%',
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: { color: '#cbd5e1', font: { size: 11 } }
                        }
                    }
                }
            });
        }

        function updateCharts() {
            // Group data by REGION for the bar chart
            const regionMap = {};
            filteredData.forEach(item => {
                const key = item.region || item.district || 'Unassigned';
                regionMap[key] = (regionMap[key] || 0) + item.units;
            });

            barChartInstance.data.labels = Object.keys(regionMap);
            barChartInstance.data.datasets[0].data = Object.values(regionMap);
            barChartInstance.update();

            // Doughnut chart update
            const issuedCount = filteredData.filter(d => d.reportIssued.toLowerCase() === 'yes').length;
            doughnutChartInstance.data.datasets[0].data = [issuedCount, filteredData.length - issuedCount];
            doughnutChartInstance.update();
        }

        function renderTable() {
            const tbody = document.getElementById('table-body');
            tbody.innerHTML = '';
            document.getElementById('table-count').textContent = `Showing ${filteredData.length} sites`;

            filteredData.forEach(row => {
                const tr = document.createElement('tr');
                tr.className = 'hover:bg-slate-800/60 border-b border-slate-800/40 cursor-pointer transition';
                
                // Clicking a row centers map and loads report card below AI assistant
                tr.onclick = () => selectSiteRow(row);

                let reportLinkHTML = row.reportLink 
                    ? `<a href="${row.reportLink}" target="_blank" onclick="event.stopPropagation();" class="inline-flex items-center gap-1 px-2 py-1 rounded-md bg-cyan-500/20 text-cyan-300 hover:bg-cyan-500/40 border border-cyan-500/30 text-[11px] font-semibold"><i class="fa-solid fa-file-pdf"></i> View PDF</a>`
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
            // Center map on site
            if (mapInstance && site.lat && site.lng) {
                mapInstance.setView([site.lat, site.lng], 13);
            }

            // Populate Selected Site Report Viewer Card
            const content = document.getElementById('report-card-content');
            const action = document.getElementById('report-card-action');

            content.innerHTML = `
                <h4 class="font-bold text-cyan-300 text-sm mb-1">${site.estate}</h4>
                <p class="text-slate-300"><b>District:</b> ${site.district} | <b>Region:</b> ${site.region}</p>
                <p class="text-slate-300"><b>Division:</b> ${site.division}</p>
                <p class="text-slate-300"><b>Planned Capacity:</b> <span class="text-emerald-400 font-bold">${site.units} Units</span></p>
                <p class="text-slate-300"><b>NBRI 1st Report:</b> ${site.reportIssued}</p>
            `;

            if (site.reportLink) {
                action.innerHTML = `
                    <a href="${site.reportLink}" target="_blank" class="w-full py-2.5 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white rounded-xl text-xs font-bold flex items-center justify-center gap-2 shadow-lg shadow-cyan-500/20 transition">
                        <i class="fa-solid fa-file-pdf"></i> Open Official NBRI Report PDF
                    </a>
                `;
            } else {
                action.innerHTML = `
                    <button disabled class="w-full py-2.5 bg-slate-800 text-slate-500 rounded-xl text-xs font-semibold flex items-center justify-center gap-2 cursor-not-allowed border border-slate-700/50">
                        <i class="fa-solid fa-circle-exclamation"></i> No Link Attached to Sheet
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
            chatBox.innerHTML += `<div class="flex justify-end mb-2"><div class="bg-purple-600/40 p-2 rounded-xl text-white">${msg}</div></div>`;
            input.value = '';

            setTimeout(() => {
                chatBox.innerHTML += `<div class="flex gap-2 mb-2"><div class="bg-slate-900 p-2 rounded-xl text-slate-200">Showing stats for current filters: <strong>${filteredData.length} sites</strong> active. Click any row in the table to view its PDF report directly!</div></div>`;
                chatBox.scrollTop = chatBox.scrollHeight;
            }, 300);
        }
    </script>
</body>
</html>
"""

# Replace LOGO_URL inside html template
html_dashboard = html_template.replace("{{LOGO_URL}}", LOGO_URL)

# 4. Render HTML inside Streamlit
components.html(html_dashboard, height=1300, scrolling=True)
