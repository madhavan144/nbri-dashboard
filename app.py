import streamlit as st
import streamlit.components.v1 as components
import os
import json
import csv
import io
import urllib.request
from datetime import datetime

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================
LOGO_URL = "https://96legendssquare.com/wp-content/uploads/2025/08/National-Building-Research-Organization-NBRO.webp"
BG_IMAGE_URL = "https://images.unsplash.com/photo-1625337905916-f1172a75d5b8?fm=jpg&q=80&w=1920&auto=format&fit=crop"

st.set_page_config(
    page_title="IHP Resettlement Progress Dashboard",
    page_icon=LOGO_URL,
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# 2. CSS STYLING & FULLSCREEN OVERRIDE
# ==========================================
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

# ==========================================
# 2b. LOAD LOCAL DISTRICT GEOJSON (uploaded layer sitting next to app.py)
# ==========================================
def load_local_district_geojson():
    """
    Looks for the district boundary geojson file uploaded to the repo, in the same
    folder as this app.py. Update DISTRICT_GEOJSON_FILENAME below if you rename it.
    Returns the parsed geojson as a Python object, or None if not found so the
    dashboard can fall back to a remote boundary source instead.
    """
    candidate_names = ["sri_lanka_districts.geojson", "sri_lanka_districts.geojson.json"]
    base_dir = os.path.dirname(os.path.abspath(__file__))
    for name in candidate_names:
        path = os.path.join(base_dir, name)
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return None
    return None

DISTRICT_GEOJSON_DATA = load_local_district_geojson()
DISTRICT_GEOJSON_JS = json.dumps(DISTRICT_GEOJSON_DATA) if DISTRICT_GEOJSON_DATA else "null"

# ==========================================
# 2c. LOGIN / SIGNUP GATE
# ==========================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "users" not in st.session_state:
    # Demo in-memory user store. Replace with a real database/auth provider for production.
    st.session_state.users = {"admin": "admin123"}
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"
if "current_user" not in st.session_state:
    st.session_state.current_user = ""

def render_login_gate():
    st.markdown(f"""
        <style>
            .stApp {{
                background: linear-gradient(rgba(4, 8, 20, 0.88), rgba(4, 8, 20, 0.92)), url('{BG_IMAGE_URL}');
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
            }}
            .auth-wrapper {{
                max-width: 420px;
                margin: 6vh auto 2rem auto;
                padding: 2.5rem 2.25rem;
                border-radius: 20px;
                background: rgba(15, 20, 38, 0.88);
                border: 1px solid rgba(6, 182, 212, 0.25);
                box-shadow: 0 20px 50px -15px rgba(0,0,0,0.7), 0 0 30px rgba(6, 182, 212, 0.08);
                backdrop-filter: blur(10px);
                text-align: center;
            }}
            .auth-wrapper img {{
                width: 64px;
                height: 64px;
                object-fit: contain;
                margin-bottom: 0.75rem;
            }}
            .auth-title {{
                color: #f8fafc;
                font-size: 1.35rem;
                font-weight: 800;
                letter-spacing: 0.02em;
                margin-bottom: 0.15rem;
            }}
            .auth-subtitle {{
                color: #94a3b8;
                font-size: 0.85rem;
                margin-bottom: 1.5rem;
            }}
            div[data-testid="stForm"] {{
                background: transparent;
                border: none;
            }}
        </style>
    """, unsafe_allow_html=True)

    st.markdown(f"""
        <div class="auth-wrapper">
            <img src="{LOGO_URL}" alt="Logo">
            <div class="auth-title">IHP 4700 RESETTLEMENT DASHBOARD</div>
            <div class="auth-subtitle">Secure access &middot; Resettlement Progress & Spatial Monitoring</div>
        </div>
    """, unsafe_allow_html=True)

    _, col, _ = st.columns([1, 1.3, 1])
    with col:
        tab_login, tab_signup = st.tabs(["Login", "Sign Up"])

        with tab_login:
            with st.form("login_form", clear_on_submit=False):
                username = st.text_input("Username", key="login_user")
                password = st.text_input("Password", type="password", key="login_pass")
                submitted = st.form_submit_button("Log In", use_container_width=True)
                if submitted:
                    if username in st.session_state.users and st.session_state.users[username] == password:
                        st.session_state.authenticated = True
                        st.session_state.current_user = username
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")

        with tab_signup:
            with st.form("signup_form", clear_on_submit=False):
                new_user = st.text_input("Choose a username", key="signup_user")
                new_pass = st.text_input("Choose a password", type="password", key="signup_pass")
                confirm_pass = st.text_input("Confirm password", type="password", key="signup_confirm")
                signed_up = st.form_submit_button("Create Account", use_container_width=True)
                if signed_up:
                    if not new_user or not new_pass:
                        st.error("Please fill in all fields.")
                    elif new_pass != confirm_pass:
                        st.error("Passwords do not match.")
                    elif new_user in st.session_state.users:
                        st.error("That username is already taken.")
                    else:
                        st.session_state.users[new_user] = new_pass
                        st.success("Account created! Please log in from the Login tab.")

    st.caption("Demo credentials: admin / admin123 (replace with real authentication before production use).")

if not st.session_state.authenticated:
    render_login_gate()
    st.stop()

# ==========================================
# 2d. LIVE SHEET-UPDATE NOTIFICATIONS
# ==========================================
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRGEDtnF-wjT39hcvY3tkA_PpRO1FM06-M267dOBvKYGYlgD-udcevC8LrWGjM_XA/pub?gid=143716875&single=true&output=csv"

# Columns that count as "important" when they change for an existing site
WATCHED_FIELDS = [
    ("NBRI 1st Report - Issued", "NBRI 1st Report Issued"),
    ("BOD Completed", "BOD Completed"),
    ("NBRI Conceptual Design", "Conceptual Plan"),
    ("NBRI 2nd Report - Issued", "NBRI 2nd Report Issued"),
]

def fetch_sheet_rows():
    """Downloads and parses the published Google Sheet CSV. Returns a list of dict rows, or None on failure."""
    try:
        req = urllib.request.Request(SHEET_CSV_URL, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=12) as resp:
            raw = resp.read().decode("utf-8", errors="ignore")
        reader = csv.DictReader(io.StringIO(raw))
        return list(reader)
    except Exception:
        return None

def row_key(row):
    district = (row.get("District") or row.get("district") or "").strip()
    estate = (row.get("Estate") or row.get("estate") or "").strip()
    division = (row.get("Division") or row.get("division") or "").strip()
    return f"{district}|{estate}|{division}"

def watched_value(row, field_name):
    for key in field_name:
        if key in row:
            return (row.get(key) or "").strip()
    return ""

def get_field_variants(field_label):
    variants_map = {
        "NBRI 1st Report - Issued": ["NBRI 1st Report - Issued", "NBRI 1st Report Issued"],
        "BOD Completed": ["BOD Completed"],
        "NBRI Conceptual Design": ["NBRI Conceptual Design"],
        "NBRI 2nd Report - Issued": ["NBRI 2nd Report - Issued", "NBRI 2nd Report Issued"],
    }
    return variants_map.get(field_label, [field_label])

def check_for_sheet_updates(silent_baseline=False):
    """Fetches the sheet, compares to the last known snapshot, and appends any
    new/changed-site notifications to session_state.notifications."""
    rows = fetch_sheet_rows()
    if rows is None:
        return

    new_snapshot = {}
    fresh_notifications = []

    for row in rows:
        key = row_key(row)
        if not key.strip("|"):
            continue
        watched = {label: watched_value(row, get_field_variants(label)) for label, _ in WATCHED_FIELDS}
        new_snapshot[key] = watched

        old_watched = st.session_state.sheet_snapshot.get(key)
        estate_name = (row.get("Estate") or row.get("estate") or "Site").strip()

        if old_watched is None:
            if not silent_baseline:
                fresh_notifications.append(f"New site added to the sheet: **{estate_name}**")
        else:
            for label, display_name in WATCHED_FIELDS:
                if old_watched.get(label, "") != watched.get(label, ""):
                    fresh_notifications.append(
                        f"**{display_name}** updated for **{estate_name}**: "
                        f"\"{old_watched.get(label, '') or '—'}\" → \"{watched.get(label, '') or '—'}\""
                    )

    st.session_state.sheet_snapshot = new_snapshot
    if fresh_notifications:
        stamp = datetime.now().strftime("%d %b %Y, %I:%M %p")
        for msg in fresh_notifications:
            st.session_state.notifications.insert(0, {"text": msg, "time": stamp, "read": False})
        st.session_state.notifications = st.session_state.notifications[:50]

if "sheet_snapshot" not in st.session_state:
    st.session_state.sheet_snapshot = {}
if "notifications" not in st.session_state:
    st.session_state.notifications = []
if "show_notifications" not in st.session_state:
    st.session_state.show_notifications = False
if "sheet_baseline_done" not in st.session_state:
    # Establish a silent baseline on first load so we don't flag all existing rows as "new"
    check_for_sheet_updates(silent_baseline=True)
    st.session_state.sheet_baseline_done = True

# ==========================================
# 3. HTML, CSS, JS INTEGRATED DASHBOARD TEMPLATE
# ==========================================
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IHP 4700 Resettlement Progress Dashboard</title>
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
            background: #64748b;
            box-shadow: 0 0 10px #64748b, 0 0 20px #64748b;
            animation: pulse-slate 2s infinite;
        }
        /* Stage 1: NBRI 1st Report Issued only - Dark Blue */
        .glowing-pin.stage-1 {
            background: #1d4ed8;
            box-shadow: 0 0 10px #1d4ed8, 0 0 20px #1d4ed8;
            animation: pulse-stage1 2s infinite;
        }
        /* Stage 2: NBRI 1st Report Issued + BOD Completed - Light Blue */
        .glowing-pin.stage-2 {
            background: #38bdf8;
            box-shadow: 0 0 10px #38bdf8, 0 0 20px #38bdf8;
            animation: pulse-stage2 2s infinite;
        }
        /* Stage 3: NBRI 1st Report Issued + BOD Completed + NBRI 2nd Report Issued - Gold/Yellow */
        .glowing-pin.stage-3 {
            background: #eab308;
            box-shadow: 0 0 10px #eab308, 0 0 20px #eab308;
            animation: pulse-stage3 2s infinite;
        }

        @keyframes pulse-stage1 {
            0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(29, 78, 216, 0.8); }
            70% { transform: scale(1.3); box-shadow: 0 0 0 12px rgba(29, 78, 216, 0); }
            100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(29, 78, 216, 0); }
        }
        @keyframes pulse-stage2 {
            0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(56, 189, 248, 0.8); }
            70% { transform: scale(1.3); box-shadow: 0 0 0 12px rgba(56, 189, 248, 0); }
            100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(56, 189, 248, 0); }
        }
        @keyframes pulse-stage3 {
            0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(234, 179, 8, 0.8); }
            70% { transform: scale(1.3); box-shadow: 0 0 0 12px rgba(234, 179, 8, 0); }
            100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(234, 179, 8, 0); }
        }
        @keyframes pulse-slate {
            0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(100, 116, 139, 0.8); }
            70% { transform: scale(1.3); box-shadow: 0 0 0 12px rgba(100, 116, 139, 0); }
            100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(100, 116, 139, 0); }
        }

        .leaflet-container {
            background: #050811 !important;
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

        /* Outline Glow Style for Boundaries */
        .district-boundary-glow {
            filter: drop-shadow(0px 0px 8px #06b6d4) drop-shadow(0px 0px 15px rgba(168, 85, 247, 0.6));
            transition: all 0.4s ease-in-out;
        }
        .district-boundary-active {
            filter: drop-shadow(0px 0px 12px #a855f7) drop-shadow(0px 0px 25px #06b6d4);
            transition: all 0.4s ease-in-out;
        }
        .country-border-glow {
            filter: drop-shadow(0px 0px 6px #06b6d4) drop-shadow(0px 0px 14px rgba(6, 182, 212, 0.7));
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
                        <h1 class="text-xl font-bold tracking-tight text-white">IHP 4700 RESETTLEMENT DASHBOARD</h1>
                        <span class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                            <span class="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span> Live Tracker Sync
                        </span>
                    </div>
                    <p class="text-xs text-slate-400">Resettlement Progress & Spatial Monitoring of Plantation Sectors</p>
                </div>
            </div>

            <!-- FILTERS & RELOAD -->
            <div class="flex flex-wrap items-center gap-3 w-full md:w-auto">
                <div class="relative flex-1 md:flex-initial">
                    <i class="fa-solid fa-layer-group absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-xs"></i>
                    <select id="filter-region" class="w-full bg-slate-900/90 text-xs text-slate-200 pl-8 pr-8 py-2 rounded-xl border border-slate-700 focus:border-cyan-500 focus:outline-none appearance-none cursor-pointer">
                        <option value="ALL">Regions</option>
                    </select>
                    <i class="fa-solid fa-chevron-down absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 text-[10px]"></i>
                </div>

                <div class="relative flex-1 md:flex-initial">
                    <i class="fa-solid fa-map-location-dot absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-xs"></i>
                    <select id="filter-district" class="w-full bg-slate-900/90 text-xs text-slate-200 pl-8 pr-8 py-2 rounded-xl border border-slate-700 focus:border-cyan-500 focus:outline-none appearance-none cursor-pointer">
                        <option value="ALL">Districts</option>
                    </select>
                    <i class="fa-solid fa-chevron-down absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 text-[10px]"></i>
                </div>

                <div class="relative flex-1 md:flex-initial">
                    <i class="fa-solid fa-building-user absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-xs"></i>
                    <select id="filter-ia" class="w-full bg-slate-900/90 text-xs text-slate-200 pl-8 pr-8 py-2 rounded-xl border border-slate-700 focus:border-cyan-500 focus:outline-none appearance-none cursor-pointer">
                        <option value="ALL">IA</option>
                    </select>
                    <i class="fa-solid fa-chevron-down absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 text-[10px]"></i>
                </div>

                <div class="relative flex-1 md:flex-initial">
                    <i class="fa-solid fa-industry absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-xs"></i>
                    <select id="filter-rpc" class="w-full bg-slate-900/90 text-xs text-slate-200 pl-8 pr-8 py-2 rounded-xl border border-slate-700 focus:border-cyan-500 focus:outline-none appearance-none cursor-pointer">
                        <option value="ALL">RPC</option>
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
        <section class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4 mb-6">

            <!-- COMBINED SITES + UNITS BOX -->
            <div class="glass-panel p-5 rounded-2xl relative overflow-hidden group hover:border-cyan-500/40 transition">
                <div class="flex items-center justify-between mb-3">
                    <span class="text-xs font-medium text-slate-400 uppercase tracking-wider">Number of Sites</span>
                    <div class="w-9 h-9 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400">
                        <i class="fa-solid fa-location-dot"></i>
                    </div>
                </div>
                <div class="flex items-baseline gap-3">
                    <h2 id="kpi-total-sites" class="text-3xl font-extrabold text-white">--</h2>
                    <span class="text-xs text-emerald-400 font-semibold flex items-center gap-1">Active Sites</span>
                </div>
                <div class="border-t border-slate-800/80 my-3"></div>
                <div class="flex items-center justify-between mb-1">
                    <span class="text-xs font-medium text-slate-400 uppercase tracking-wider">Number of Units Planned</span>
                    <div class="w-9 h-9 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400">
                        <i class="fa-solid fa-house-chimney"></i>
                    </div>
                </div>
                <div class="flex items-baseline gap-3">
                    <h2 id="kpi-total-units" class="text-3xl font-extrabold text-white">--</h2>
                    <span class="text-xs text-cyan-400 font-semibold">Housing Units</span>
                </div>
            </div>

            <div class="glass-panel p-5 rounded-2xl relative overflow-hidden group hover:border-purple-500/40 transition">
                <div class="flex items-center justify-between mb-3">
                    <span class="text-xs font-medium text-slate-400 uppercase tracking-wider">NBRI 1st Report Issued</span>
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
                <p id="kpi-report-units" class="text-[11px] text-slate-500 mt-2">NBRI 1st Report - Units: 0</p>
            </div>

            <div class="glass-panel p-5 rounded-2xl relative overflow-hidden group hover:border-indigo-500/40 transition">
                <div class="flex items-center justify-between mb-3">
                    <span class="text-xs font-medium text-slate-400 uppercase tracking-wider">Conceptual Plan Issued</span>
                    <div class="w-9 h-9 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
                        <i class="fa-solid fa-sitemap"></i>
                    </div>
                </div>
                <div class="flex items-baseline gap-3">
                    <h2 id="kpi-conceptual-issued" class="text-3xl font-extrabold text-white">--</h2>
                    <span id="kpi-conceptual-pct" class="text-xs text-indigo-400 font-semibold">--%</span>
                </div>
                <p id="kpi-conceptual-detail" class="text-[11px] text-slate-500 mt-2">Conceptual subdivision layout status</p>
                <p id="kpi-conceptual-units" class="text-[11px] text-slate-500 mt-1">NBRI Conceptual Design - Units: 0</p>
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
                <p id="kpi-bod-units" class="text-[11px] text-slate-500 mt-1">BOD Marked on Ground: 0</p>
            </div>

            <div class="glass-panel p-5 rounded-2xl relative overflow-hidden group hover:border-amber-500/40 transition">
                <div class="flex items-center justify-between mb-3">
                    <span class="text-xs font-medium text-slate-400 uppercase tracking-wider">NBRI 2nd Report Issued</span>
                    <div class="w-9 h-9 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
                        <i class="fa-solid fa-file-circle-check"></i>
                    </div>
                </div>
                <div class="flex items-baseline gap-3">
                    <h2 id="kpi-report2-issued" class="text-3xl font-extrabold text-white">--</h2>
                    <span id="kpi-report2-pct" class="text-xs text-amber-400 font-semibold">--%</span>
                </div>
                <div class="w-full bg-slate-800 h-1.5 rounded-full mt-3 overflow-hidden">
                    <div id="kpi-report2-bar" class="bg-gradient-to-r from-amber-500 to-orange-500 h-full w-0 transition-all duration-700"></div>
                </div>
                <p id="kpi-report2-units" class="text-[11px] text-slate-500 mt-2">NBRI 2nd Report - Units: 0</p>
            </div>
        </section>

        <!-- DASHBOARD BODY -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
            
            <!-- LEFT 8 COLS -->
            <div class="lg:col-span-8 flex flex-col gap-6">
                
                <!-- GIS MAP WITH ESRI WORLD NAVIGATION DARK BASEMAP & GLOWING ADMINISTRATIVE BOUNDARIES -->
                <div class="glass-panel rounded-2xl p-5 relative flex flex-col">
                    <div class="flex items-center justify-between mb-4">
                        <div class="flex items-center gap-2.5">
                            <div class="w-3 h-3 rounded-full bg-cyan-400 animate-pulse shadow-lg shadow-cyan-400"></div>
                            <h3 class="text-base font-bold text-white">Interactive GIS Map (Esri Dark Navigation & Glowing Boundaries)</h3>
                        </div>
                        <span id="district-tag" class="hidden text-xs px-3 py-1 rounded-lg bg-purple-500/20 text-purple-300 border border-purple-500/40 shadow-lg shadow-purple-500/20 font-medium">
                            <i class="fa-solid fa-bullseye mr-1 animate-spin"></i> Active Glowing Boundary Focus
                        </span>
                    </div>
                    <div class="flex flex-wrap items-center gap-3 mb-3 text-[11px] text-slate-300">
                        <span class="flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded-full inline-block" style="background:#64748b;"></span> No Reports Issued</span>
                        <span class="flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded-full inline-block" style="background:#1d4ed8;"></span> NBRI 1st Report Issued</span>
                        <span class="flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded-full inline-block" style="background:#38bdf8;"></span> NBRI 1st Report Issued + BOD Completed</span>
                        <span class="flex items-center gap-1.5"><span class="w-2.5 h-2.5 rounded-full inline-block" style="background:#eab308;"></span> NBRI 1st Report + BOD Completed + NBRI 2nd Report Issued</span>
                    </div>
                    <div class="w-full h-[450px] rounded-xl overflow-hidden relative border border-slate-800 shadow-2xl" id="map-container">
                        <div id="map" class="w-full h-full z-10"></div>
                    </div>
                </div>

                <!-- DISTRICT-WISE HOUSING UNIT DISTRIBUTION - HIGH QUALITY ATTRACTIVE COMBO CHART -->
                <div class="glass-panel rounded-2xl p-5">
                    <div class="flex items-center justify-between mb-4">
                        <div>
                            <h3 class="text-base font-bold text-white flex items-center gap-2">
                                <i class="fa-solid fa-chart-column text-cyan-400 text-sm"></i> District-wise Housing Unit & Site Distribution
                            </h3>
                            <p class="text-xs text-slate-400 mt-0.5">Live visualization of units and site density aggregated by district</p>
                        </div>
                        <span class="text-xs font-mono text-cyan-400 bg-cyan-500/10 border border-cyan-500/30 px-2.5 py-1 rounded-lg">
                            <i class="fa-solid fa-chart-line mr-1"></i> Interactive Chart
                        </span>
                    </div>
                    
                    <div class="relative h-[280px] w-full">
                        <canvas id="districtChart"></canvas>
                    </div>
                </div>

                <!-- MAIN SITE DETAILS TABLE -->
                <div class="glass-panel rounded-2xl p-5">
                    <div class="flex flex-wrap items-center justify-between gap-3 mb-4">
                        <h3 class="text-base font-bold text-white flex items-center gap-2">
                            <i class="fa-solid fa-table-cells text-purple-400 text-sm"></i> Resettlement Site Details Registry
                        </h3>
                        <div class="flex items-center gap-3">
                            <div class="relative w-56">
                                <i class="fa-solid fa-magnifying-glass absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-xs"></i>
                                <input type="text" id="registry-search" autocomplete="off" placeholder="Search site or location..." class="w-full bg-slate-900/90 text-xs text-slate-200 pl-8 pr-4 py-2 rounded-xl border border-slate-700 focus:border-purple-500 focus:outline-none placeholder-slate-500">
                                <div id="registry-search-results" class="hidden absolute z-30 top-full left-0 right-0 mt-1.5 bg-slate-900/98 border border-slate-700 rounded-xl shadow-2xl max-h-56 overflow-y-auto"></div>
                            </div>
                            <div class="text-xs text-slate-400 whitespace-nowrap" id="table-count">Showing 0 sites</div>
                        </div>
                    </div>
                    
                    <div class="max-h-[380px] overflow-y-auto pr-1 border border-slate-800/80 rounded-xl">
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
                
                <!-- SITE DISCUSSION / COMMENTS TAB -->
                <div class="glass-panel rounded-2xl p-5 border border-cyan-500/30 flex flex-col justify-between shadow-xl">
                    <div>
                        <div class="flex items-center justify-between mb-3">
                            <h3 class="text-sm font-bold text-white flex items-center gap-2">
                                <i class="fa-solid fa-comments text-cyan-400 text-sm"></i> Site Discussion
                            </h3>
                            <span id="discussion-site-tag" class="text-[10px] text-cyan-300 bg-cyan-500/20 px-2.5 py-1 rounded-lg border border-cyan-500/30 font-semibold">No Site Selected</span>
                        </div>
                        <div id="discussion-thread" class="bg-slate-950/80 p-4 rounded-xl border border-slate-800/80 text-xs space-y-3 h-[220px] overflow-y-auto">
                            <p class="text-slate-400 italic">Click on any site row in the table, or a map marker/district, to open its discussion thread and leave comments here.</p>
                        </div>
                    </div>
                    <div class="mt-3 flex items-center gap-2">
                        <input type="text" id="discussion-input" disabled onkeypress="if(event.key==='Enter') postDiscussionComment();" placeholder="Select a site to comment..." class="w-full bg-slate-900/95 text-xs text-slate-200 px-3 py-2.5 rounded-xl border border-slate-700/80 focus:border-cyan-500 focus:outline-none placeholder-slate-500 disabled:opacity-50">
                        <button id="discussion-send" onclick="postDiscussionComment()" disabled class="px-3.5 py-2.5 bg-cyan-600/40 hover:bg-cyan-600/60 disabled:opacity-40 disabled:cursor-not-allowed text-cyan-100 border border-cyan-500/40 rounded-xl text-xs font-semibold transition">
                            <i class="fa-solid fa-paper-plane"></i>
                        </button>
                    </div>
                </div>

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

                <!-- HSPTD AI ASSISTANT (placed directly below Conceptual Land Subdivision Layout) -->
                <div class="glass-panel-glow rounded-2xl p-6 flex flex-col shadow-2xl">
                    <div class="flex items-center justify-between mb-4">
                        <div class="flex items-center gap-3">
                            <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-purple-600 via-indigo-600 to-pink-500 flex items-center justify-center text-white text-sm shadow-lg shadow-purple-500/30">
                                <i class="fa-solid fa-wand-magic-sparkles animate-pulse"></i>
                            </div>
                            <div>
                                <h3 class="text-base font-bold text-white flex items-center gap-2">
                                    HSPTD AI Assistant
                                    <span class="text-[10px] bg-purple-500/20 text-purple-300 border border-purple-500/30 px-2 py-0.5 rounded-full font-medium">Smart Query Engine</span>
                                </h3>
                                <p class="text-xs text-purple-300">Ask any query regarding estate resettlement, report links, or district statistics</p>
                            </div>
                        </div>
                        <button onclick="clearAIChat()" class="text-xs text-slate-400 hover:text-slate-200 bg-slate-900/80 px-3 py-1.5 rounded-lg border border-slate-800 transition">
                            <i class="fa-solid fa-trash-can mr-1"></i> Clear Chat
                        </button>
                    </div>

                    <div id="ai-chat-box" class="h-[220px] overflow-y-auto space-y-3 p-4 bg-slate-950/90 rounded-xl border border-slate-800/90 text-xs mb-4 scroll-smooth">
                        <div class="flex gap-3">
                            <div class="w-7 h-7 rounded-full bg-purple-600 flex-shrink-0 flex items-center justify-center text-xs text-white font-bold shadow-md shadow-purple-500/20">AI</div>
                            <div class="bg-slate-900/90 text-slate-200 p-3 rounded-2xl border border-slate-800 max-w-[85%] leading-relaxed">
                                <strong>Ayubowan!</strong> Welcome to the HSPTD AI Assistant. Ask me anything about estate site locations, district breakdown, BOD clearances, or direct report links in the drive!
                            </div>
                        </div>
                    </div>

                    <div class="relative flex items-center">
                        <input type="text" id="ai-input" onkeypress="handleAIPress(event)" placeholder="Type your query..." class="w-full bg-slate-900/95 text-xs text-slate-200 pl-4 pr-12 py-3 rounded-xl border border-slate-700/80 focus:border-purple-500 focus:outline-none shadow-inner placeholder-slate-500">
                        <button onclick="sendAIMessage()" class="absolute right-3 text-purple-400 hover:text-purple-300 p-2 transition transform active:scale-95">
                            <i class="fa-solid fa-paper-plane text-sm"></i>
                        </button>
                    </div>
                </div>

            </div>
        </div>

    </main>

    <script>
        // Currently logged-in user, injected server-side, used to attribute discussion comments
        window.currentUser = { name: "{{CURRENT_USER}}" };

        // Live Google Sheets published CSV URL
        const DEFAULT_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRGEDtnF-wjT39hcvY3tkA_PpRO1FM06-M267dOBvKYGYlgD-udcevC8LrWGjM_XA/pub?gid=143716875&single=true&output=csv";

        // Locally uploaded district boundary GeoJSON, embedded server-side by app.py (falls back to remote if not present)
        const LOCAL_DISTRICT_GEOJSON = {{DISTRICT_GEOJSON}};

        // Fallback remote sources (used only if the local repo file isn't embedded)
        const SRI_LANKA_DISTRICTS_FALLBACK_URL = "https://raw.githubusercontent.com/wmgeolab/geoBoundaries/main/releaseData/gbOpen/LKA/ADM2/geoBoundaries-LKA-ADM2_simplified.geojson";
        const SRI_LANKA_COUNTRY_BORDER_URL = "https://raw.githubusercontent.com/wmgeolab/geoBoundaries/main/releaseData/gbOpen/LKA/ADM0/geoBoundaries-LKA-ADM0_simplified.geojson";

        let rawData = [];
        let filteredData = [];
        let registrySearchTerm = '';
        let mapInstance = null;
        let markersGroup = null;
        let districtGeoJsonLayer = null;
        let countryBorderLayer = null;
        let selectedDistrictName = 'ALL';
        
        let districtChartInstance = null;
        let subdivisionChartInstance = null;

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
            mapInstance = L.map('map', { zoomControl: true, attributionControl: false }).setView([7.8731, 80.7718], 7.5);
            
            // ESRI World Navigation Dark Blue Basemap
            L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}', {
                maxZoom: 18,
                attribution: 'Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ'
            }).addTo(mapInstance);

            markersGroup = L.layerGroup().addTo(mapInstance);

            // Overlay Sri Lanka administrative district boundaries (uploaded layer) + a permanently glowing country border
            fetchDistrictBoundaries();
            fetchCountryBorder();
        }

        function fetchDistrictBoundaries() {
            if (LOCAL_DISTRICT_GEOJSON) {
                districtGeoJsonLayer = L.geoJSON(LOCAL_DISTRICT_GEOJSON, {
                    style: styleDistrictFeature,
                    onEachFeature: onEachDistrictFeature
                }).addTo(mapInstance);
                return;
            }
            // Fallback to remote source if the uploaded local geojson wasn't found alongside app.py
            fetch(SRI_LANKA_DISTRICTS_FALLBACK_URL)
                .then(res => res.json())
                .then(geojsonData => {
                    districtGeoJsonLayer = L.geoJSON(geojsonData, {
                        style: styleDistrictFeature,
                        onEachFeature: onEachDistrictFeature
                    }).addTo(mapInstance);
                })
                .catch(err => console.log('District GeoJSON load error:', err));
        }

        function fetchCountryBorder() {
            fetch(SRI_LANKA_COUNTRY_BORDER_URL)
                .then(res => res.json())
                .then(geojsonData => {
                    countryBorderLayer = L.geoJSON(geojsonData, {
                        style: {
                            color: '#06b6d4',
                            weight: 2.5,
                            opacity: 0.9,
                            fillOpacity: 0,
                            className: 'country-border-glow'
                        },
                        interactive: false
                    }).addTo(mapInstance);
                })
                .catch(err => console.log('Country border load error:', err));
        }

        // Districts stay plain/unlit by default; only the district that is currently
        // selected (via dropdown, map click, or table row) gets the purple highlight glow.
        // The Sri Lanka national border (separate layer above) glows at all times.
        function styleDistrictFeature(feature) {
            const shapeName = (feature.properties.shapeName || feature.properties.NAME_2 || feature.properties.district || feature.properties.DISTRICT || feature.properties.name || '').toLowerCase();
            const selected = selectedDistrictName.toLowerCase();

            if (selected !== 'all' && shapeName && shapeName.includes(selected)) {
                return {
                    color: '#a855f7',
                    weight: 3,
                    opacity: 0.95,
                    fillColor: '#a855f7',
                    fillOpacity: 0.25,
                    className: 'district-boundary-active'
                };
            }

            return {
                color: '#3b4a63',
                weight: 1,
                opacity: 0.5,
                fillColor: '#3b4a63',
                fillOpacity: 0.02,
                className: ''
            };
        }

        function onEachDistrictFeature(feature, layer) {
            const dName = feature.properties.shapeName || feature.properties.NAME_2 || feature.properties.district || feature.properties.DISTRICT || feature.properties.name || 'District';
            layer.bindTooltip(`<b>${dName} District</b>`, { sticky: true, className: 'custom-tooltip' });
            
            layer.on({
                click: (e) => {
                    const distSelect = document.getElementById('filter-district');
                    for (let opt of distSelect.options) {
                        if (opt.value.toLowerCase() === dName.toLowerCase()) {
                            distSelect.value = opt.value;
                            applyFilters();
                            break;
                        }
                    }
                }
            });
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

        function parseUnitsValue(raw) {
            if (raw === undefined || raw === null) return 0;
            const cleaned = String(raw).replace(/[^0-9]/g, '');
            return parseInt(cleaned) || 0;
        }

        function processCSVRows(rows) {
            rawData = rows.map((r, idx) => {
                const region = r['Region'] || r['region'] || 'Rathnapura';
                const district = r['District'] || r['district'] || region;
                const estate = r['Estate'] || r['estate'] || `Site ${idx+1}`;
                const division = r['Division'] || r['division'] || '-';
                const ia = r["IA's"] || r["IA"] || 'SEC';
                const rpc = r['RPC'] || r["RPC's"] || r['rpc'] || '-';
                
                let rawUnits = r['Units (2529 List)'] || r['Units (2020 List)'] || r['Units'] || '0';
                if (typeof rawUnits === 'string') rawUnits = rawUnits.replace(/[^0-9]/g, '');
                const units = parseInt(rawUnits) || 0;

                const reportIssued = (r['NBRI 1st Report - Issued'] || r['NBRI 1st Report Issued'] || 'Yes').trim();
                const reportYear = r['NBRI 1st Report - Year '] || r['NBRI 1st Report - Year'] || '2026';
                const reportUnits = parseUnitsValue(r['NBRI 1st Report - Units'] || r['NBRI 1st Report Units']);
                const bodCompleted = (r['BOD Completed'] || 'No').trim();
                const bodMarkedUnits = parseUnitsValue(r['BOD Marked on Ground'] || r['BOD Marked On Ground'] || r['BOD Morked on Ground']);
                const perimeterSurvey = r['Perimeter Survey'] || 'Yes';
                const droneSurvey = r['Drone Survey'] || 'Completed';
                const conceptualDesign = (r['NBRI Conceptual Design'] || 'In Progress').trim();
                const conceptualUnits = parseUnitsValue(r['NBRI Conceptual Design - Units'] || r['NBRI Conceptual Design Units']);
                const report2Issued = (r['NBRI 2nd Report - Issued'] || r['NBRI 2nd Report Issued'] || 'No').trim();
                const report2Year = r['NBRI 2nd Report - Year '] || r['NBRI 2nd Report - Year'] || '';
                const report2Units = parseUnitsValue(r['NBRI 2nd Report - Units'] || r['NBRI 2nd Report Units']);
                
                // Directly capture raw link from spreadsheet cell (handles SharePoint / Drive / Web URLs)
                const reportLinkRaw = r['NBRI 1st Report - Link'] || r['Report Link'] || r['Link'] || '';
                const reportLink = formatReportURL(reportLinkRaw, estate);

                let baseCoords = districtCoordinates[district] || { lat: 6.68, lng: 80.39 };
                let lat = parseFloat(r['Lat'] || r['Latitude']) || (baseCoords.lat + (Math.random() - 0.5) * 0.12);
                let lng = parseFloat(r['Lon'] || r['Longitude']) || (baseCoords.lng + (Math.random() - 0.5) * 0.12);

                return { 
                    sno: idx + 1, region, district, estate, division, ia, rpc, units, 
                    reportIssued, reportYear, reportUnits, bodCompleted, bodMarkedUnits, perimeterSurvey, droneSurvey, 
                    conceptualDesign, conceptualUnits, report2Issued, report2Year, report2Units, reportLinkRaw, reportLink, lat, lng 
                };
            });

            populateFilterDropdowns();
            applyFilters();
        }

        function formatReportURL(rawLink, estateName) {
            if (!rawLink || rawLink.trim() === '' || rawLink.trim() === '-') return '';
            let cleaned = rawLink.trim();

            // Direct URL (SharePoint / Google Drive / NBRI Web) check
            if (cleaned.toLowerCase().startsWith('http://') || cleaned.toLowerCase().startsWith('https://')) {
                return cleaned;
            }
            if (cleaned.includes('sharepoint.com') || cleaned.includes('drive.google.com') || cleaned.includes('docs.google.com')) {
                return 'https://' + cleaned;
            }

            // Fallback for plain text site name reference
            return `https://www.google.com/search?q=NBRI+Report+${encodeURIComponent(cleaned)}+${encodeURIComponent(estateName)}`;
        }

        function populateFilterDropdowns() {
            const regionSelect = document.getElementById('filter-region');
            const districtSelect = document.getElementById('filter-district');
            const iaSelect = document.getElementById('filter-ia');
            const rpcSelect = document.getElementById('filter-rpc');

            const regions = [...new Set(rawData.map(d => d.region))].filter(Boolean);
            const districts = [...new Set(rawData.map(d => d.district))].filter(Boolean);
            const ias = [...new Set(rawData.map(d => d.ia))].filter(Boolean);
            const rpcs = [...new Set(rawData.map(d => d.rpc))].filter(Boolean);

            regionSelect.innerHTML = '<option value="ALL">Regions</option>' + regions.map(r => `<option value="${r}">${r}</option>`).join('');
            districtSelect.innerHTML = '<option value="ALL">Districts</option>' + districts.map(d => `<option value="${d}">${d}</option>`).join('');
            iaSelect.innerHTML = '<option value="ALL">IA</option>' + ias.map(i => `<option value="${i}">${i}</option>`).join('');
            rpcSelect.innerHTML = '<option value="ALL">RPC</option>' + rpcs.map(p => `<option value="${p}">${p}</option>`).join('');
        }

        function applyFilters() {
            const regionVal = document.getElementById('filter-region').value;
            const districtVal = document.getElementById('filter-district').value;
            const iaVal = document.getElementById('filter-ia').value;
            const rpcVal = document.getElementById('filter-rpc').value;
            selectedDistrictName = districtVal;
            const searchVal = document.getElementById('search-input').value.toLowerCase().trim();

            filteredData = rawData.filter(item => {
                const matchRegion = (regionVal === 'ALL' || item.region === regionVal);
                const matchDistrict = (districtVal === 'ALL' || item.district === districtVal);
                const matchIA = (iaVal === 'ALL' || item.ia === iaVal);
                const matchRPC = (rpcVal === 'ALL' || item.rpc === rpcVal);
                const matchSearch = !searchVal || item.estate.toLowerCase().includes(searchVal) || item.division.toLowerCase().includes(searchVal);
                return matchRegion && matchDistrict && matchIA && matchRPC && matchSearch;
            });

            updateKPIs();
            updateMapMarkers(districtVal);
            if (districtGeoJsonLayer) {
                districtGeoJsonLayer.setStyle(styleDistrictFeature);
            }
            updateDistrictChart();
            updateCharts();
            renderMainTable();
        }

        function updateKPIs() {
            const totalSites = filteredData.length;
            const totalUnits = filteredData.reduce((acc, curr) => acc + curr.units, 0);
            const reportIssuedCount = filteredData.filter(d => d.reportIssued.toLowerCase() === 'yes').length;
            const bodCompletedCount = filteredData.filter(d => d.bodCompleted.toLowerCase() === 'yes').length;
            const conceptualIssuedCount = filteredData.filter(d => (d.conceptualDesign || '').toLowerCase().includes('completed')).length;
            const report2IssuedCount = filteredData.filter(d => d.report2Issued.toLowerCase() === 'yes').length;

            const reportPct = totalSites > 0 ? Math.round((reportIssuedCount / totalSites) * 100) : 0;
            const bodPct = totalSites > 0 ? Math.round((bodCompletedCount / totalSites) * 100) : 0;
            const conceptualPct = totalSites > 0 ? Math.round((conceptualIssuedCount / totalSites) * 100) : 0;
            const report2Pct = totalSites > 0 ? Math.round((report2IssuedCount / totalSites) * 100) : 0;

            document.getElementById('kpi-total-sites').textContent = totalSites;
            document.getElementById('kpi-total-units').textContent = totalUnits.toLocaleString();
            document.getElementById('kpi-report-issued').textContent = reportIssuedCount;
            document.getElementById('kpi-report-pct').textContent = `${reportPct}%`;
            document.getElementById('kpi-report-bar').style.width = `${reportPct}%`;
            document.getElementById('kpi-bod-completed').textContent = bodCompletedCount;
            document.getElementById('kpi-bod-pct').textContent = `${bodPct}%`;
            document.getElementById('kpi-conceptual-issued').textContent = conceptualIssuedCount;
            document.getElementById('kpi-conceptual-pct').textContent = `${conceptualPct}%`;
            document.getElementById('kpi-report2-issued').textContent = report2IssuedCount;
            document.getElementById('kpi-report2-pct').textContent = `${report2Pct}%`;
            document.getElementById('kpi-report2-bar').style.width = `${report2Pct}%`;

            // Unit-level detail drawn from the corresponding "- Units" / ground-marking columns
            const reportUnitsSum = filteredData.reduce((acc, curr) => acc + (curr.reportUnits || 0), 0);
            const conceptualUnitsSum = filteredData.reduce((acc, curr) => acc + (curr.conceptualUnits || 0), 0);
            const bodMarkedUnitsSum = filteredData.reduce((acc, curr) => acc + (curr.bodMarkedUnits || 0), 0);
            const report2UnitsSum = filteredData.reduce((acc, curr) => acc + (curr.report2Units || 0), 0);

            document.getElementById('kpi-report-units').textContent = `NBRI 1st Report - Units: ${reportUnitsSum.toLocaleString()}`;
            document.getElementById('kpi-conceptual-units').textContent = `NBRI Conceptual Design - Units: ${conceptualUnitsSum.toLocaleString()}`;
            document.getElementById('kpi-bod-units').textContent = `BOD Marked on Ground: ${bodMarkedUnitsSum.toLocaleString()}`;
            document.getElementById('kpi-report2-units').textContent = `NBRI 2nd Report - Units: ${report2UnitsSum.toLocaleString()}`;
        }

        function updateMapMarkers(selectedDistrict) {
            markersGroup.clearLayers();
            const districtTag = document.getElementById('district-tag');

            if (selectedDistrict !== 'ALL' && districtCoordinates[selectedDistrict]) {
                const coords = districtCoordinates[selectedDistrict];
                districtTag.classList.remove('hidden');
                if (mapInstance) mapInstance.flyTo([coords.lat, coords.lng], 10, { duration: 1.2 });
            } else {
                districtTag.classList.add('hidden');
            }

            if (filteredData.length === 0) return;
            const bounds = [];

            filteredData.forEach(site => {
                const isReport1 = site.reportIssued.toLowerCase() === 'yes';
                const isBod = site.bodCompleted.toLowerCase() === 'yes';
                const isReport2 = site.report2Issued.toLowerCase() === 'yes';

                let pinClass = '';
                if (isReport1 && isBod && isReport2) {
                    pinClass = 'stage-3';
                } else if (isReport1 && isBod) {
                    pinClass = 'stage-2';
                } else if (isReport1) {
                    pinClass = 'stage-1';
                }
                // else: no stage class -> default neutral/grey pin (no reports issued)

                const customIcon = L.divIcon({
                    className: 'custom-pin-wrapper',
                    html: `<span class="glowing-pin ${pinClass}"></span>`,
                    iconSize: [14, 14],
                    iconAnchor: [7, 7]
                });

                const marker = L.marker([site.lat, site.lng], { icon: customIcon });
                
                let linkButton = site.reportLink 
                    ? `<a href="${site.reportLink}" target="_blank" rel="noopener noreferrer" class="inline-block mt-2 px-3 py-1.5 bg-cyan-500/30 text-cyan-200 border border-cyan-400/40 rounded-lg text-xs font-semibold hover:bg-cyan-500/50 transition"><i class="fa-solid fa-file-pdf mr-1"></i> Open Official Report Link</a>`
                    : '<span class="text-[10px] text-slate-400 mt-1 block">No direct report link attached</span>';

                marker.bindPopup(`
                    <div style="font-family:'Plus Jakarta Sans', sans-serif; padding:4px;">
                        <h4 style="font-weight:700; color:#38bdf8; font-size:14px; margin-bottom:6px;">${site.estate}</h4>
                        <p style="font-size:11px; color:#cbd5e1; margin:2px 0;"><b>1. Division:</b> ${site.division}</p>
                        <p style="font-size:11px; color:#cbd5e1; margin:2px 0;"><b>2. District:</b> ${site.district}</p>
                        <p style="font-size:11px; color:#cbd5e1; margin:2px 0;"><b>3. Region:</b> ${site.region}</p>
                        <p style="font-size:11px; color:#cbd5e1; margin:2px 0;"><b>4. IA / RPC:</b> <span style="color:#a855f7; font-weight:700;">${site.ia}</span> / ${site.rpc}</p>
                        <p style="font-size:11px; color:#cbd5e1; margin:2px 0;"><b>5. Planned Units:</b> <span style="color:#34d399; font-weight:700;">${site.units} Units</span></p>
                        <p style="font-size:11px; color:#cbd5e1; margin:2px 0;"><b>6. NBRI 1st Report:</b> ${site.reportIssued} (${site.reportYear})</p>
                        <p style="font-size:11px; color:#cbd5e1; margin:2px 0;"><b>7. BOD Clearance:</b> ${site.bodCompleted}</p>
                        <p style="font-size:11px; color:#cbd5e1; margin:2px 0;"><b>8. Perimeter Survey:</b> ${site.perimeterSurvey}</p>
                        <p style="font-size:11px; color:#cbd5e1; margin:2px 0;"><b>9. Drone Survey:</b> ${site.droneSurvey}</p>
                        <p style="font-size:11px; color:#cbd5e1; margin:2px 0;"><b>10. Conceptual Design:</b> ${site.conceptualDesign}</p>
                        <p style="font-size:11px; color:#cbd5e1; margin:2px 0;"><b>11. NBRI 2nd Report:</b> ${site.report2Issued}${site.report2Year ? ' (' + site.report2Year + ')' : ''}</p>
                        ${linkButton}
                    </div>
                `);

                marker.on('click', () => selectSiteRow(site));
                markersGroup.addLayer(marker);
                bounds.push([site.lat, site.lng]);
            });

            if (selectedDistrict === 'ALL' && bounds.length > 0) {
                mapInstance.fitBounds(bounds, { padding: [30, 30], maxZoom: 11 });
            }
        }

        function initCharts() {
            // 1. District-wise Housing Units Combo Chart
            const ctxDist = document.getElementById('districtChart').getContext('2d');
            districtChartInstance = new Chart(ctxDist, {
                type: 'bar',
                data: {
                    labels: [],
                    datasets: [
                        {
                            label: 'Housing Units',
                            type: 'bar',
                            data: [],
                            backgroundColor: 'rgba(6, 182, 212, 0.65)',
                            borderColor: '#06b6d4',
                            borderWidth: 1.5,
                            borderRadius: 6,
                            yAxisID: 'y'
                        },
                        {
                            label: 'Number of Sites',
                            type: 'line',
                            data: [],
                            borderColor: '#a855f7',
                            backgroundColor: '#a855f7',
                            borderWidth: 2.5,
                            pointRadius: 4,
                            pointHoverRadius: 7,
                            tension: 0.3,
                            yAxisID: 'y1'
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            labels: { color: '#cbd5e1', font: { size: 11, family: 'Plus Jakarta Sans' } }
                        },
                        tooltip: {
                            mode: 'index',
                            intersect: false,
                            backgroundColor: 'rgba(15, 23, 42, 0.95)',
                            borderColor: '#3b82f6',
                            borderWidth: 1
                        }
                    },
                    scales: {
                        x: {
                            ticks: { color: '#94a3b8', font: { size: 10 } },
                            grid: { color: 'rgba(255, 255, 255, 0.05)' }
                        },
                        y: {
                            type: 'linear',
                            display: true,
                            position: 'left',
                            ticks: { color: '#06b6d4' },
                            grid: { color: 'rgba(255, 255, 255, 0.05)' },
                            title: { display: true, text: 'Housing Units', color: '#06b6d4', font: { size: 10 } }
                        },
                        y1: {
                            type: 'linear',
                            display: true,
                            position: 'right',
                            ticks: { color: '#a855f7' },
                            grid: { drawOnChartArea: false },
                            title: { display: true, text: 'No. of Sites', color: '#a855f7', font: { size: 10 } }
                        }
                    }
                }
            });

            // 2. Conceptual Subdivision Doughnut Chart
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
        }

        function updateDistrictChart() {
            const districtMap = {};
            filteredData.forEach(item => {
                const dist = item.district || 'Unassigned';
                if (!districtMap[dist]) districtMap[dist] = { sites: 0, units: 0 };
                districtMap[dist].sites += 1;
                districtMap[dist].units += item.units;
            });

            const sortedDistricts = Object.keys(districtMap)
                .map(d => ({ district: d, ...districtMap[d] }))
                .sort((a, b) => b.units - a.units);

            districtChartInstance.data.labels = sortedDistricts.map(d => d.district);
            districtChartInstance.data.datasets[0].data = sortedDistricts.map(d => d.units);
            districtChartInstance.data.datasets[1].data = sortedDistricts.map(d => d.sites);
            districtChartInstance.update();
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
            const registryRows = getRegistryMatches();
            document.getElementById('table-count').textContent = registrySearchTerm
                ? `Showing ${registryRows.length} of ${filteredData.length} sites`
                : `Showing ${filteredData.length} sites`;

            registryRows.forEach(row => {
                const tr = document.createElement('tr');
                tr.className = 'hover:bg-slate-800/60 border-b border-slate-800/40 cursor-pointer transition';
                
                tr.onclick = () => selectSiteRow(row);

                let reportLinkHTML = row.reportLink 
                    ? `<a href="${row.reportLink}" target="_blank" rel="noopener noreferrer" onclick="event.stopPropagation();" class="inline-flex items-center gap-1 px-2.5 py-1 rounded-md bg-cyan-500/20 text-cyan-300 hover:bg-cyan-500/40 border border-cyan-500/30 text-[11px] font-semibold transition"><i class="fa-solid fa-file-pdf"></i> View Link</a>`
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

        let currentSelectedSite = null;
        const DISCUSSION_STORAGE_KEY = 'ihp4700_site_discussions';

        function loadDiscussionStore() {
            try {
                return JSON.parse(localStorage.getItem(DISCUSSION_STORAGE_KEY)) || {};
            } catch (e) {
                return {};
            }
        }

        function saveDiscussionStore(store) {
            try {
                localStorage.setItem(DISCUSSION_STORAGE_KEY, JSON.stringify(store));
            } catch (e) { /* storage unavailable, ignore */ }
        }

        function siteDiscussionKey(site) {
            return `${site.district}__${site.estate}__${site.sno}`;
        }

        function selectSiteRow(site) {
            if (mapInstance && site.lat && site.lng) {
                mapInstance.setView([site.lat, site.lng], 13);
            }

            // Update Selected District Glow on Map
            if (site.district) {
                selectedDistrictName = site.district;
                if (districtGeoJsonLayer) districtGeoJsonLayer.setStyle(styleDistrictFeature);
            }

            currentSelectedSite = site;
            document.getElementById('discussion-site-tag').textContent = `${site.estate} (Site #${site.sno})`;
            document.getElementById('discussion-input').disabled = false;
            document.getElementById('discussion-input').placeholder = 'Add a comment about this site...';
            document.getElementById('discussion-send').disabled = false;

            renderDiscussionThread();
        }

        function renderDiscussionThread() {
            const thread = document.getElementById('discussion-thread');
            if (!currentSelectedSite) {
                thread.innerHTML = `<p class="text-slate-400 italic">Click on any site row in the table, or a map marker/district, to open its discussion thread and leave comments here.</p>`;
                return;
            }
            const store = loadDiscussionStore();
            const key = siteDiscussionKey(currentSelectedSite);
            const comments = store[key] || [];

            if (comments.length === 0) {
                thread.innerHTML = `<p class="text-slate-400 italic">No comments yet for <strong class="text-cyan-300">${currentSelectedSite.estate}</strong>. Be the first to add a note or observation about this site.</p>`;
                return;
            }

            thread.innerHTML = comments.map(c => `
                <div class="flex gap-2.5">
                    <div class="w-6 h-6 rounded-full bg-cyan-600/70 flex-shrink-0 flex items-center justify-center text-[10px] text-white font-bold">${(c.author || 'U').charAt(0).toUpperCase()}</div>
                    <div class="bg-slate-900/90 text-slate-200 p-2.5 rounded-xl border border-slate-800 flex-1">
                        <div class="flex items-center justify-between mb-0.5">
                            <span class="text-[11px] font-semibold text-cyan-300">${c.author || 'User'}</span>
                            <span class="text-[9px] text-slate-500">${c.time || ''}</span>
                        </div>
                        <p class="text-[11px] leading-relaxed">${c.text}</p>
                    </div>
                </div>
            `).join('');
            thread.scrollTop = thread.scrollHeight;
        }

        function postDiscussionComment() {
            if (!currentSelectedSite) return;
            const input = document.getElementById('discussion-input');
            const text = input.value.trim();
            if (!text) return;

            const store = loadDiscussionStore();
            const key = siteDiscussionKey(currentSelectedSite);
            if (!store[key]) store[key] = [];

            const authorName = (window.currentUser && window.currentUser.name) ? window.currentUser.name : 'You';
            store[key].push({
                author: authorName,
                text: text,
                time: new Date().toLocaleString()
            });
            saveDiscussionStore(store);
            input.value = '';
            renderDiscussionThread();
        }

        function setupEventListeners() {
            document.getElementById('filter-region').addEventListener('change', applyFilters);
            document.getElementById('filter-district').addEventListener('change', applyFilters);
            document.getElementById('filter-ia').addEventListener('change', applyFilters);
            document.getElementById('filter-rpc').addEventListener('change', applyFilters);
            document.getElementById('search-input').addEventListener('input', applyFilters);

            const registrySearchInput = document.getElementById('registry-search');
            registrySearchInput.addEventListener('input', handleRegistrySearchInput);
            registrySearchInput.addEventListener('focus', renderRegistrySearchSuggestions);
            document.addEventListener('click', (e) => {
                const box = document.getElementById('registry-search-results');
                if (box && !box.contains(e.target) && e.target !== registrySearchInput) {
                    box.classList.add('hidden');
                }
            });
        }

        // Local search scoped to the Resettlement Site Details Registry table only.
        // Lets the user find and select a specific site/location without touching the
        // global region/district/IA/RPC filters above the map.
        function handleRegistrySearchInput() {
            registrySearchTerm = document.getElementById('registry-search').value.toLowerCase().trim();
            renderMainTable();
            renderRegistrySearchSuggestions();
        }

        function getRegistryMatches() {
            if (!registrySearchTerm) return filteredData;
            return filteredData.filter(item =>
                (item.estate || '').toLowerCase().includes(registrySearchTerm) ||
                (item.division || '').toLowerCase().includes(registrySearchTerm) ||
                (item.district || '').toLowerCase().includes(registrySearchTerm) ||
                (item.region || '').toLowerCase().includes(registrySearchTerm)
            );
        }

        function renderRegistrySearchSuggestions() {
            const box = document.getElementById('registry-search-results');
            if (!box) return;
            if (!registrySearchTerm) { box.classList.add('hidden'); box.innerHTML = ''; return; }

            const matches = getRegistryMatches().slice(0, 8);
            if (matches.length === 0) {
                box.innerHTML = `<div class="px-3 py-2.5 text-[11px] text-slate-500 italic">No matching site or location found</div>`;
                box.classList.remove('hidden');
                return;
            }

            box.innerHTML = matches.map(site => `
                <div class="px-3 py-2 text-[11px] text-slate-200 hover:bg-purple-500/20 cursor-pointer border-b border-slate-800/60 last:border-b-0" data-sno="${site.sno}">
                    <span class="font-semibold text-cyan-300">${site.estate}</span>
                    <span class="text-slate-400"> — ${site.division}, ${site.district}</span>
                </div>
            `).join('');
            box.classList.remove('hidden');

            box.querySelectorAll('[data-sno]').forEach(el => {
                el.addEventListener('click', () => {
                    const sno = parseInt(el.getAttribute('data-sno'));
                    const site = filteredData.find(s => s.sno === sno);
                    if (site) {
                        selectSiteRow(site);
                        document.getElementById('registry-search').value = site.estate;
                        registrySearchTerm = site.estate.toLowerCase();
                        renderMainTable();
                    }
                    box.classList.add('hidden');
                });
            });
        }

        function handleAIPress(e) { if (e.key === 'Enter') sendAIMessage(); }
        function sendAIMessage() {
            const input = document.getElementById('ai-input');
            const msg = input.value.trim();
            if (!msg) return;

            const chatBox = document.getElementById('ai-chat-box');
            chatBox.innerHTML += `
                <div class="flex justify-end mb-2">
                    <div class="bg-purple-600/80 text-white p-2.5 rounded-2xl max-w-[80%] shadow-md">
                        ${msg}
                    </div>
                </div>
            `;
            input.value = '';

            setTimeout(() => {
                let aiReply = `Analyzed live dashboard database for <strong>"${msg}"</strong>: currently filtering <strong>${filteredData.length} sites</strong>.`;
                
                // Smart auto responses based on query keywords
                const lowerMsg = msg.toLowerCase();
                if (lowerMsg.includes('report') || lowerMsg.includes('link') || lowerMsg.includes('drive')) {
                    aiReply = `All Google Drive / SharePoint report links are directly synchronized from the sheet under column 'NBRI 1st Report - Link'. Click any site row or map marker to launch the direct PDF report!`;
                } else if (lowerMsg.includes('highest') || lowerMsg.includes('max') || lowerMsg.includes('district')) {
                    aiReply = `Check out the new District-wise Housing Unit Chart above! It highlights districts with the highest concentration of housing units and active estate sites.`;
                }

                chatBox.innerHTML += `
                    <div class="flex gap-3 mb-2">
                        <div class="w-7 h-7 rounded-full bg-purple-600 flex-shrink-0 flex items-center justify-center text-xs text-white font-bold">AI</div>
                        <div class="bg-slate-900/95 text-slate-200 p-3 rounded-2xl border border-slate-800/80 max-w-[85%] leading-relaxed">
                            ${aiReply}
                        </div>
                    </div>
                `;
                chatBox.scrollTop = chatBox.scrollHeight;
            }, 300);
        }

        function clearAIChat() {
            const chatBox = document.getElementById('ai-chat-box');
            chatBox.innerHTML = `
                <div class="flex gap-3">
                    <div class="w-7 h-7 rounded-full bg-purple-600 flex-shrink-0 flex items-center justify-center text-xs text-white font-bold">AI</div>
                    <div class="bg-slate-900/90 text-slate-200 p-3 rounded-2xl border border-slate-800 max-w-[85%] leading-relaxed">
                        Chat cleared! How can I assist you with the resettlement dataset?
                    </div>
                </div>
            `;
        }
    </script>
</body>
</html>
"""

# ==========================================
# 4. STREAMLIT RENDER
# ==========================================
unread_count = sum(1 for n in st.session_state.notifications if not n["read"])
bell_label = f"🔔 Notifications ({unread_count})" if unread_count > 0 else "🔔 Notifications"

top_left, bell_col, logout_col = st.columns([6, 1.4, 1])
with bell_col:
    if st.button(bell_label, use_container_width=True):
        check_for_sheet_updates(silent_baseline=False)
        st.session_state.show_notifications = not st.session_state.show_notifications
        for n in st.session_state.notifications:
            n["read"] = True
        st.rerun()
with logout_col:
    if st.button("Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.current_user = ""
        st.rerun()

if st.session_state.show_notifications:
    with st.container(border=True):
        header_col, clear_col = st.columns([5, 1])
        with header_col:
            st.markdown("**Recent Sheet Activity**")
        with clear_col:
            if st.button("Clear all", key="clear_notifs"):
                st.session_state.notifications = []
                st.rerun()

        if not st.session_state.notifications:
            st.caption("No updates yet. New sheet changes (report status, BOD clearance, conceptual plan, new sites) will show up here.")
        else:
            for n in st.session_state.notifications[:20]:
                st.markdown(f"- {n['text']}  \n  <span style='color:#94a3b8; font-size:0.75rem;'>{n['time']}</span>", unsafe_allow_html=True)

html_dashboard = (
    html_template
    .replace("{{LOGO_URL}}", LOGO_URL)
    .replace("{{DISTRICT_GEOJSON}}", DISTRICT_GEOJSON_JS)
    .replace("{{CURRENT_USER}}", st.session_state.current_user or "User")
)
components.html(html_dashboard, height=1550, scrolling=True)
