import streamlit as st
from streamlit_gsheets import GSheetsConnection

# Create a connection object.
conn = st.connection("gsheets", type=GSheetsConnection)

@st.experimental_fragment(run_every=5)
def get_data():
    df = conn.read(
        worksheet="Blad1",
        ttl="0",
    )
    df.set_index("vehicle_id")
    st.write("### Vehicle Data", df.sort_index())


with st.container():
    get_data()
    