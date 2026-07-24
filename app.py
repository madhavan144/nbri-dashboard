import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import json
import os
import requests

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION
# -----------------------------------------------------------------------------
LOGO_URL = "https://96legendssquare.com/wp-content/uploads/2025/08/National-Building-Research-Organization-NBRO.webp"

st.set_page_config(
    page_title="NBRI - IHP 4700 Resettlement Dashboard",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Dark Slate Glassmorphism Theme Styling
st.markdown("""
    <style>
    /* Global App Background */
    .stApp {
        background-color: #0f172a;
        color: #f8fafc;
    }
    
    /* Login Card Styling */
    .login-card {
        max-width: 420px;
        margin: 60px auto;
        padding: 35px;
        background: rgba(30, 41, 59, 0.75);
        border: 1px solid rgba(56, 189, 248, 0.2);
        border-radius: 16px;
        box-shadow: 0 20px 30px -5px rgba(0, 0, 0, 0.6);
        backdrop-filter: blur(12px);
    }
    
    /* Title Customizations */
    .main-title {
        font-size: 26px;
        font-weight: 800;
        color: #38bdf8;
        letter-spacing: 0.5px;
        margin-bottom: 2px;
        text-shadow: 0 0 10px rgba(56, 189, 248, 0.3);
    }
    .sub-title {
        font-size: 13px;
        color: #94a3b8;
        margin-bottom: 10px;
    }
    
    /* KPI Boxes */
    .combined-kpi-box {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.85), rgba(15, 23, 42, 0.95));
        border: 1px solid rgba(56, 189, 248, 0.35);
        border-radius: 12px;
        padding: 12px 16px;
        height: 100%;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    .kpi-box {
        background: rgba(30, 41, 59, 0.65);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 12px 16px;
        text-align: center;
        height: 100%;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    .kpi-label {
        font-size: 11px;
        font-weight: 600;
        color: #94a3b8;
        margin-bottom: 6px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .kpi-val {
        font-size: 22px;
        font-weight: 700;
        color: #f1f5f9;
    }

    /* Discussion Comment Cards */
    .comment-card {
        background-color: #1e293b;
        border-left: 4px solid #38bdf8;
        padding: 10px 14px;
        border-radius: 6px;
        margin-bottom: 10px;
    }
    .comment-user {
        font-size: 12px;
        font-weight: bold;
        color: #cbd5e1;
    }
    .comment-text {
        font-size: 13px;
        color: #f8fafc;
        margin-top: 2px;
    }

    /* Notification Cards */
    .notif-card {
        background: rgba(30, 41, 59, 0.9);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 10px;
        margin-bottom: 8px;
    }
    .notif-title {
        font-size: 13px;
        font-weight: bold;
        color: #38bdf8;
    }
    .notif-time {
        font-size: 10px;
        color: #64748b;
        float: right;
    }
    .notif-body {
        font-size: 12px;
        color: #e2e8f0;
        margin-top: 4px;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. SESSION STATE INITIALIZATION
# -----------------------------------------------------------------------------
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if 'comments' not in st.session_state:
    st.session_state['comments'] = {}

if 'notifications' not in st.session_state:
    st.session_state['notifications'] = [
        {"id": 1, "title": "District Boundary Layer Active", "desc": "sri_lanka_districts.geojson loaded with cyan glow overlay.", "time": "Just now", "unread": True},
        {"id": 2, "title": "NBRI 2nd Report Approved", "desc": "SITE-004 has completed NBRI 2nd Report clearance.", "time": "10 mins ago", "unread": True},
        {"id": 3, "title": "New Comment Added", "desc": "Planning Engineer commented on SITE-012.", "time": "1 hour ago", "unread": True},
        {"id": 4, "title": "BOD Milestone Reached", "desc": "BOD Completed for SITE-002.", "time": "Yesterday", "unread": False},
    ]

# -----------------------------------------------------------------------------
# 3. LOGIN SCREEN
# -----------------------------------------------------------------------------
def login_screen():
    st.markdown("""
        <div style="text-align: center; margin-top: 40px;">
            <h1 style="color: #38bdf8; font-weight: 800; font-size: 32px; text-shadow: 0 0 12px rgba(56, 189, 248, 0.4);">NBRI - IHP 4700 RESETTLEMENT DASHBOARD</h1>
            <p style="color: #94a3b8; font-size: 16px;">Resettlement Progress & Spatial Monitoring of Plantation Sectors</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.1, 1])
    with col2:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.subheader("🔒 Sign In to Dashboard")
        username = st.text_input("Username", value="admin")
        password = st.text_input("Password", type="password", value="1234")
        
        if st.button("Sign In", use_container_width=True, type="primary"):
            if username and password:
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
                st.rerun()
            else:
                st.error("Please enter valid credentials.")
        st.markdown('</div>', unsafe_allow_html=True)

if not st.session_state['logged_in']:
    login_screen()
    st.stop()

# -----------------------------------------------------------------------------
# 4. LOAD DATA & DATA GENERATOR
# -----------------------------------------------------------------------------
@st.cache_data
def load_data():
    np.random.seed(42)
    regions = ["Central", "Uva", "Sabaragamuwa", "Western"]
    districts = ["Kandy", "Nuwara Eliya", "Badulla", "Ratnapura", "Kegalle"]
    ias = ["IA-Alpha", "IA-Beta", "IA-Gamma"]
    rpcs = ["Kelani Valley", "Maskeliya", "Bogawantalawa", "Elpitiya"]

    data = []
    for i in range(1, 41):
        rep1 = np.random.choice([True, False], p=[0.8, 0.2])
        bod = np.random.choice([True, False], p=[0.6, 0.4]) if rep1 else False
        rep2 = np.random.choice([True, False], p=[0.4, 0.6]) if (rep1 and bod) else False
        concept = np.random.choice(["Completed", "In Progress", "Pending"])

        data.append({
            "Site_ID": f"SITE-{i:03d}",
            "Site_Name": f"Estate Site {i}",
            "Region": np.random.choice(regions),
            "District": np.random.choice(districts),
            "IA": np.random.choice(ias),
            "RPC": np.random.choice(rpcs),
            "Units_Planned": int(np.random.randint(25, 150)),
            "Latitude": float(6.9 + np.random.uniform(-0.3, 0.5)),
            "Longitude": float(80.6 + np.random.uniform(-0.3, 0.5)),
            "NBRI_1st_Report": rep1,
            "Conceptual_Plan": concept,
            "BOD_Completed": bod,
            "NBRI_2nd_Report": rep2,
            "Report_Link": f"https://www.google.com/search?q=Estate+Site+{i}+NBRI+Report"
        })
    return pd.DataFrame(data)

df = load_data()

# -----------------------------------------------------------------------------
# 5. HEADER & SYSTEM ALERTS
# -----------------------------------------------------------------------------
head_left, head_right = st.columns([3, 1])

with head_left:
    st.markdown('<div class="main-title">NBRI - IHP 4700 RESETTLEMENT DASHBOARD</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Resettlement Progress & Spatial Monitoring of Plantation Sectors</div>', unsafe_allow_html=True)

with head_right:
    btn_col1, btn_col2 = st.columns([1, 1])
    
    unread_count = sum(1 for n in st.session_state['notifications'] if n['unread'])
    notif_label = f"🔔 ({unread_count})" if unread_count > 0 else "🔔"
    
    with btn_col1:
        with st.popover(notif_label):
            st.markdown("### 🔔 System Alerts")
            if st.button("Mark all as read", type="secondary", key="mark_read_btn"):
                for n in st.session_state['notifications']:
                    n['unread'] = False
                st.rerun()
            
            st.markdown("---")
            for notif in st.session_state['notifications']:
                unread_badge = "🔴 " if notif['unread'] else ""
                st.markdown(f"""
                    <div class="notif-card">
                        <span class="notif-time">{notif['time']}</span>
                        <div class="notif-title">{unread_badge}{notif['title']}</div>
                        <div class="notif-body">{notif['desc']}</div>
                    </div>
                """, unsafe_allow_html=True)
                
    with btn_col2:
        if st.button("Logout"):
            st.session_state['logged_in'] = False
            st.rerun()

# -----------------------------------------------------------------------------
# 6. GLOBAL FILTER BAR
# -----------------------------------------------------------------------------
f_col1, f_col2, f_col3, f_col4 = st.columns(4)

with f_col1:
    selected_region = st.selectbox("Regions", ["All"] + list(df["Region"].unique()))
with f_col2:
    selected_district = st.selectbox("Districts", ["All"] + list(df["District"].unique()))
with f_col3:
    selected_ia = st.selectbox("IA", ["All"] + list(df["IA"].unique()))
with f_col4:
    selected_rpc = st.selectbox("RPC", ["All"] + list(df["RPC"].unique()))

# Filter Dataset
filtered_df = df.copy()
if selected_region != "All":
    filtered_df = filtered_df[filtered_df["Region"] == selected_region]
if selected_district != "All":
    filtered_df = filtered_df[filtered_df["District"] == selected_district]
if selected_ia != "All":
    filtered_df = filtered_df[filtered_df["IA"] == selected_ia]
if selected_rpc != "All":
    filtered_df = filtered_df[filtered_df["RPC"] == selected_rpc]

st.markdown("---")

# -----------------------------------------------------------------------------
# 7. METRIC KPI OVERVIEW (5 KPI CARDS)
# -----------------------------------------------------------------------------
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

with kpi1:
    total_sites = len(filtered_df)
    total_units = filtered_df["Units_Planned"].sum() if not filtered_df.empty else 0
    st.markdown(f"""
        <div class="combined-kpi-box">
            <div style="margin-bottom: 6px;">
                <span class="kpi-label">Sites:</span> 
                <span style="font-size: 18px; font-weight: 700; color: #38bdf8;">{total_sites}</span>
            </div>
            <div>
                <span class="kpi-label">Units Planned:</span> 
                <span style="font-size: 18px; font-weight: 700; color: #38bdf8;">{total_units}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

with kpi2:
    rep1_count = filtered_df["NBRI_1st_Report"].sum() if not filtered_df.empty else 0
    st.markdown(f"""
        <div class="kpi-box">
            <div class="kpi-label">NBRI 1st Report</div>
            <div class="kpi-val" style="color: #f59e0b;">{rep1_count}</div>
        </div>
    """, unsafe_allow_html=True)

with kpi3:
    concept_count = len(filtered_df[filtered_df["Conceptual_Plan"] == "Completed"]) if not filtered_df.empty else 0
    st.markdown(f"""
        <div class="kpi-box">
            <div class="kpi-label">Conceptual Layout</div>
            <div class="kpi-val" style="color: #a855f7;">{concept_count}</div>
        </div>
    """, unsafe_allow_html=True)

with kpi4:
    bod_count = filtered_df["BOD_Completed"].sum() if not filtered_df.empty else 0
    st.markdown(f"""
        <div class="kpi-box">
            <div class="kpi-label">BOD Completed</div>
            <div class="kpi-val" style="color: #3b82f6;">{bod_count}</div>
        </div>
    """, unsafe_allow_html=True)

with kpi5:
    rep2_count = filtered_df["NBRI_2nd_Report"].sum() if not filtered_df.empty else 0
    st.markdown(f"""
        <div class="kpi-box">
            <div class="kpi-label">NBRI 2nd Report</div>
            <div class="kpi-val" style="color: #10b981;">{rep2_count}</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 8. HYBRID DASHBOARD INTEGRATION (GIS MAP + ANALYTICAL CHARTS + DISCUSSIONS)
# -----------------------------------------------------------------------------
data_json = filtered_df.to_json(orient="records")

html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

    <style>
        body {{
            background-color: #0f172a;
            color: #e2e8f0;
            font-family: sans-serif;
            margin: 0;
            padding: 0;
        }}
        .glass-panel {{
            background: rgba(30, 41, 59, 0.7);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
        }}
        .glowing-pin {{
            display: block;
            width: 14px;
            height: 14px;
            border-radius: 50%;
            background: #06b6d4;
            box-shadow: 0 0 10px #06b6d4, 0 0 20px #06b6d4;
        }}
        .glowing-pin.completed {{
            background: #10b981;
            box-shadow: 0 0 10px #10b981, 0 0 20px #10b981;
        }}
        .glowing-pin.pending {{
            background: #f59e0b;
            box-shadow: 0 0 10px #f59e0b, 0 0 20px #f59e0b;
        }}
        .leaflet-container {{
            background: #050811 !important;
        }}
        .leaflet-popup-content-wrapper {{
            background: rgba(15, 23, 42, 0.95) !important;
            color: #f8fafc !important;
            border: 1px solid rgba(56, 189, 248, 0.4);
            border-radius: 12px !important;
        }}
        .leaflet-popup-tip {{
            background: rgba(15, 23, 42, 0.95) !important;
        }}
    </style>
</head>
<body class="p-2">

    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        <!-- LEFT 8 COLUMNS: GIS MAP & CHARTS -->
        <div class="lg:col-span-8 flex flex-col gap-6">
            
            <!-- GIS MAP -->
            <div class="glass-panel rounded-2xl p-4">
                <div class="flex items-center justify-between mb-3">
                    <h3 class="text-sm font-bold text-cyan-400 flex items-center gap-2">
                        <i class="fa-solid fa-map-location-dot"></i> Interactive GIS Spatial Map (Esri Dark Navigation)
                    </h3>
                    <span class="text-xs text-slate-400">Filtered Sites Focus</span>
                </div>
                <div id="map" class="w-full h-[400px] rounded-xl border border-slate-700"></div>
            </div>

            <!-- ANALYTICS CHART -->
            <div class="glass-panel rounded-2xl p-4">
                <h3 class="text-sm font-bold text-white mb-3 flex items-center gap-2">
                    <i class="fa-solid fa-chart-column text-cyan-400"></i> District-wise Housing Capacity Breakdown
                </h3>
                <div class="relative h-[250px] w-full">
                    <canvas id="districtChart"></canvas>
                </div>
            </div>

            <!-- SITE TABLE -->
            <div class="glass-panel rounded-2xl p-4">
                <h3 class="text-sm font-bold text-white mb-3 flex items-center gap-2">
                    <i class="fa-solid fa-table text-purple-400"></i> Resettlement Sites Registry
                </h3>
                <div class="max-h-[250px] overflow-y-auto border border-slate-800 rounded-xl">
                    <table class="w-full text-left text-xs text-slate-300">
                        <thead class="bg-slate-900 sticky top-0 text-slate-400 font-semibold uppercase">
                            <tr>
                                <th class="p-2">Site ID</th>
                                <th class="p-2">Site Name</th>
                                <th class="p-2">District</th>
                                <th class="p-2 text-right">Units</th>
                                <th class="p-2 text-center">1st Report</th>
                                <th class="p-2 text-center">BOD</th>
                                <th class="p-2 text-center">Link</th>
                            </tr>
                        </thead>
                        <tbody id="table-body" class="divide-y divide-slate-800"></tbody>
                    </table>
                </div>
            </div>

        </div>

        <!-- RIGHT 4 COLUMNS: SITE DETAILS & AI ASSISTANT -->
        <div class="lg:col-span-4 flex flex-col gap-6">
            
            <!-- TECHNICAL CARD DETAILS -->
            <div class="glass-panel rounded-2xl p-4 border border-cyan-500/30">
                <h3 class="text-sm font-bold text-white mb-2 flex items-center gap-2">
                    <i class="fa-solid fa-circle-info text-cyan-400"></i> Technical Site Inspector
                </h3>
                <div id="site-card-content" class="bg-slate-950 p-3 rounded-xl border border-slate-800 text-xs space-y-2">
                    <p class="text-slate-400 italic">Click any marker or table row to view full site parameters.</p>
                </div>
            </div>

            <!-- HSPTD AI ASSISTANT -->
            <div class="glass-panel rounded-2xl p-4 border border-purple-500/30">
                <h3 class="text-sm font-bold text-white mb-2 flex items-center gap-2">
                    <i class="fa-solid fa-wand-magic-sparkles text-purple-400"></i> HSPTD AI Assistant
                </h3>
                <div id="ai-chat-box" class="h-[180px] overflow-y-auto p-3 bg-slate-950 rounded-xl border border-slate-800 text-xs space-y-2 mb-2">
                    <div class="bg-slate-900 p-2 rounded-lg text-slate-300">
                        <strong>AI:</strong> Ayubowan! Ask me anything regarding site progress or report links.
                    </div>
                </div>
                <div class="flex gap-2">
                    <input type="text" id="ai-input" placeholder="Ask AI query..." class="w-full bg-slate-900 text-xs text-slate-200 px-3 py-2 rounded-xl border border-slate-700 focus:outline-none">
                    <button onclick="sendAI()" class="bg-purple-600 px-3 py-2 rounded-xl text-xs text-white font-bold"><i class="fa-solid fa-paper-plane"></i></button>
                </div>
            </div>

        </div>

    </div>

    <script>
        const rawData = {data_json};
        let map, chart;

        document.addEventListener('DOMContentLoaded', () => {{
            initMap();
            initChart();
            renderTable();
        }});

        function initMap() {{
            map = L.map('map').setView([7.1, 80.6], 8);
            L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{{z}}/{{y}}/{{x}}', {{
                maxZoom: 18,
                attribution: 'Tiles &copy; Esri'
            }}).addTo(map);

            const bounds = [];
            rawData.forEach(site => {{
                let pinClass = site.NBRI_2nd_Report ? 'completed' : (site.NBRI_1st_Report ? '' : 'pending');
                const customIcon = L.divIcon({{
                    className: 'custom-pin',
                    html: `<span class="glowing-pin ${{pinClass}}"></span>`,
                    iconSize: [14, 14]
                }});

                const marker = L.marker([site.Latitude, site.Longitude], {{ icon: customIcon }}).addTo(map);
                marker.bindPopup(`<b>${{site.Site_Name}}</b><br>District: ${{site.District}}<br>Units: ${{site.Units_Planned}}`);
                marker.on('click', () => showSiteDetails(site));
                bounds.push([site.Latitude, site.Longitude]);
            }});

            if (bounds.length > 0) map.fitBounds(bounds, {{ padding: [20, 20] }});
        }}

        function initChart() {{
            const distMap = {{}};
            rawData.forEach(d => {{
                distMap[d.District] = (distMap[d.District] || 0) + d.Units_Planned;
            }});

            const ctx = document.getElementById('districtChart').getContext('2d');
            chart = new Chart(ctx, {{
                type: 'bar',
                data: {{
                    labels: Object.keys(distMap),
                    datasets: [{{
                        label: 'Units Planned',
                        data: Object.values(distMap),
                        backgroundColor: '#06b6d4',
                        borderRadius: 6
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{ legend: {{ display: false }} }},
                    scales: {{
                        x: {{ ticks: {{ color: '#94a3b8' }} }},
                        y: {{ ticks: {{ color: '#06b6d4' }} }}
                    }}
                }}
            }});
        }}

        function renderTable() {{
            const tbody = document.getElementById('table-body');
            tbody.innerHTML = '';
            rawData.forEach(row => {{
                const tr = document.createElement('tr');
                tr.className = 'hover:bg-slate-800 cursor-pointer border-b border-slate-800/50';
                tr.onclick = () => showSiteDetails(row);
                tr.innerHTML = `
                    <td class="p-2 font-mono text-cyan-400">${{row.Site_ID}}</td>
                    <td class="p-2 font-bold text-white">${{row.Site_Name}}</td>
                    <td class="p-2">${{row.District}}</td>
                    <td class="p-2 text-right font-bold text-emerald-400">${{row.Units_Planned}}</td>
                    <td class="p-2 text-center">${{row.NBRI_1st_Report ? 'Yes' : 'No'}}</td>
                    <td class="p-2 text-center">${{row.BOD_Completed ? 'Yes' : 'No'}}</td>
                    <td class="p-2 text-center">
                        <a href="${{row.Report_Link}}" target="_blank" class="text-cyan-400 hover:underline"><i class="fa-solid fa-file-pdf"></i></a>
                    </td>
                `;
                tbody.appendChild(tr);
            }});
        }}

        function showSiteDetails(site) {{
            const box = document.getElementById('site-card-content');
            box.innerHTML = `
                <div class="font-bold text-cyan-400 text-sm mb-1">${{site.Site_Name}} (${{site.Site_ID}})</div>
                <div><b>Region / District:</b> ${{site.Region}} / ${{site.District}}</div>
                <div><b>IA / RPC:</b> ${{site.IA}} / ${{site.RPC}}</div>
                <div><b>Planned Units:</b> <span class="text-emerald-400 font-bold">${{site.Units_Planned}}</span></div>
                <div><b>1st Report Issued:</b> ${{site.NBRI_1st_Report ? 'Yes' : 'No'}}</div>
                <div><b>BOD Clearance:</b> ${{site.BOD_Completed ? 'Yes' : 'No'}}</div>
                <div><b>2nd Report Issued:</b> ${{site.NBRI_2nd_Report ? 'Yes' : 'No'}}</div>
                <div><b>Conceptual Plan:</b> ${{site.Conceptual_Plan}}</div>
                <div class="mt-2">
                    <a href="${{site.Report_Link}}" target="_blank" class="block text-center py-1 bg-cyan-600 text-white rounded-lg font-bold">Open Report Link</a>
                </div>
            `;
            if (map) map.setView([site.Latitude, site.Longitude], 12);
        }}

        function sendAI() {{
            const input = document.getElementById('ai-input');
            const val = input.value.trim();
            if (!val) return;
            const chat = document.getElementById('ai-chat-box');
            chat.innerHTML += `<div class="bg-purple-900/50 p-2 rounded-lg text-white"><b>You:</b> ${{val}}</div>`;
            input.value = '';
            setTimeout(() => {{
                chat.innerHTML += `<div class="bg-slate-900 p-2 rounded-lg text-slate-300"><b>AI:</b> Analyzed query for "${{val}}". Total ${{rawData.length}} filtered sites match active criteria.</div>`;
                chat.scrollTop = chat.scrollHeight;
            }}, 300);
        }}
    </script>
</body>
</html>
"""

components.html(html_template, height=920, scrolling=True)

# -----------------------------------------------------------------------------
# 9. INTERACTIVE FIELD DISCUSSION THREAD
# -----------------------------------------------------------------------------
st.markdown("---")
st.subheader("💬 Site Discussion & Field Observations")

disc_col1, disc_col2 = st.columns([1, 1])

with disc_col1:
    site_list = filtered_df["Site_Name"].tolist() if not filtered_df.empty else ["No Sites Available"]
    selected_site_name = st.selectbox("Select Site for Thread:", site_list)

with disc_col2:
    if not filtered_df.empty and selected_site_name in site_list:
        site_info = filtered_df[filtered_df["Site_Name"] == selected_site_name].iloc[0]
        site_id = site_info["Site_ID"]
        
        st.markdown(f"**Discussion Thread for {selected_site_name} (`{site_id}`)**")
        
        if site_id not in st.session_state['comments']:
            st.session_state['comments'][site_id] = [
                {"user": "Site Inspector", "text": "District boundary checked. Site topography verified."},
                {"user": "Project Engineer", "text": "NBRI 1st Report clearance submitted for approval."}
            ]
        
        for comment in st.session_state['comments'][site_id]:
            st.markdown(f"""
                <div class="comment-card">
                    <div class="comment-user">👤 {comment['user']}</div>
                    <div class="comment-text">{comment['text']}</div>
                </div>
            """, unsafe_allow_html=True)
            
        with st.form(key=f"comment_form_{site_id}", clear_on_submit=True):
            new_comment = st.text_area("Post Field Observation Note:", height=70)
            submit_btn = st.form_submit_button("Submit Note")
            if submit_btn and new_comment.strip():
                st.session_state['comments'][site_id].append({
                    "user": st.session_state.get('username', 'User'),
                    "text": new_comment.strip()
                })
                st.session_state['notifications'].insert(0, {
                    "id": len(st.session_state['notifications']) + 1,
                    "title": f"New Note on {site_id}",
                    "desc": f"{st.session_state.get('username', 'User')}: {new_comment.strip()[:30]}...",
                    "time": "Just now",
                    "unread": True
                })
                st.success("Note posted successfully!")
                st.rerun()

# -----------------------------------------------------------------------------
# 10. FOOTER & LEGEND
# -----------------------------------------------------------------------------
st.markdown("---")
st.markdown("##### 🎨 Spatial Map Stage Legend")
leg1, leg2, leg3 = st.columns(3)
leg1.markdown("🟢 **Green:** `2nd Report Issued (Completed)`")
leg2.markdown("🔵 **Cyan:** `1st Report Issued (In Progress)`")
leg3.markdown("🟡 **Amber:** `Pending Report Clearance`")
