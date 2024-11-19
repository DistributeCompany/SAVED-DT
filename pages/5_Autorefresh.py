import datetime
import numpy as np
import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium
import random 

st.set_page_config(
    page_title="Folium Live Map",
    page_icon=":world_map:️",
    layout="wide",
)
st.markdown("# Folium Live Update Demo")
st.sidebar.header("Folium Demo")
st.write(
    """This demo illustrates a combination of plotting and animation with
Streamlit. We're generating a bunch of random markers in a loop for around
5 seconds. Enjoy!"""
)

if st.button("Reset streaming") or "markers" not in st.session_state:
    st.session_state["markers"] = []

left, right = st.columns(2)

@st.experimental_fragment(run_every=1)
def generate_chart():
    random_lat = 52.2435423371021 + random.uniform(0.001, 0.01)
    random_lon = 6.851863861083985 + random.uniform(0.001, 0.01)
    random_marker = folium.CircleMarker(
        location=[random_lat, random_lon],
        popup=f"Random marker at {random_lat:.6f}, {random_lon:.6f}",
    )
    st.session_state["markers"].append(random_marker)

    m = folium.Map(location=st.session_state["center"], zoom_start=st.session_state["zoom"])
    fg = folium.FeatureGroup(name="Markers")
    for marker in st.session_state["markers"]:
        fg.add_child(marker)

    st_data = st_folium(
        m,
        center=st.session_state["center"],
        zoom=15,
        key="new",
        feature_group_to_add=fg,
        height=400,
        width=700,
    )      
    st.caption(f"Last updated {datetime.datetime.now()}")
    return st_data

@st.experimental_fragment(run_every=1)
def get_latest_locations():
    return st.session_state['markers'][-1].location
    
with left:
    st_data =  generate_chart()
    st_data
with right: 
    st.caption(f"Last updated {datetime.datetime.now()}")
    st.write(get_latest_locations())

      