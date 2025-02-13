import streamlit as st
import altair as alt
import pandas as pd

from utils.classes import Vehicle, Trip

def get_gantt_chart(use_container_width: bool) -> None:
    """
    Create and display a Gantt chart of vehicle schedules using Altair.

    The chart visualizes the schedule of all vehicles and uses a custom color scale
    based on the trip status.

    Parameters
    ----------
    use_container_width : bool
        Whether to display the chart using the container's full width.
    """
    # Get schedules of all vehicles in a DataFrame
    schedules = Vehicle.get_schedules()

    # Ensure 'start' and 'end' columns are datetime objects
    schedules["start"] = pd.to_datetime(schedules["start"])
    schedules["end"] = pd.to_datetime(schedules["end"])

    # Define a brush selection for interactivity (optional)
    brush = alt.selection_interval()

    # Define a color scale mapping for status
    status_to_hex = {
        'draft': '#1f77b4',
        'requested': '#ffa500',
        'confirmed': '#2ca02c',
        'in_transit': '#d62728',
        'completed': '#9467bd',
        'cancelled': '#8c564b',
        'accepted': '#e377c2',
        'modified': '#7f7f7f'
    }

    # Create Gantt Chart using Altair with a color scale for the 'status' field
    chart = (
        alt.Chart(schedules)
        .mark_bar(opacity=0.7)
        .encode(
            x=alt.X(
                'start:T',
                axis=alt.Axis(title='Time', labelAngle=-45, format='%H:%M')
            ),
            x2='end:T',
            y=alt.Y('vehicle:N', title='Vehicle'),
            color=alt.Color(
                'status:N',
                scale=alt.Scale(
                    domain=list(status_to_hex.keys()),
                    range=list(status_to_hex.values())
                ),
                title='Status'
            ),
            tooltip=[alt.Tooltip('task_name:N')]
        )
        .add_params(brush)
    )

    st.altair_chart(chart, use_container_width=use_container_width)
