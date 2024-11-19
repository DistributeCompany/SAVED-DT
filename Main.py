import streamlit as st

st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)

st.write("# Autonomous Delivery Control Tower 👋")

st.markdown(
    """
    **👈 TODO**

    ## Manual Mode
    Story.
    - Select input parameters (number of vehicles, jobs, speed of simulation, etc. in sidebar)
    - Initialize model with a map and (empty) tables/graphs
    - Start/End/Reset simulation buttons
    - User starts simulation
    - Click on map to add a destination (= a delivery job)
    - Select a vehicle to assign it to a vehicle and insert it in current schedule
    - Vehicle deliver container
    - Realtime monitor movements (and status) of vehicles out-for-delivery on map
    - Realtime monitor status of vehicles in tables/graphs
    - Realtime monitor performance of system in charts/KPIs
    - End simulation (after time has passed, number of jobs, ...)
"""
)