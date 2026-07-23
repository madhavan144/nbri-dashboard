import streamlit as st # type: ignore[import-not-found]
import streamlit.components.v1 as components # type: ignore[import-not-found]

# 1. Page Configuration
LOGO_URL = "https://96legendssquare.com/wp-content/uploads/2025/08/National-Building-Research-Organization-NBRO.webp"

st.set_page_config(
    page_title="NBRI - Cyber HUD Resettlement Dashboard",
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

# 3. Sci-Fi Cyber-Blue Integrated Dashboard Template
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NBRI - Cyber Resettlement Progress Dashboard</title>
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- FontAwesome Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;800;900&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <!-- Leaflet CSS & JS -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <!-- PapaParse -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/PapaParse/5.4.1/papaparse.min.js"></script>

    <script>
        tailwind.config = {
            theme: {
                extend: {
                    fontFamily: {
                        sans: ['Plus Jakarta Sans', 'sans-serif'],
                        orbitron: ['Orbitron', 'sans-serif'],
                    },
                    colors: {
                        cyberDark: '#030712',
                        cyberBlue: '#0284c7',
                        neonCyan: '#06b6d4',
                        neonGlow: '#38bdf8',
                        cardBg: 'rgba(6, 15, 30, 0.85)',
                        borderGlow: 'rgba(6, 182, 212, 0.3)'
                    }
                }
            }
        }
    </script>

    <style>
        body {
            font-family: 'Plus Jakarta Sans', sans-serif;
            background: #02040a;
            background-image: 
                radial-gradient(circle at 50% 50%, rgba(6, 182, 212, 0.08) 0%, transparent 60%),
                linear-gradient(rgba(2, 6, 23, 0.94), rgba(2, 6, 23, 0.98)),
                repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(6, 182, 212, 0.03) 2px, rgba(6, 182, 212, 0.03) 4px);
            background-attachment: fixed;
            color: #e2e8f0;
            margin: 0;
            padding: 0;
        }

        .hud-border {
            background: rgba(8, 20, 42, 0.85);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(6, 182, 212, 0.25);
            box-shadow: inset 0 0 15px rgba(6, 182, 212, 0.05), 0 8px 32px 0 rgba(0, 0, 0, 0.8);
            position: relative;
        }

        .hud-border::before {
            content: '';
            position: absolute;
            top: -1px; left: -1px; width: 10px; height: 10px;
            border-top: 2px solid #06b6d4;
            border-left: 2px solid #06b6d4;
        }
        .hud-border::after {
            content: '';
            position: absolute;
            bottom: -1px; right: -1px; width: 10px; height: 10px;
            border-bottom: 2px solid #06b6d4;
            border-right: 2px solid #06b6d4;
        }

        ::-webkit-scrollbar { width: 4px; height: 4px; }
        ::-webkit-scrollbar-track { background: rgba(2, 6, 23, 0.8); }
        ::-webkit-scrollbar-thumb { background: #0284c7; border-radius: 2px; }
        ::-webkit-scrollbar-thumb:hover { background: #06b6d4; }

        .glowing-pin {
            display: block; width: 12px; height: 12px;
            border-radius: 50%; background: #06b6d4;
            box-shadow: 0 0 10px #06b6d4, 0 0 20px #06b6d4;
            animation: pulse-cyan 2s infinite;
        }
        @keyframes pulse-cyan {
            0% { transform: scale(0.9); box-shadow: 0 0 0 0 rgba(6, 182, 212, 0.8); }
            70% { transform: scale(1.2); box-shadow: 0 0 0 10px rgba(6, 182, 212, 0); }
            100% { transform: scale(0.9); box-shadow: 0 0 0 0 rgba(6, 182, 212, 0); }
        }

        .leaflet-container { background: #02040a !important; }
        .leaflet-popup-content-wrapper {
            background: rgba(6, 15, 30, 0.95) !important;
            color: #f8fafc !important;
            border: 1px solid #06b6d4;
            border-radius: 8px !important;
            box-shadow: 0 0 15px rgba(6, 182, 212, 0.3);
        }
        .leaflet-popup-tip { background: rgba(6, 15, 30, 0.95) !important; }
    </style>
</head>
<body class="min-h-screen pb-10">

    <!-- HEADER NAVIGATION -->
    <header class="sticky top-0 z-50 hud-border border-b border-cyan-500/30 px-6 py-3 mb-6 bg-slate-950/90">
        <div class="max-w-[1750px] mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
            
            <div class="flex items-center gap-3.5">
                <div class="w-10 h-10 rounded bg-cyan-950/50 border border-cyan-500/50 p-1 flex items-center justify-center shadow-lg shadow-cyan-500/20">
                    <img src="{{LOGO_URL}}" alt="NBRO" class="w-full h-full object-contain">
                </div>
                <div>
                    <h1 class="text-lg font-extrabold tracking-wider text-cyan-400 font-orbitron flex items-center gap-2">
                        <i class="fa-solid fa-microchip text-xs animate-pulse"></i> NBRI RESETTLEMENT COMMAND CENTER
                    </h1>
                    <p class="text-[11px] text-slate-400 tracking-wide">Spatial Monitoring & Progress Analytics HUD</p>
                </div>
            </div>

            <!-- FILTERS -->
            <div class="flex flex-wrap items-center gap-3 w-full md:w-auto">
                <select id="filter-region" class="bg-slate-900 text-xs text-cyan-300 px-3 py-2 rounded border border-cyan-500/40 focus:outline-none font-mono">
                    <option value="ALL">ALL REGIONS</option>
                </select>

                <select id="filter-district" class="bg-slate-900 text-xs text-cyan-300 px-3 py-2 rounded border border-cyan-500/40 focus:outline-none font-mono">
                    <option value="ALL">ALL DISTRICTS</option>
                </select>

                <input type="text" id="search-input" placeholder="SEARCH ESTATE..." class="bg-slate-900 text-xs text-cyan-200 px-3 py-2 rounded border border-cyan-500/40 focus:outline-none placeholder-slate-600 font-mono">

                <button onclick="fetchCSVData()" class="px-3 py-2 bg-cyan-600/30 hover:bg-cyan-500/40 text-cyan-300 border border-cyan-400/50 rounded text-xs font-mono transition flex items-center gap-2">
                    <i id="sync-icon" class="fa-solid fa-arrows-rotate"></i> SYNC
                </button>
            </div>
        </div>
    </header>

    <!-- MAIN DASHBOARD CONTENT -->
    <main class="max-w-[1750px] mx-auto px-4 sm:px-6">

        <!-- KPI STATS PANEL -->
        <section class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <div class="hud-border p-4 rounded bg-slate-950/60">
                <span class="text-[10px] font-orbitron tracking-widest text-slate-400 uppercase">TOTAL SITES</span>
                <h2 id="kpi-total-sites" class="text-3xl font-extrabold text-cyan-400 font-orbitron mt-1">--</h2>
            </div>
            <div class="hud-border p-4 rounded bg-slate-950/60">
                <span class="text-[10px] font-orbitron tracking-widest text-slate-400 uppercase">TOTAL UNITS</span>
                <h2 id="kpi-total-units" class="text-3xl font-extrabold text-cyan-400 font-orbitron mt-1">--</h2>
            </div>
            <div class="hud-border p-4 rounded bg-slate-950/60">
                <span class="text-[10px] font-orbitron tracking-widest text-slate-400 uppercase">1ST REPORT ISSUED</span>
                <h2 id="kpi-report-issued" class="text-3xl font-extrabold text-emerald-400 font-orbitron mt-1">--</h2>
            </div>
            <div class="hud-border p-4 rounded bg-slate-950/60">
                <span class="text-[10px] font-orbitron tracking-widest text-slate-400 uppercase">BOD COMPLETED</span>
                <h2 id="kpi-bod-completed" class="text-3xl font-extrabold text-blue-400 font-orbitron mt-1">--</h2>
            </div>
        </section>

        <!-- DASHBOARD GRID -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
            
            <!-- LEFT AREA: GIS MAP & TABLES -->
            <div class="lg:col-span-8 flex flex-col gap-6">
                
                <!-- SCI-FI GIS MAP -->
                <div class="hud-border rounded p-4 relative">
                    <div class="flex items-center justify-between mb-3">
                        <h3 class="text-xs font-orbitron tracking-wider text-cyan-400 flex items-center gap-2">
                            <i class="fa-solid fa-crosshairs text-cyan-500"></i> GIS SPATIAL VISUALIZER
                        </h3>
                    </div>
                    <div class="w-full h-[400px] rounded overflow-hidden relative border border-cyan-500/30" id="map"></div>
                </div>

                <!-- MAIN REGISTRY TABLE WITH WORKING LINK -->
                <div class="hud-border rounded p-4">
                    <div class="flex items-center justify-between mb-3">
                        <h3 class="text-xs font-orbitron tracking-wider text-cyan-400 flex items-center gap-2">
                            <i class="fa-solid fa-table-list"></i> SITE REGISTRY & REPORT DOCUMENTS
                        </h3>
                    </div>
                    
                    <div class="max-h-[350px] overflow-y-auto border border-cyan-500/20 rounded">
                        <table class="w-full text-left text-xs font-mono">
                            <thead class="bg-slate-950 text-cyan-400 sticky top-0 z-20 border-b border-cyan-500/30">
                                <tr>
                                    <th class="py-2.5 px-3">NO</th>
                                    <th class="py-2.5 px-3">REGION</th>
                                    <th class="py-2.5 px-3">DISTRICT</th>
                                    <th class="py-2.5 px-3">ESTATE SITE</th>
                                    <th class="py-2.5 px-3 text-right">UNITS</th>
                                    <th class="py-2.5 px-3 text-center">REPORT LINK</th>
                                </tr>
                            </thead>
                            <tbody id="table-body" class="divide-y divide-slate-800 text-slate-300"></tbody>
                        </table>
                    </div>
                </div>

            </div>

            <!-- RIGHT AREA: SUMMARY & DIRECT PDF VIEWER -->
            <div class="lg:col-span-4 flex flex-col gap-6">
                
                <!-- SELECTED SITE REPORT LINK VIEWER CARD -->
                <div class="hud-border rounded p-5 bg-slate-950/80 border-cyan-400/50">
                    <h3 class="text-xs font-orbitron text-cyan-300 mb-3 flex items-center gap-2">
                        <i class="fa-solid fa-file-pdf"></i> ACTIVE REPORT INSPECTOR
                    </h3>
                    
                    <div id="report-card-content" class="bg-slate-900/90 p-4 rounded border border-cyan-500/30 text-xs space-y-2 font-mono">
                        <p class="text-slate-400 italic">Select any site row or marker to inspect the direct report link.</p>
                    </div>

                    <div id="report-card-action" class="mt-4">
                        <button disabled class="w-full py-2.5 bg-slate-800 text-slate-500 rounded text-xs font-mono border border-slate-700 cursor-not-allowed">
                            SELECT A SITE TO OPEN REPORT PDF
                        </button>
                    </div>
                </div>

                <!-- DISTRICT SUMMARY TABLE -->
                <div class="hud-border rounded p-4">
                    <h3 class="text-xs font-orbitron tracking-wider text-cyan-400 mb-3">
                        DISTRICT HOUSING SUMMARY
                    </h3>
                    <div class="max-h-[250px] overflow-y-auto">
                        <table class="w-full text-left text-xs font-mono">
                            <thead class="text-slate-400 border-b border-slate-800">
                                <tr>
                                    <th class="pb-2">DISTRICT</th>
                                    <th class="pb-2 text-right">UNITS</th>
                                </tr>
                            </thead>
                            <tbody id="district-summary-body" class="divide-y divide-slate-800 text-slate-300"></tbody>
                        </table>
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

        const districtCoordinates = {
            "Rathnapura": { lat: 6.6828, lng: 80.3992 },
            "Badulla": { lat: 6.9934, lng: 81.0550 },
            "Kalutara": { lat: 6.5854, lng: 79.9607 },
            "Kegalle": { lat: 7.2513, lng: 80.3464 },
            "Kandy": { lat: 7.2906, lng: 80.6337 },
            "Nuwara Eliya": { lat: 6.9497, lng: 80.7891 }
        };

        document.addEventListener('DOMContentLoaded', () => {
            initMap();
            fetchCSVData();
            document.getElementById('filter-region').addEventListener('change', applyFilters);
            document.getElementById('filter-district').addEventListener('change', applyFilters);
            document.getElementById('search-input').addEventListener('input', applyFilters);
        });

        function initMap() {
            mapInstance = L.map('map', { zoomControl: true }).setView([6.9, 80.6], 8);
            L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', { maxZoom: 18 }).addTo(mapInstance);
            markersGroup = L.layerGroup().addTo(mapInstance);
        }

        function fetchCSVData() {
            Papa.parse(DEFAULT_CSV_URL, {
                download: true,
                header: true,
                skipEmptyLines: true,
                complete: function(results) {
                    if (results.data && results.data.length > 0) processCSVRows(results.data);
                }
            });
        }

        function processCSVRows(rows) {
            rawData = rows.map((r, idx) => {
                const region = r['Region'] || r['region'] || 'Rathnapura';
                const district = r['District'] || r['district'] || region;
                const estate = r['Estate'] || r['estate'] || `Site ${idx+1}`;
                const division = r['Division'] || r['division'] || '-';
                
                let rawUnits = r['Units (2529 List)'] || r['Units (2020 List)'] || r['Units'] || '0';
                const units = parseInt(rawUnits.toString().replace(/[^0-9]/g, '')) || 0;

                const reportIssued = (r['NBRI 1st Report - Issued'] || 'Yes').trim();
                const bodCompleted = (r['BOD Completed'] || 'No').trim();
                
                // Extraction of Report Direct Link
                const reportLinkRaw = r['NBRI 1st Report - Link'] || r['Report Link'] || '';
                const reportLink = formatReportURL(reportLinkRaw, estate);

                let baseCoords = districtCoordinates[district] || { lat: 6.68, lng: 80.39 };
                let lat = parseFloat(r['Lat']) || (baseCoords.lat + (Math.random() - 0.5) * 0.1);
                let lng = parseFloat(r['Lon']) || (baseCoords.lng + (Math.random() - 0.5) * 0.1);

                return { sno: idx + 1, region, district, estate, division, units, reportIssued, bodCompleted, reportLink, lat, lng };
            });

            populateDropdowns();
            applyFilters();
        }

        function formatReportURL(rawLink, estateName) {
            if (!rawLink || rawLink.trim() === '' || rawLink.trim() === '-') return '';
            let cleaned = rawLink.trim();
            if (cleaned.startsWith('http://') || cleaned.startsWith('https://')) return cleaned;
            return `https://www.google.com/search?q=NBRI+Report+${encodeURIComponent(cleaned)}+${encodeURIComponent(estateName)}`;
        }

        function populateDropdowns() {
            const regionSelect = document.getElementById('filter-region');
            const districtSelect = document.getElementById('filter-district');

            const regions = [...new Set(rawData.map(d => d.region))].filter(Boolean);
            const districts = [...new Set(rawData.map(d => d.district))].filter(Boolean);

            regionSelect.innerHTML = '<option value="ALL">ALL REGIONS</option>' + regions.map(r => `<option value="${r}">${r}</option>`).join('');
            districtSelect.innerHTML = '<option value="ALL">ALL DISTRICTS</option>' + districts.map(d => `<option value="${d}">${d}</option>`).join('');
        }

        function applyFilters() {
            const regionVal = document.getElementById('filter-region').value;
            const districtVal = document.getElementById('filter-district').value;
            const searchVal = document.getElementById('search-input').value.toLowerCase().trim();

            filteredData = rawData.filter(item => {
                const matchRegion = (regionVal === 'ALL' || item.region === regionVal);
                const matchDistrict = (districtVal === 'ALL' || item.district === districtVal);
                const matchSearch = !searchVal || item.estate.toLowerCase().includes(searchVal);
                return matchRegion && matchDistrict && matchSearch;
            });

            updateKPIs();
            renderMainTable();
            updateMapMarkers();
            renderDistrictSummary();
        }

        function updateKPIs() {
            document.getElementById('kpi-total-sites').textContent = filteredData.length;
            document.getElementById('kpi-total-units').textContent = filteredData.reduce((a, c) => a + c.units, 0).toLocaleString();
            document.getElementById('kpi-report-issued').textContent = filteredData.filter(d => d.reportIssued.toLowerCase() === 'yes').length;
            document.getElementById('kpi-bod-completed').textContent = filteredData.filter(d => d.bodCompleted.toLowerCase() === 'yes').length;
        }

        function renderMainTable() {
            const tbody = document.getElementById('table-body');
            tbody.innerHTML = '';

            filteredData.forEach(row => {
                const tr = document.createElement('tr');
                tr.className = 'hover:bg-cyan-950/40 cursor-pointer transition';
                tr.onclick = () => selectSiteRow(row);

                // event.stopPropagation ensures direct PDF opening without Map Zoom override
                let reportButton = row.reportLink 
                    ? `<a href="${row.reportLink}" target="_blank" rel="noopener noreferrer" onclick="event.stopPropagation();" class="inline-block px-2 py-1 rounded bg-cyan-500/20 text-cyan-300 hover:bg-cyan-500/50 border border-cyan-400/40 text-[10px] font-bold">
                        <i class="fa-solid fa-file-pdf mr-1"></i> OPEN REPORT
                       </a>`
                    : `<span class="text-slate-600 text-[10px]">NO LINK</span>`;

                tr.innerHTML = `
                    <td class="py-2 px-3 text-slate-500">${row.sno}</td>
                    <td class="py-2 px-3">${row.region}</td>
                    <td class="py-2 px-3">${row.district}</td>
                    <td class="py-2 px-3 font-bold text-cyan-300">${row.estate}</td>
                    <td class="py-2 px-3 text-right text-emerald-400 font-bold">${row.units}</td>
                    <td class="py-2 px-3 text-center">${reportButton}</td>
                `;
                tbody.appendChild(tr);
            });
        }

        function updateMapMarkers() {
            markersGroup.clearLayers();
            filteredData.forEach(site => {
                const customIcon = L.divIcon({
                    className: 'custom-pin',
                    html: `<span class="glowing-pin"></span>`,
                    iconSize: [12, 12]
                });

                const marker = L.marker([site.lat, site.lng], { icon: customIcon });
                marker.bindPopup(`<b>${site.estate}</b><br>Units: ${site.units}`);
                marker.on('click', () => selectSiteRow(site));
                markersGroup.addLayer(marker);
            });
        }

        function selectSiteRow(site) {
            if (mapInstance && site.lat && site.lng) mapInstance.setView([site.lat, site.lng], 12);

            const content = document.getElementById('report-card-content');
            const action = document.getElementById('report-card-action');

            content.innerHTML = `
                <div class="border-b border-cyan-500/30 pb-2 mb-2">
                    <h4 class="font-bold text-cyan-300 text-sm">${site.estate}</h4>
                    <p class="text-[10px] text-slate-400">Division: ${site.division}</p>
                </div>
                <div><b>District:</b> ${site.district}</div>
                <div><b>Units:</b> <span class="text-emerald-400 font-bold">${site.units}</span></div>
                <div><b>1st Report:</b> ${site.reportIssued}</div>
            `;

            if (site.reportLink) {
                action.innerHTML = `
                    <a href="${site.reportLink}" target="_blank" rel="noopener noreferrer" class="w-full py-2.5 bg-cyan-600 hover:bg-cyan-500 text-slate-950 font-bold rounded text-xs font-mono flex items-center justify-center gap-2 transition">
                        <i class="fa-solid fa-file-pdf"></i> OPEN NBRI OFFICIAL PDF REPORT
                    </a>
                `;
            } else {
                action.innerHTML = `
                    <button disabled class="w-full py-2.5 bg-slate-800 text-slate-500 rounded text-xs font-mono border border-slate-700 cursor-not-allowed">
                        NO REPORT LINK ATTACHED
                    </button>
                `;
            }
        }

        function renderDistrictSummary() {
            const summaryBody = document.getElementById('district-summary-body');
            summaryBody.innerHTML = '';
            const map = {};
            filteredData.forEach(i => map[i.district] = (map[i.district] || 0) + i.units);

            Object.keys(map).forEach(d => {
                const tr = document.createElement('tr');
                tr.innerHTML = `<td class="py-1.5 font-bold text-cyan-300">${d}</td><td class="py-1.5 text-right text-emerald-400 font-bold">${map[d]}</td>`;
                summaryBody.appendChild(tr);
            });
        }
    </script>
</body>
</html>
"""

# 4. Render Dashboard
html_dashboard = html_template.replace("{{LOGO_URL}}", LOGO_URL)
components.html(html_dashboard, height=1400, scrolling=True)
