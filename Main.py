import streamlit as st

import streamlit as st

# Page configuration
st.set_page_config(
    page_title="SAVED - Digital Model - Demonstrator",
    page_icon=":world_map:",
    layout="wide",
)

# Title and introductory description
st.title("Welcome to the SAVED Digital Model")

st.markdown("""
The **SAVED Digital Model** is a logistics visualization and representation tool, developed within the SAVED research project. It serves as a logistics planning & control system for Autonomous Vehicles on the XL Businesspark Almelo. 
In the current status, the model is able to manually create trips and assign vehicles to execute a trip. Trip execution is simulated based on input parameters. 
            

The model is built according to the principles of the [Open Trip Model (OTM5)](https://otm5.opentripmodel.org/). This allows for a common vocabulary regarding the logistics operations, and allows for smoother integration with other systems (i.e., by sending/receiving OTM-compliant JSON messages) 
            
Some features of the Digital Model:          
- **Plan and monitor trips:** Create, view, and manage trips in real time.
- **Manage vehicles and routes:** Track vehicle performance, update schedules, and visualize routes on interactive maps.
- **Analyze data:** View statistics, schedules, and other charts to assess the performance of your transportation network.

The model also serves as a base for further developments. Further developments include:
- **Digital Shadow**. Integrate real-life (sensor) data such as to create a real-time shadow of the physical system. Possible data sources include, vehicle GPS location, vehicle battery level, camera feeds, ...
- **Digital Twin**. The model can provide real-time decision-support to optimize logistics operations on XL Business Park Almelo. This also requires integration with logistics planning software (e.g., to retreive transport jobs) 

The interested reader is referred to [Nikula et al. (2020)](http://dx.doi.org/10.1515/eng-2020-0088) for a more detailed discussion on the differences between Model, Shadow, and Twin.             
""")

st.header("Getting Started")
st.markdown("""
**Step 1: Installation**

- Ensure you have Python 3.7+ installed.
- Install the required dependencies with the following command:
  ```bash
  pip install -r requirements.txt

            
**Step 2: Running the App**    

- Launch the app by running the following command: 
  ```bash
  streamlit run Main.py


**Step 3: Navigating the App**
- **Main Tab**: General introduction to the Digital Model.
- **Digital Model Tab**: The main functionality of the app lives here. 
- **Documentation Tab**: Detailed documentation of the model. 

**Step 4: Using the Digital Model**
- Configure the model in the **Inputs** tab (e.g., set the number of vehicles)
- Vehicles are initialized at the Parking at CTT (marked by a 'P' Icon).
- Click on the map in the **Map** tab to start creating a trip (note: only the shown markers are valid locations).
- A vehicle will start a Trip at the first Marker clicked. If you want to start the trip at the current location of the vehicle, click that Marker first. 
- Keep clicking to add more locations. 
- To finish, click 'Create Trip below the map. Click 'Reset' to start over. 
- Assign a vehicle to the trip by selecting a vehicle from the dropdown menu in the **To Be Planned Trips** table.  
- The vehicle will execute the trip as soon as possible (i.e., depending on already scheduled trips)      
- Note: the map is updated every x seconds to reflect updates in the progress of the trip. 
""")


st.header("Contact")
st.markdown("""
Please contact Berry Gerrits via b.gerrits@distribute.company for any inquiries. 
""")

st.header("Funding")
st.markdown("""
**This research has been funded by SIA via the RAAK-PRO project: SAVED.** https://www.sia-projecten.nl/project/saved-samenwerkend-autonoom-vervoer-op-bedrijventerreinen
""")