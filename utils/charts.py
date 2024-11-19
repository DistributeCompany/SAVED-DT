import streamlit as st
from utils.classes import Vehicle, Trip

def get_gantt_chart(use_container_width: bool):
    import altair as alt
    import pandas as pd

    # Get schedules of all vehicles in a DataFrame
    schedules = Vehicle.get_schedules()

    # Reformat start and end columns
    schedules["start"] = pd.to_datetime(schedules["start"])
    schedules["end"] = pd.to_datetime(schedules["end"])

    # Add brush (optional)
    brush = alt.selection_interval()

    # Color bars based on status of trip Not required?
    status_to_hex = {
        'draft': '#1f77b4',
        'requested': 'orange',
        'confirmed': '#2ca02c',
        'in_transit': '#d62728',
        'completed': '#9467bd',
        'cancelled': '#8c564b',
        'accepted': '#e377c2',
        'modified': '#7f7f7f'
    }
    # Not required?
    schedules['color'] = schedules['status'].map(status_to_hex)

    # Create Gantt Chart
    chart = alt.Chart(schedules).mark_bar(opacity=0.7).encode(
        x=alt.X('start', axis=alt.Axis(title='Time', labelAngle=-45, format = ("%H %M"))),
        x2='end',
        y='vehicle',
        color = 'status',
        tooltip=['task_name'],
    ).add_params(
    brush
)

    st.altair_chart(chart, use_container_width=True)

