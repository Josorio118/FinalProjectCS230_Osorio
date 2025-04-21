"""
Name:       Your Name
CS230:      Section XXX
Data:       New England Airports (from ourairports.com)
URL:

Description:
This program is an interactive data explorer for New England airports. It lets users filter by state, airport type,
and elevation, and view visualizations such as a pie chart, bar chart, and interactive map using Streamlit.
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pydeck as pdk

# [DA1] Load and clean data
# [PY3] Error checking with try/except

def load_data():
    try:
        df = pd.read_csv("airports.csv")
        states = ['US-MA', 'US-CT', 'US-RI', 'US-NH', 'US-VT', 'US-ME']
        df = df[df['iso_region'].isin(states)].copy()
        df.dropna(subset=['latitude_deg', 'longitude_deg', 'elevation_ft'], inplace=True)
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

# [PY1] Function with default parameter
def filter_data(df, states, types, min_elev=0):
    return df[(df['iso_region'].isin(states)) &
              (df['type'].isin(types)) &
              (df['elevation_ft'] >= min_elev)]

# [PY2] Return multiple values
def count_by_state(df):
    counts = df['iso_region'].value_counts()
    return counts.index.tolist(), counts.values.tolist()

# [VIZ1] Pie chart
def generate_pie_chart(labels, sizes):
    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')
    return fig

# [VIZ2] Bar chart for top elevations
def generate_bar_chart(df):
    top_df = df.sort_values(by='elevation_ft', ascending=False).head(10)
    fig, ax = plt.subplots()
    ax.bar(top_df['name'], top_df['elevation_ft'], color='skyblue')
    ax.set_xlabel("Airport")
    ax.set_ylabel("Elevation (ft)")
    ax.set_title("Top 10 Highest Elevation Airports")
    plt.xticks(rotation=45, ha='right')
    return fig

# [MAP] Generate interactive map
# [PY5] Dictionary access in tooltip, [PY4] numpy.mean

def generate_map(df):
    view_state = pdk.ViewState(
        latitude=np.mean(df['latitude_deg']),
        longitude=np.mean(df['longitude_deg']),
        zoom=6,
        pitch=0)

    layer = pdk.Layer(
        'ScatterplotLayer',
        data=df,
        get_position='[longitude_deg, latitude_deg]',
        get_radius=1000,
        get_color='[0, 100, 255, 160]',
        pickable=True)

    tooltip = {"html": "<b>{name}</b><br />{municipality}",
               "style": {"backgroundColor": "steelblue", "color": "white"}}

    return pdk.Deck(map_style='mapbox://styles/mapbox/light-v9',
                    initial_view_state=view_state,
                    layers=[layer],
                    tooltip=tooltip)

# Streamlit UI
st.set_page_config(page_title="New England Airports Explorer", layout="wide")
st.title("🛬 New England Airports Explorer")
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

# Filter data
filtered = filter_data(data, states, types, min_elev)

if not filtered.empty:
    st.subheader("Airport Locations")
    st.pydeck_chart(generate_map(filtered))

    st.subheader("Airports Per State")
    labels, sizes = count_by_state(filtered)
    st.pyplot(generate_pie_chart(labels, sizes))

    st.subheader("Top Elevation Airports")
    st.pyplot(generate_bar_chart(filtered))
else:
    st.warning("No airports match the selected criteria.")
