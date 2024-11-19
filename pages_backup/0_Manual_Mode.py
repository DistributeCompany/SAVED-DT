import streamlit as st
import folium
from streamlit_folium import st_folium
import random
import pandas as pd

st.set_page_config(page_title="Manual mode",
                   page_icon="🌍",
                   layout="wide")

st.markdown("# Manual Mode")
st.sidebar.header("Manual Mode Settings")
st.write(
    """This page allows you to manually plan a fleet of autonomous delivery vehicles. First select the settings in the sidebar before running `Start Simulation`."""
)


# Session state
if "center" not in st.session_state:
    st.session_state["center"] = [52.237182765244796, 6.853408813476563]
if "zoom" not in st.session_state:
    st.session_state["zoom"] = 15
if "markers" not in st.session_state:   
    st.session_state["markers"] = []
if "fleet_size" not in st.session_state:
    st.session_state["fleet_size"] = st.sidebar.slider('No. of street robots',1,5,step=1)
if "vehicle_data" not in st.session_state:
    st.session_state["vehicle_data"] = []
if 'slider_disabled' not in st.session_state:
    st.session_state.slider_disabled = False

# Side-bar
# Conditionally disable the slider(s) when the simulation has started
if st.session_state.slider_disabled:
     st.session_state["fleet_size"] = st.sidebar.slider('No. of street robots',1,5, value=st.session_state["fleet_size"],step=1, disabled=True, key='off')
else:
     st.session_state["fleet_size"] = st.sidebar.slider('No. of street robots',1,5,step=1,key='on')


# Function to toggle the slider state
def init():
    '''
    Initialization of simulation run.
    '''
    # Disable all input parameters
    st.session_state.slider_disabled = True

def reset():
    '''
    Reset of simulation run.
    '''
    # Enable all input parameters
    st.session_state.slider_disabled = False
    pass

# Main view layout
left, right = st.columns(2)

with left:
    col1, col2 = st.columns(2)
    with col1:
        st.button("Start Simulation",on_click=init)
    with col2:
        st.button("Reset Simulation",on_click=reset)

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
        width=1000,
    )      

with right:
    """
    Vehicle related data
    """
    st.session_state["vehicle_data"] = []
    for vehicle in range(st.session_state["fleet_size"]):
        # Init vehicle
        data = {'id':vehicle+1,'lat':52.24103278020692,'lon':6.855399012565614}
        st.session_state["vehicle_data"].append(data)

    df = pd.DataFrame(st.session_state["vehicle_data"])
    df.set_index('id')
    st.write(df.sort_index())


st_data