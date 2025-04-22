"""
Name:       Julian Osorio
CS230:      Section 6
Data:       New England Airports
URL: https://ourairports.com/data/

Description:
This program is an interactive data explorer for New England airports. It lets users filter by state, airport type,
and elevation, and view visualizations such as a pie chart, bar chart, and interactive map using Streamlit. You can also filter whether the Airport has scheduled service or not. 
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pydeck as pdk


# Load and clean data to show only New England Airports
# [PY3] Error checking

def load_data():
    try:
        df = pd.read_csv("airports.csv")
        df.columns = df.columns.str.strip()
        states = ['US-MA', 'US-CT', 'US-RI', 'US-NH', 'US-VT', 'US-ME']
        df = df[df['iso_region'].isin(states)].copy()
        df.dropna(subset=['latitude_deg', 'longitude_deg', 'elevation_ft'], inplace=True)
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

# Default parameter
def filter_data(df, states, types, min_elev=0):
    return df[(df['iso_region'].isin(states)) &
              (df['type'].isin(types)) &
              (df['elevation_ft'] >= min_elev)]

# Return states
def count_by_state(df):
    counts = df['iso_region'].value_counts()
    return counts.index.tolist(), counts.values.tolist()

# Pie chart
def generate_pie_chart(labels, sizes):
    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')
    return fig

# Bar chart for top elevations
def generate_bar_chart(df):
    top_df = df.sort_values(by='elevation_ft', ascending=False).head(20)
    fig, ax = plt.subplots()
    ax.bar(top_df['name'], top_df['elevation_ft'], color='red')
    ax.set_xlabel("Airport")
    ax.set_ylabel("Elevation (ft)")
    ax.set_title("Top 10 Highest Elevation Airports")
    plt.xticks(rotation=45, ha='right')
    return fig

# MAP
# Dictionary/tooltip

# assign color based on airport type
def assign_colors(types):
    return [
        [0, 200, 0, 160] if t == 'small_airport' else
        [255, 165, 0, 160] if t == 'medium_airport' else
        [200, 0, 0, 160] if t == 'large_airport' else
        [100, 100, 255, 160] if t == 'heliport' else
        [175, 50, 255, 100] if t == 'seaplane_base' else
        [100,200,200,0] if t == 'balloonport' else
        [150, 150, 150, 160] #default gray(closed airports)
        for t in types
    ]

def generate_map(df):
    df = df.copy()
    df['color'] = assign_colors(df['type'])

    view_state = pdk.ViewState(
        latitude=np.mean(df['latitude_deg']),
        longitude=np.mean(df['longitude_deg']),
        zoom=8,
        pitch=0)

    layer = pdk.Layer(
        'ScatterplotLayer',
        data=df,
        get_position='[longitude_deg, latitude_deg]',
        get_color='color',  # Now pulling from DataFrame column
        get_radius=1000,
        pickable=True)

    tooltip = {"html": "<b>{name}</b><br />{type}<br />{municipality}",
               "style": {"backgroundColor": "steelblue", "color": "white"}}

    return pdk.Deck(
        map_style='mapbox://styles/mapbox/light-v9',
        initial_view_state=view_state,
        layers=[layer],
        tooltip=tooltip)

# Streamlit UI
st.set_page_config(page_title="New England Airports Discovery", layout="wide")
st.title(" New England Airports Discovery")
st.markdown("Use the sidebar to filter and explore airport data.")

# [ST4] Sidebar layout
st.sidebar.header("Filter Options")
data = load_data()

# [ST1] State multiselect
states = st.sidebar.multiselect("Select State(s)", options=sorted(data['iso_region'].unique()), default=['US-MA'])

# [ST2] Type multiselect
types = st.sidebar.multiselect("Select Airport Type(s)", options=data['type'].unique(), default=['small_airport'])

# [ST3] Elevation slider
min_elev = st.sidebar.slider("Minimum Elevation (ft)", min_value=0, max_value=5000, value=0)

scheduled_only = st.sidebar.checkbox("Only show airports with scheduled service")
if scheduled_only:
    data = data[data['scheduled_service'] == 'yes']

# Filter data
filtered = filter_data(data, states, types, min_elev)

if not filtered.empty:
    st.subheader("Airport Locations")
    st.pydeck_chart(generate_map(filtered))

    st.subheader("Airports Per State")
    labels, sizes = count_by_state(filtered)
    st.pyplot(generate_pie_chart(labels, sizes))

    st.subheader("Top Highest Elevation Airports")
    st.pyplot(generate_bar_chart(filtered))
else:
    st.warning("No airports match the selected criteria.")
