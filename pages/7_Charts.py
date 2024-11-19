import streamlit as st

def get_gantt_chart(use_container_width: bool):
    import altair as alt
    import pandas as pd

    source = pd.DataFrame([
        {"task": "A", "start": 1, "end": 3},
        {"task": "B", "start": 3, "end": 8},
        {"task": "C", "start": 8, "end": 10},
        {"task": "D", "start": 8, "end": 400}
    ])

    brush = alt.selection_interval()
    chart = alt.Chart(source).mark_bar().encode(
        x='start',
        x2='end',
        y='task'
    ).add_params(
    brush
)

    st.altair_chart(chart, theme="streamlit", use_container_width=True)



get_gantt_chart(True)