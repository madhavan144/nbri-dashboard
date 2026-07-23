import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk

# Page Configuration (NRIS Dark / Modern Theme)
st.set_page_config(
    page_title="NBRI Housing Resettlement Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 1. Live Google Sheet Data Loading
@st.cache_data(ttl=300)  # 5 நிமிடத்திற்கு ஒருமுறை தானாக புதுப்பிக்கும்
def load_data():
    # Publish to web செய்த CSV Link-ஐ இங்கு மாற்றவும்
    csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRGEDtnF-wjT39hcvY3tkA_PpRO1FM06-M267dOBvKYGYlgD-udcevC8LrWGjM_XA/pub?gid=143716875&single=true&output=csv"
    df = pd.read_csv(csv_url)
    return df

df = load_data()

# Header Section
st.title("🏛️ NBRI Progress & Housing Resettlement Dashboard")
st.markdown("---")

# 2. Sidebar Filters (NRIS Style Dropdowns)
st.sidebar.header("🔍 Filter Options")
region_filter = st.sidebar.multiselect("Select Region", options=df["Region"].unique(), default=df["Region"].unique())
district_filter = st.sidebar.multiselect("Select District", options=df["District"].unique(), default=df["District"].unique())

filtered_df = df[(df["Region"].isin(region_filter)) & (df["District"].isin(district_filter))]

# 3. Top KPI Cards (NRIS Style Metrics)
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Sites", len(filtered_df))
col2.metric("Total Units", int(filtered_df["Units (2529 List)"].sum()))
col3.metric("NBRI 1st Report Issued", len(filtered_df[filtered_df["NBRI 1st Report - Issued"] == "Yes"]))
col4.metric("BOD Completed", len(filtered_df[filtered_df["BOD Completed"] == "Yes"]))

st.markdown("---")

# 4. Interactive Map (NRIS Style Map)
st.subheader("📍 Interactive Site Location Map")
map_data = filtered_df.dropna(subset=["Lat", "Lon"])

if not map_data.empty:
    st.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/dark-v10",
        initial_view_state=pdk.ViewState(
            latitude=map_data["Lat"].mean(),
            longitude=map_data["Lon"].mean(),
            zoom=8,
            pitch=30,
        ),
        layers=[
            pdk.Layer(
                'ScatterplotLayer',
                data=map_data,
                get_position='[Lon, Lat]',
                get_color='[255, 75, 75, 200]',
                get_radius=800,
                pickable=True
            ),
        ],
        tooltip={"text": "Estate: {Estate}\nDistrict: {District}\nUnits: {Units (2529 List)}"}
    ))

# 5. Charts Section (Donut & Bar Charts)
st.markdown("---")
c1, c2 = st.columns(2)

with c1:
    st.subheader("📊 Region-wise Unit Distribution")
    fig_bar = px.bar(
        filtered_df, 
        x="Region", 
        y="Units (2529 List)", 
        color="District", 
        barmode="group",
        template="plotly_dark"
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with c2:
    st.subheader("🥧 NBRI Report Status")
    fig_pie = px.pie(
        filtered_df, 
        names="NBRI 1st Report - Issued", 
        title="1st Report Issued vs Pending",
        hole=0.4,
        template="plotly_dark"
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# 6. Detailed Data Table
st.markdown("---")
st.subheader("📋 Site Details Table")
st.dataframe(filtered_df[['S.No. ', 'Region', 'District', 'Estate', 'Division', 'Units (2529 List)', 'NBRI 1st Report - Issued', 'BOD Completed']], use_container_width=True)