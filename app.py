import streamlit as st
import streamlit.components.v1 as components

# 1. Page Configuration
LOGO_URL = "https://96legendssquare.com/wp-content/uploads/2025/08/National-Building-Research-Organization-NBRO.webp"

st.set_page_config(
    page_title="NBRI - IHP Progress Dashboard",
    page_icon=LOGO_URL,
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Remove default Streamlit padding & header
st.markdown("""
    <style>
        .block-container {
            padding-top: 0rem !important;
            padding-bottom: 0rem !important;
            padding-left: 0rem !important;
            padding-right: 0rem !important;
            max-width: 100% !important;
        }
        header[data-testid="stHeader"] { display: none !important; }
        footer { display: none !important; }
    </style>
""", unsafe_allow_html=True)

# 3. HTML, CSS, Leaflet JS Dashboard Template
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NBRI - IHP 4700 Resettlement Dashboard</title>
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
    <!-- PapaParse for Google Sheets CSV handling -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/PapaParse/5.4.1/papaparse.min.js"></script>

    <script>
        tailwind.config = {
            theme: {
                extend: {
                    fontFamily: { sans: ['Plus Jakarta Sans', 'sans-serif'] },
                    colors: {
                        darkBg: '#060913',
                        cardBg: 'rgba(15, 22, 41, 0.85)',
                        accentCyan: '#06b6d4',
                        accentBlue: '#3b82f6',
                        accentPurple: '#a855f7',
                        accentGreen: '#10b981',
                    }
                }
            }
        }
    </script>

    <style>
        body {
            font-family: 'Plus Jakarta Sans', sans-serif;
            background: radial-gradient(circle at 50% 0%, #0c142d 0%, #060913 80%);
            background-attachment: fixed;
            color: #e2e8f0;
            margin: 0;
            padding: 0;
        }

        .glass-panel {
            background: rgba(15, 23, 42, 0.85);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
        }

        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: rgba(15, 23, 42, 0.6); }
        ::-webkit-scrollbar-thumb { background: rgba(100, 116, 139, 0.5); border-radius: 4px; }

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
            background: #060913 !important;
            font-family: 'Plus Jakarta Sans', sans-serif !important;
        }
        .leaflet-popup-content-wrapper, .leaflet-tooltip {
            background: rgba(10, 16, 32, 0.95) !important;
            color: #f8fafc !important;
            border: 1px solid rgba(56, 189, 248, 0.4);
            border-radius: 12px !important;
            backdrop-filter: blur(12px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.6) !important;
        }
        .leaflet-popup-tip { background: rgba(10, 16, 32, 0.95) !important; }
    </style>
</head>
<body class="min-h-screen pb-10">

    <!-- TOP HEADER -->
    <header class="sticky top-0 z-50 glass-panel border-b border-slate-800/80 px-6 py-3 mb-6">
        <div class="max-w-[1700px] mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
            
            <div class="flex items-center gap-3.5">
                <div class="w-11 h-11 rounded-xl bg-slate-900 border border-slate-700 p-1 flex items-center justify-center shadow-lg overflow-hidden">
                    <img src="{{LOGO_URL}}" alt="NBRO Logo" class="w-full h-full object-contain">
                </div>
                <div>
                    <div class="flex items-center gap-2">
                        <h1 class="text-lg font-bold tracking-tight text-white">NBRI - IHP 4700 Resettlement Dashboard</h1>
                        <span class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                            <span class="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span> Live Data
                        </span>
                    </div>
                    <p class="text-xs text-slate-400">Resettlement Site Monitoring & Technical Report Tracking System</p>
                </div>
            </div>

            <!-- FILTERS -->
            <div class="flex flex-wrap items-center gap-3 w-full md:w-auto">
                <div class="relative flex-1 md:flex-initial">
                    <select id="filter-region" class="w-full bg-slate-900/90 text-xs text-slate-200 pl-3 pr-8 py-2 rounded-xl border border-slate-700 focus:border-cyan-500 outline-none cursor-pointer">
                        <option value="ALL">All Regions</option>
                    </select>
                </div>

                <div class="relative flex-1 md:flex-initial">
                    <select id="filter-district" class="w-full bg-slate-900/90 text-xs text-slate-200 pl-3 pr-8 py-2 rounded-xl border border-slate-700 focus:border-cyan-500 outline-none cursor-pointer">
                        <option value="ALL">All Districts</option>
                    </select>
                </div>

                <div class="relative flex-1 md:flex-initial">
                    <input type="text" id="search-input" placeholder="Search site or division..." class="w-full bg-slate-900/90 text-xs text-slate-200 pl-3 pr-4 py-2 rounded-xl border border-slate-700 focus:border-cyan-500 outline-none placeholder-slate-500">
                </div>

                <button onclick="fetchCSVData()" class="px-3.5 py-2 bg-cyan-600/30 hover:bg-cyan-600/50 text-cyan-200 border border-cyan-500/40 rounded-xl text-xs font-medium transition flex items-center gap-2">
                    <i id="sync-icon" class="fa-solid fa-arrows-rotate"></i> Sync Data
                </button>
            </div>

        </div>
    </header>

    <!-- MAIN CONTAINER -->
    <main class="max-w-[1700px] mx-auto px-4 sm:px-6">

        <!-- KPI SUMMARY CARDS -->
        <section class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <div class="glass-panel p-4 rounded-2xl border-l-4 border-l-cyan-500">
                <span class="text-xs font-medium text-slate-400 uppercase tracking-wider">Total Resettlement Sites</span>
                <h2 id="kpi-total-sites" class="text-2xl font-extrabold text-white mt-1">--</h2>
                <p class="text-[11px] text-cyan-400 mt-1"><i class="fa-solid fa-location-dot mr-1"></i> Monitored Estates</p>
            </div>

            <div class="glass-panel p-4 rounded-2xl border-l-4 border-l-blue-500">
                <span class="text-xs font-medium text-slate-400 uppercase tracking-wider">Total Planned Housing Units</span>
                <h2 id="kpi-total-units" class="text-2xl font-extrabold text-white mt-1">--</h2>
                <p class="text-[11px] text-blue-400 mt-1"><i class="fa-solid fa-house-chimney mr-1"></i> Resettlement Capacity</p>
            </div>

            <div class="glass-panel p-4 rounded-2xl border-l-4 border-l-purple-500">
                <span class="text-xs font-medium text-slate-400 uppercase tracking-wider">NBRI 1st Report Issued</span>
                <div class="flex items-baseline gap-2 mt-1">
                    <h2 id="kpi-report-issued" class="text-2xl font-extrabold text-white">--</h2>
                    <span id="kpi-report-pct" class="text-xs text-purple-400 font-semibold">--%</span>
                </div>
                <div class="w-full bg-slate-800 h-1.5 rounded-full mt-2 overflow-hidden">
                    <div id="kpi-report-bar" class="bg-purple-500 h-full w-0 transition-all duration-500"></div>
                </div>
            </div>

            <div class="glass-panel p-4 rounded-2xl border-l-4 border-l-emerald-500">
                <span class="text-xs font-medium text-slate-400 uppercase tracking-wider">BOD Completed</span>
                <div class="flex items-baseline gap-2 mt-1">
                    <h2 id="kpi-bod-completed" class="text-2xl font-extrabold text-white">--</h2>
                    <span id="kpi-bod-pct" class="text-xs text-emerald-400 font-semibold">--%</span>
                </div>
                <p class="text-[11px] text-emerald-400 mt-1"><i class="fa-solid fa-circle-check mr-1"></i> Clearance Done</p>
            </div>
        </section>

        <!-- MAIN DASHBOARD CONTENT -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
            
            <!-- LEFT 8 COLUMNS: MAP & BAR CHART -->
            <div class="lg:col-span-8 flex flex-col gap-6">
                
                <!-- GIS MAP WITH ESRI DEEP BLUE BASEMAP -->
                <div class="glass-panel rounded-2xl p-4 relative">
                    <div class="flex items-center justify-between mb-3">
                        <div class="flex items-center gap-2">
                            <span class="w-2.5 h-2.5 rounded-full bg-cyan-400 animate-pulse"></span>
                            <h3 class="text-sm font-bold text-white">GIS Map - Site Location & District Highlights</h3>
                        </div>
                        <span class="text-[11px] text-slate-400">
                            <i class="fa-solid fa-hand-pointer text-cyan-400 mr-1"></i> Hover on markers for 5 Key Details
                        </span>
                    </div>
                    <div class="w-full h-[420px] rounded-xl overflow-hidden relative border border-slate-800" id="map-container">
                        <div id="map" class="w-full h-full z-10"></div>
                    </div>
                </div>

                <!-- BAR CHART -->
                <div class="glass-panel rounded-2xl p-4">
                    <h3 class="text-sm font-bold text-white mb-3 flex items-center gap-2">
                        <i class="fa-solid fa-chart-column text-cyan-400"></i> Region-wise Housing Unit Distribution
                    </h3>
                    <div class="h-[250px] w-full">
                        <canvas id="barChart"></canvas>
                    </div>
                </div>

                <!-- TABLE SECTION WITH FIXED VIEW PDF DIRECT LINK -->
                <div class="glass-panel rounded-2xl p-4 overflow-hidden">
                    <div class="flex items-center justify-between mb-3">
                        <h3 class="text-sm font-bold text-white flex items-center gap-2">
                            <i class="fa-solid fa-table text-purple-400"></i> Resettlement Site Details
                        </h3>
                        <span class="text-xs text-slate-400" id="table-count">Showing 0 sites</span>
                    </div>
                    
                    <div class="max-h-[380px] overflow-y-auto border border-slate-800 rounded-xl">
                        <table class="w-full text-left text-xs text-slate-300">
                            <thead class="bg-slate-900 sticky top-0 z-20 text-slate-400 font-semibold uppercase border-b border-slate-800">
                                <tr>
                                    <th class="py-2.5 px-3">S.NO</th>
                                    <th class="py-2.5 px-3">REGION</th>
                                    <th class="py-2.5 px-3">DISTRICT</th>
                                    <th class="py-2.5 px-3">ESTATE / SITE</th>
                                    <th class="py-2.5 px-3">DIVISION</th>
                                    <th class="py-2.5 px-3 text-right">UNITS</th>
                                    <th class="py-2.5 px-3 text-center">NBRI REPORT</th>
                                    <th class="py-2.5 px-3 text-center">BOD</th>
                                    <th class="py-2.5 px-3 text-center">REPORT LINK</th>
                                </tr>
                            </thead>
                            <tbody id="table-body" class="divide-y divide-slate-800/60 font-medium"></tbody>
                        </table>
                    </div>
                </div>

            </div>

            <!-- RIGHT 4 COLUMNS: DOUGHNUT CHART & SITE VIEWER -->
            <div class="lg:col-span-4 flex flex-col gap-6">
                
                <!-- DOUGHNUT CHART (வட்டவரைபடம்) -->
                <div class="glass-panel rounded-2xl p-4">
                    <h3 class="text-sm font-bold text-white mb-1 flex items-center gap-2">
                        <i class="fa-solid fa-chart-pie text-purple-400"></i> NBRI Report Status
                    </h3>
                    <p class="text-xs text-slate-400 mb-3">1st Clearance Report Issued vs Pending</p>
                    <div class="relative h-[220px] flex items-center justify-center">
                        <canvas id="doughnutChart"></canvas>
                    </div>
                </div>

                <!-- SELECTED SITE REPORT CARD -->
                <div class="glass-panel rounded-2xl p-5 border border-cyan-500/30 flex flex-col justify-between">
                    <div>
                        <div class="flex items-center justify-between mb-3">
                            <h3 class="text-sm font-bold text-white flex items-center gap-2">
                                <i class="fa-solid fa-file-pdf text-cyan-400"></i> Selected Site Info
                            </h3>
                            <span class="text-[10px] text-cyan-300 bg-cyan-500/20 px-2 py-0.5 rounded border border-cyan-500/30">Quick Access</span>
                        </div>
                        <div id="report-card-content" class="bg-slate-900/90 p-4 rounded-xl border border-slate-800 text-xs space-y-2">
                            <p class="text-slate-400 italic">Click any site row in the table or point on the map to load its report PDF link here.</p>
                        </div>
                    </div>
                    <div id="report-card-action" class="mt-4">
                        <button disabled class="w-full py-2.5 bg-slate-800 text-slate-500 rounded-xl text-xs font-semibold flex items-center justify-center gap-2 cursor-not-allowed">
                            Select a Site to Open Report
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
        let geoJsonLayer = null;
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
            loadDistrictGeoJSON();
        });

        function initMap() {
            mapInstance = L.map('map', { zoomControl: true, attributionControl: false }).setView([6.9, 80.6], 8);
            
            // ESRI Deep Blue / World Dark Gray Canvas Tile Layer
            L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}', {
                maxZoom: 16,
                subdomains: 'abcd'
            }).addTo(mapInstance);

            markersGroup = L.layerGroup().addTo(mapInstance);
        }

        // Fetch Sri Lanka District GeoJSON (COD AB LKA)
        function loadDistrictGeoJSON() {
            fetch('https://raw.githubusercontent.com/ahmdrefai/sri-lanka-geojson/master/districts.json')
                .then(res => res.json())
                .then(data => {
                    geoJsonLayer = L.geoJSON(data, {
                        style: {
                            color: '#06b6d4',
                            weight: 1,
                            opacity: 0.3,
                            fillColor: '#0284c7',
                            fillOpacity: 0.05
                        }
                    }).addTo(mapInstance);
                }).catch(err => console.log('GeoJSON optional layer error:', err));
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
                // Find keys dynamically
                const getVal = (keys) => {
                    for (let k of keys) {
                        const found = Object.keys(r).find(key => key.trim().toLowerCase() === k.toLowerCase());
                        if (found && r[found]) return r[found].trim();
                    }
                    return '';
                };

                const region = getVal(['Region', 'region']) || 'Rathnapura';
                const district = getVal(['District', 'district']) || region;
                const estate = getVal(['Estate', 'Estate / Site', 'estate', 'site']) || `Site ${idx+1}`;
                const division = getVal(['Division', 'division']) || '-';
                
                // Units Parsing
                let rawUnits = getVal(['Units (2020 List)', 'Units', 'units', 'No. of Units']) || '0';
                rawUnits = rawUnits.replace(/[^0-9]/g, '');
                const units = parseInt(rawUnits) || 0;

                const reportIssued = getVal(['NBRI 1st Report Issued', '1st Report Issued', 'NBRI Report']) || 'Yes';
                const bodCompleted = getVal(['BOD Completed', 'BOD']) || 'None';
                
                // NBRI 1st Report - Link column exact extraction
                const reportLink = getVal(['NBRI 1st Report - Link', 'Report Link', 'NBRI Report Link', 'Link']) || '';

                let baseCoords = districtCoordinates[district] || { lat: 6.68, lng: 80.39 };
                let lat = parseFloat(getVal(['Latitude', 'lat'])) || (baseCoords.lat + (Math.random() - 0.5) * 0.12);
                let lng = parseFloat(getVal(['Longitude', 'lng', 'long'])) || (baseCoords.lng + (Math.random() - 0.5) * 0.12);

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

            // Highlight District GeoJSON if selected
            if (geoJsonLayer) {
                geoJsonLayer.eachLayer(layer => {
                    const dName = layer.feature?.properties?.district || layer.feature?.properties?.NAME_1 || '';
                    if (selectedDistrict !== 'ALL' && dName.toLowerCase().includes(selectedDistrict.toLowerCase())) {
                        layer.setStyle({ color: '#38bdf8', weight: 3, opacity: 0.9, fillColor: '#0284c7', fillOpacity: 0.25 });
                    } else {
                        layer.setStyle({ color: '#06b6d4', weight: 1, opacity: 0.3, fillColor: '#0284c7', fillOpacity: 0.05 });
                    }
                });
            }

            if (filteredData.length === 0) return;
            const bounds = [];

            filteredData.forEach(site => {
                const isBod = site.bodCompleted.toLowerCase() === 'yes';
                let pinClass = isBod ? 'completed' : '';

                const customIcon = L.divIcon({
                    className: 'custom-pin-wrapper',
                    html: `<span class="glowing-pin ${pinClass}"></span>`,
                    iconSize: [14, 14],
                    iconAnchor: [7, 7]
                });

                const marker = L.marker([site.lat, site.lng], { icon: customIcon });

                // 5 Key items in hover tooltip / popup
                const tooltipHTML = `
                    <div style="font-family:'Plus Jakarta Sans', sans-serif; padding:2px;">
                        <div style="font-weight:700; color:#38bdf8; font-size:13px; margin-bottom:4px;"><i class="fa-solid fa-location-dot"></i> ${site.estate}</div>
                        <div style="font-size:11px; color:#cbd5e1; margin:2px 0;"><b>1. District & Region:</b> ${site.district} (${site.region})</div>
                        <div style="font-size:11px; color:#cbd5e1; margin:2px 0;"><b>2. Division:</b> ${site.division}</div>
                        <div style="font-size:11px; color:#cbd5e1; margin:2px 0;"><b>3. Units Planned:</b> <span style="color:#34d399; font-weight:700;">${site.units} Units</span></div>
                        <div style="font-size:11px; color:#cbd5e1; margin:2px 0;"><b>4. NBRI 1st Report:</b> ${site.reportIssued}</div>
                        <div style="font-size:11px; color:#cbd5e1; margin:2px 0;"><b>5. BOD Status:</b> ${site.bodCompleted}</div>
                    </div>
                `;

                marker.bindTooltip(tooltipHTML, { sticky: true, direction: 'top' });
                marker.on('click', () => selectSiteRow(site));
                
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
                        backgroundColor: 'rgba(6, 182, 212, 0.85)',
                        borderColor: '#06b6d4',
                        borderWidth: 1,
                        borderRadius: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        x: { ticks: { color: '#94a3b8', font: { size: 10 } }, grid: { display: false } },
                        y: { ticks: { color: '#94a3b8', font: { size: 10 } }, grid: { color: 'rgba(255, 255, 255, 0.05)' } }
                    }
                }
            });

            // DOUGHNUT CHART (வட்டவரைபடம்)
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
                    cutout: '70%',
                    plugins: {
                        legend: { position: 'bottom', labels: { color: '#cbd5e1', font: { size: 11 } } }
                    }
                }
            });
        }

        function updateCharts() {
            // Group data by REGION for the bar chart
            const regionMap = {};
            filteredData.forEach(item => {
                const key = item.region || 'Other';
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
                tr.className = 'hover:bg-slate-800/80 border-b border-slate-800/40 cursor-pointer transition';
                tr.onclick = () => selectSiteRow(row);

                // FIXED DIRECT PDF LINK logic
                let reportLinkHTML = (row.reportLink && row.reportLink.startsWith('http'))
                    ? `<a href="${row.reportLink}" target="_blank" rel="noopener noreferrer" onclick="event.stopPropagation();" class="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg bg-cyan-500/20 text-cyan-300 hover:bg-cyan-500/40 border border-cyan-500/40 text-[11px] font-semibold transition-all shadow-sm"><i class="fa-solid fa-file-pdf text-red-400"></i> View PDF</a>`
                    : `<span class="text-slate-500 text-[10px]">N/A</span>`;

                tr.innerHTML = `
                    <td class="py-2.5 px-3 font-mono text-slate-400">${row.sno}</td>
                    <td class="py-2.5 px-3 font-semibold text-slate-200">${row.region}</td>
                    <td class="py-2.5 px-3 text-slate-300">${row.district}</td>
                    <td class="py-2.5 px-3 font-bold text-cyan-300">${row.estate}</td>
                    <td class="py-2.5 px-3 text-slate-400">${row.division}</td>
                    <td class="py-2.5 px-3 text-right font-bold text-emerald-400">${row.units}</td>
                    <td class="py-2.5 px-3 text-center">${row.reportIssued}</td>
                    <td class="py-2.5 px-3 text-center">${row.bodCompleted}</td>
                    <td class="py-2.5 px-3 text-center">${reportLinkHTML}</td>
                `;
                tbody.appendChild(tr);
            });
        }

        function selectSiteRow(site) {
            if (mapInstance && site.lat && site.lng) {
                mapInstance.setView([site.lat, site.lng], 12);
            }

            const content = document.getElementById('report-card-content');
            const action = document.getElementById('report-card-action');

            content.innerHTML = `
                <h4 class="font-bold text-cyan-300 text-sm mb-1">${site.estate}</h4>
                <p class="text-slate-300"><b>District:</b> ${site.district} | <b>Region:</b> ${site.region}</p>
                <p class="text-slate-300"><b>Division:</b> ${site.division}</p>
                <p class="text-slate-300"><b>Housing Capacity:</b> <span class="text-emerald-400 font-bold">${site.units} Units</span></p>
                <p class="text-slate-300"><b>NBRI 1st Report Issued:</b> ${site.reportIssued}</p>
            `;

            if (site.reportLink && site.reportLink.startsWith('http')) {
                action.innerHTML = `
                    <a href="${site.reportLink}" target="_blank" rel="noopener noreferrer" class="w-full py-2.5 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white rounded-xl text-xs font-bold flex items-center justify-center gap-2 shadow-lg transition">
                        <i class="fa-solid fa-file-pdf"></i> Open Official NBRI PDF Report
                    </a>
                `;
            } else {
                action.innerHTML = `
                    <button disabled class="w-full py-2.5 bg-slate-800 text-slate-500 rounded-xl text-xs font-semibold flex items-center justify-center gap-2 cursor-not-allowed">
                        No Report Link in Sheet
                    </button>
                `;
            }
        }

        function setupEventListeners() {
            document.getElementById('filter-region').addEventListener('change', applyFilters);
            document.getElementById('filter-district').addEventListener('change', applyFilters);
            document.getElementById('search-input').addEventListener('input', applyFilters);
        }
    </script>
</body>
</html>
"""

# Replace LOGO_URL inside html template
html_dashboard = html_template.replace("{{LOGO_URL}}", LOGO_URL)

# 4. Render HTML inside Streamlit
components.html(html_dashboard, height=1350, scrolling=True)
