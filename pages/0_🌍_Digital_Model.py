import streamlit as st
import numpy as np
import pandas as pd
import time
import folium

from folium.plugins import Fullscreen
from streamlit_folium import st_folium

from utils.entities import *
from utils.tables import *
from utils.classes import Location, Trip, Actor, Route, Action, Vehicle
from utils.osmnx import get_graph_from_place
from utils.charts import get_gantt_chart
from utils.stats import update_statistics

# Page configuration
st.set_page_config(
    page_title="SAVED - Digital Model",
    page_icon=":world_map:️",
    layout="wide",
)


# Session state initialization
session_keys = {
    "center": [52.32104656977127, 6.646610524501365],
    "zoom": 15,
    "markers": [],
    "destinations": [],
    "sleep_time": 2,
    "auto_refresh": True,
    "do_refresh": False,
    "static_locations": [],
    "polylines": [],
    "disable_inputs": False,
    "clicked_before_reset": {'lat': 0.0, 'lng': 0.0},
    "clicked_before_creating_trip": {'lat': 0.0, 'lng': 0.0},
    "selected_rows": {"rows": [], "columns": []},
    "create_trip": [],
    "locations": [],
    "trips": [],
    "actors": [],
    "routes": [],
    "actions": [],
    "vehicles": [],
    "vehicle_markers": [],
    "num_terminal_tractors": 1,
    "terminal_tractor_capacity": 1,
    "terminal_tractor_speed": 15.0,
    "terminal_tractor_load_time": 0,
    "terminal_tractor_unload_time": 0,
    "terminal_tractor_co2_emission": 0,
    "terminal_tractor_nox_emission": 0,
    "terminal_tractor_noise_pollution": 0,
    "terminal_tractor_land_use": 0.03,
    "terminal_tractor_energy_consumption_moving": 0,
    "terminal_tractor_energy_consumption_idling": 0,
    "terminal_tractor_battery_capacity": 0,
    "terminal_tractor_battery_threshold": 0,
    "terminal_tractor_charge_speed": 0,
    "real_time_factor": 1,
}

for key, default in session_keys.items():
    if key not in st.session_state:
        st.session_state[key] = default

# Initialize OSM graph if not available in session
if "graph" not in st.session_state:
    st.session_state.graph = get_graph_from_place("XL Businesspark Twente", network_type='all')

# Create Streamlit tabs
tab1, tab2 = st.tabs(["Map", "Inputs"])

def on_input_change() -> None:
    """Update number of vehicles when input changes."""
    st.session_state['vehicles'] = create_vehicles(
        num_vehicles=st.session_state.num_terminal_tractors,
        type="terminal_tractor"
    )
    st.session_state['vehicle_markers'] = [vehicle.marker for vehicle in st.session_state['vehicles']]

def update_real_time_factor() -> None:
    """Update the actual speed of all vehicles based on the real-time factor."""
    vehicles = Vehicle.get_all_vehicles()
    for vehicle in vehicles:
        vehicle.update_instance_parameter('actual_speed', vehicle.average_speed * st.session_state['real_time_factor'])

def update_vehicle_properties() -> None:
    """Update vehicle properties from the current session state parameters."""
    vehicles = Vehicle.get_all_vehicles()
    for vehicle in vehicles:
        vehicle.update_instance_parameter('average_speed', st.session_state.terminal_tractor_speed / 3.6) #km/h -> m/s
        vehicle.update_instance_parameter('actual_speed', vehicle.average_speed * st.session_state['real_time_factor'])
        vehicle.update_instance_parameter('load_time', st.session_state.terminal_tractor_load_time)
        vehicle.update_instance_parameter('unload_time', st.session_state.terminal_tractor_unload_time)
        vehicle.update_instance_parameter('co2_emission', st.session_state.terminal_tractor_co2_emission)
        vehicle.update_instance_parameter('nox_emission', st.session_state.terminal_tractor_nox_emission)
        vehicle.update_instance_parameter('noise_pollution', st.session_state.terminal_tractor_noise_pollution)
        vehicle.update_instance_parameter('land_use', st.session_state.terminal_tractor_land_use)
        vehicle.update_instance_parameter('battery_capacity', st.session_state.terminal_tractor_battery_capacity)
        vehicle.update_instance_parameter('energy_consumption_moving', st.session_state.terminal_tractor_energy_consumption_moving)
        vehicle.update_instance_parameter('energy_consumption_idling', st.session_state.terminal_tractor_energy_consumption_idling)
        vehicle.update_instance_parameter('battery_threshold', st.session_state.terminal_tractor_battery_threshold)
        vehicle.update_instance_parameter('charge_speed', st.session_state.terminal_tractor_charge_speed)

# Sidebar settings
st.sidebar.markdown("## Inputs")

def delete_all_trips() -> None:
    """
    NOT IN USE. 

    Delete all trips and reset relevant session states.
    Resets the instances of Trip, Actor, Action, and Route.
    """
    for cls in [Trip, Actor, Action, Route]:
        cls.delete_all_instances()
    st.session_state.disable_inputs = False
    st.session_state.destinations = []
    st.session_state.clicked_before_reset = st_data['last_object_clicked']

def add_new_delivery() -> list:
    """
    Add a new delivery based on the user's last map click.
    
    Returns:
        list: The updated list of static location markers.
    """
    if st_data['last_object_clicked']:
        filtered_list = [
            marker for marker in st.session_state['static_locations']
            if marker.location[0] == st_data['last_object_clicked']['lat'] and 
               marker.location[1] == st_data['last_object_clicked']['lng']
        ]
        if filtered_list and 'tractor' not in st_data['last_object_clicked_popup'] and \
           st_data['last_object_clicked'] != st.session_state['clicked_before_creating_trip']:
            location = Location.get_by_georeference([
                st_data['last_object_clicked']['lat'],
                st_data['last_object_clicked']['lng']
            ])
            if location is not None:
                if not st.session_state['create_trip']:
                    st.session_state['create_trip'].append(location)
                elif st.session_state['create_trip'][-1] != location:
                    st.session_state['create_trip'].append(location)
    return st.session_state["static_locations"]

def create_map(markers: list, user_markers: list, microhubs: list, routes: list) -> dict:
    """
    Create and display a Folium map with various feature groups.

    Parameters:
        markers (list): Vehicle markers.
        user_markers (list): User-added markers.
        microhubs (list): Markers for microhubs.
        routes (list): Route polylines.

    Returns:
        dict: The Folium map data.
    """
    m = folium.Map(location=st.session_state["center"], zoom_start=st.session_state["zoom"], width=1600)
    Fullscreen().add_to(m)

    fg_vehicles = folium.FeatureGroup(name="Vehicles")
    for marker in markers:
        fg_vehicles.add_child(marker)

    fg_user = folium.FeatureGroup(name="UserMarkers")
    for marker in user_markers:
        fg_user.add_child(marker)

    fg_microhubs = folium.FeatureGroup(name="Microhubs")
    for hub in microhubs:
        fg_microhubs.add_child(hub)

    fg_routes = folium.FeatureGroup(name='Routes')
    for route in routes:
        fg_routes.add_child(route)

    st_data = st_folium(
        m,
        center=st.session_state["center"],
        zoom=15,
        key="new",
        feature_group_to_add=[fg_vehicles, fg_user, fg_microhubs, fg_routes],
        height=400,
        width=1600,
    )
    folium.LayerControl().add_to(m)
    return st_data

def color_change(val: str) -> str:
    """
    Return a CSS style for background color based on trip status.
    """
    color_map = {
        'draft': 'background-color: #1f77b4',
        'requested': 'background-color: #ffa500',
        'confirmed': 'background-color: #2ca02c',
        'in_transit': 'background-color: #d62728',
        'completed': 'background-color: #9467bd',
        'cancelled': 'background-color: #8c564b',
        'accepted': 'background-color: #e377c2',
        'modified': 'background-color: #7f7f7f'
    }
    return color_map.get(val, '')

def color_change_action(val: str) -> str:
    """
    Return a CSS style for background color based on action lifecycle.
    """
    color_map = {
        'requested': 'background-color: #ACE5EE',
        'planned': 'background-color: #EDC8AB',
        'projected': 'background-color: #ABEDD1',
        'actual': 'background-color: #ABEDD1',
        'realized': 'background-color: #ABEDD1',
    }
    return color_map.get(val, '')

def create_new_trip() -> None:
    """
    Create a new trip based on user input and update session state.
    """
    if (st.session_state.clicked_before_reset['lat'] != st_data['last_object_clicked']['lat'] and
        st.session_state.clicked_before_reset['lng'] != st_data['last_object_clicked']['lng']):
        st.session_state.clicked_before_reset = {'lat': 0.0, 'lng': 0.0}
        actors = [location.actors[0] for location in st.session_state['create_trip']]
        trip = create_trip(actors)
        routes = []
        actions_to_add = []
        for idx, row in to_create_trip.iterrows():
            origin = row['from_location']
            destination = row['to_location']
            route_actors = [row['from_actor'], row['to_actor']]
            route = create_route(route_actors, st.session_state.graph, origin=origin, destination=destination)
            routes.append(route)
            st.session_state["routes"].append(route)
            actions_to_add.append({
                'sequence_nr': len(actions_to_add),
                'type': 'move',
                'origin': origin,
                'destination': destination,
                'route': route,
                'trip': trip
            })
        if st.session_state["static_locations"]:
            for ac in actions_to_add:
                create_action(
                    ac['origin'],
                    ac['destination'],
                    sequence_nr=ac['sequence_nr'],
                    route=ac['route'],
                    trip=ac['trip'],
                    action_type=ac['type']
                )
            st.session_state["actions"] = Action.get_all_actions()
        else:
            raise Exception("No micro-hub available. Please check st.session_state.microhubs")
        st.session_state['clicked_before_creating_trip'] = {
            'lat': st.session_state['create_trip'][-1].georeference[0],
            'lng': st.session_state['create_trip'][-1].georeference[1]
        }
        print(f"Overwriting session state: {st.session_state['clicked_before_creating_trip']}")
        st.session_state['create_trip'] = []

# Get data for tables
trips = get_trips()
vehicles = get_vehicles()

def reset_trip() -> None:
    """Reset the list of locations for the current trip."""
    st.session_state.create_trip = []

def get_currently_creating_trip() -> pd.DataFrame:
    """
    Construct a DataFrame showing details of the trip being created.

    Returns:
        pd.DataFrame: A DataFrame with origin, destination, and actor details.
    """
    trip_list = []
    for i in range(len(st.session_state.create_trip) - 1):
        pair = {
            "from": st.session_state.create_trip[i].name,
            "to": st.session_state.create_trip[i+1].name,
            "from_to": f"{st.session_state.create_trip[i].actors[0].name} - {st.session_state.create_trip[i+1].actors[0].name}",
            "from_location": st.session_state.create_trip[i],
            "to_location": st.session_state.create_trip[i+1],
            "from_actor": st.session_state.create_trip[i].actors[0],
            "to_actor": st.session_state.create_trip[i+1].actors[0]
        }
        trip_list.append(pair)
    return pd.DataFrame(trip_list)

with tab1:
    st.markdown("# Digital Model - Manual Mode")
    st.write("Click any Marker on the map to start creating a trip. Please wait until the 'Creating Trips' table is created/updated, before clicking the next Marker.")
    st_data = create_map(
        st.session_state["vehicle_markers"],
        st.session_state["destinations"],
        st.session_state["static_locations"],
        st.session_state["polylines"]
    )
    
    left, right = st.columns(2)
    
    with left:
        if not st.session_state['static_locations']:
            locations = create_locations('locations.json')
            previous_company = ""
            if "CTT" in locations[0][0].name:
                previous_company = "CTT"
            elif "BOL" in locations[0][0].name:
                previous_company = "Bolk"
            elif "BLK" in locations[0][0].name:
                previous_company = "Bleckmann"
            elif "TBL" in locations[0][0].name:
                previous_company = "Timberland"
            actor = create_actor(locations[0][0], name=previous_company)
            for location in locations:
                st.session_state["locations"].append(location[0])
                st.session_state["static_locations"].append(location[1])
                current_company = ""
                if "CTT" in location[0].name:
                    current_company = "CTT"
                elif "BOL" in location[0].name:
                    current_company = "Bolk"
                elif "BLK" in location[0].name:
                    current_company = "Bleckmann"
                elif "TBL" in location[0].name:
                    current_company = "Timberland"
                if current_company != previous_company:
                    actor = create_actor(location[0], name=current_company)
                    previous_company = current_company
                location[0].actors = actor
                actor[0].locations.append(location[0])
            st.session_state['vehicles'] = create_vehicles(
                st.session_state.num_terminal_tractors,
                type="terminal_tractor",
                average_speed=st.session_state.terminal_tractor_speed / 3.6,
                load_time=st.session_state.terminal_tractor_load_time,
                unload_time=st.session_state.terminal_tractor_unload_time
            )
            st.session_state['vehicle_markers'] = [vehicle.marker for vehicle in st.session_state['vehicles']]
        
        if st.session_state['create_trip']:
            global to_create_trip
            st.markdown("### Creating Trip")
            to_create_trip = get_currently_creating_trip()
            columns_to_hide = [col for col in ['from_location', 'to_location', 'from_actor', 'to_actor'] if col in to_create_trip.columns]
            filtered_trips = to_create_trip.drop(columns=columns_to_hide)
            st.data_editor(filtered_trips, use_container_width=True)
            st.button("Create Trip", on_click=create_new_trip)
            st.button("Reset Trip", type="primary", on_click=reset_trip)
        
        if not trips.empty:
            st.markdown("### To Be Planned Trips")
            filtered_df = trips[trips['status'].isin(['draft'])]
            columns_to_hide = ['polyline', 'marker', 'progress', 'length']
            filtered_trips = filtered_df.drop(columns=columns_to_hide)
            edited_df = st.data_editor(
                filtered_trips,
                key='trip_edit',
                column_config={
                    "vehicle": st.column_config.SelectboxColumn(
                        "vehicle",
                        options=vehicles['name'],
                        required=False,
                    )
                },
                disabled=['name', 'creation_date', 'status', 'from', 'to', 'id'],
                hide_index=True,
                use_container_width=True
            )
            for row, vehicle in st.session_state.trip_edit['edited_rows'].items():
                success = Vehicle.get_by_vehicle_name(vehicle['vehicle']).assign_to_trip(
                    Trip.get_by_id(edited_df.iloc[row]['id'])
                )
        else:
            st.session_state['disable_inputs'] = False
    
    with right:
        did_user_click = add_new_delivery()
        if not trips.empty:
            st.markdown("### All Trips")
            selected_options = st.multiselect(
                "Filter trips based on status",
                options=['all','draft','requested','confirmed','in_transit','completed','cancelled','accepted','modified'],
                default=['all']
            )
            st.session_state['disable_inputs'] = True
            filtered_df = trips if 'all' in selected_options else trips[trips['status'].isin(selected_options)]
            columns_to_hide = ['polyline', 'marker']
            filtered_trips = filtered_df.drop(columns=columns_to_hide)
            styled_and_filtered_trips = filtered_trips.style.applymap(color_change, subset=['status'])
            trip_list = st.dataframe(
                styled_and_filtered_trips,
                key="data",
                on_select="rerun",
                selection_mode=["single-row"],
                column_config={
                    "progress": st.column_config.ProgressColumn(
                        "progress",
                        help="The progress of the trip",
                        min_value=0,
                        max_value=100,
                    ),
                },
                use_container_width=True,
                hide_index=True
            )
            selected_rows = trip_list.selection
            st.session_state['selected_rows'] = selected_rows
            st.session_state["polylines"] = []
            for row in st.session_state['selected_rows']['rows']:
                route = trips.iloc[row]['polyline']
                if route not in st.session_state["polylines"]:
                    st.session_state["polylines"].append(route)
                trip = Trip.get_by_id(trips.iloc[row]['id'])
                st.write(f"Details of {trip.name}")
                actions = get_actions_of_trip(trip)
                styled_actions = actions.style.applymap(color_change_action, subset=['lifecycle'])
                st.dataframe(
                    styled_actions,
                    column_config={
                        "progress": st.column_config.ProgressColumn(
                            "progress",
                            help="The progress of the action",
                            min_value=0,
                            max_value=100,
                        ),
                    },
                    use_container_width=True,
                    hide_index=True,
                )
    
    st.markdown("## Detailed Trip View")
    options = [trip.name for trip in Trip.get_all_trips()]
    selected_trips = st.multiselect("Filter trips based on name", options=options)
    st.session_state["polylines"] = []
    selected_actions = pd.DataFrame()
    for trip_name in selected_trips:
        trip = Trip.get_by_name(trip_name)
        df_actions = get_actions_of_trip(trip)
        selected_actions = pd.concat([selected_actions, df_actions], ignore_index=True)
        for action in trip.get_actions():
            if action.action_type == 'move' and action.route.polyline not in st.session_state['polylines']:
                st.session_state["polylines"].append(action.route.polyline)
    if not selected_actions.empty:
        styled_actions = selected_actions.style.applymap(color_change_action, subset=['lifecycle'])
        st.dataframe(
            styled_actions,
            column_config=get_trip_details_table_config(),
            use_container_width=True,
            hide_index=True,
        )
    
    # Start trips with status "requested"
    trips_with_status_requested = Trip.get_by_status('requested')
    start_trips(trips_with_status_requested)
    
    # Update vehicle positions
    trips_with_status_in_transit = Trip.get_by_status('in_transit')
    st.session_state['vehicle_markers'], st.session_state['destinations'] = update_vehicle_positions(
        trips_with_status_in_transit,
        st.session_state['vehicle_markers'],
        st.session_state['destinations']
    )
    
    # Display Schedule and Vehicle Statistics
    if not trips.empty:
        st.markdown("## Schedule")
        st.write(get_gantt_chart(True))
        latest_vehicle_stats = update_statistics()
        if not latest_vehicle_stats.empty:
            st.markdown("## Vehicle Raw Data")
            columns_to_hide = ['id','energy_consumption','co2_emission','nox_emission','noise_pollution','land_use']
            latest_vehicle_stats = latest_vehicle_stats.drop(columns=columns_to_hide)
            latest_vehicle_stats['utilization'] = latest_vehicle_stats['utilization'] * 100
            st.dataframe(
                latest_vehicle_stats,
                column_config=get_vehicle_data_table_config(),
                hide_index=True
            )
            st.markdown("## Vehicle Occupancy")
            st.bar_chart(
                latest_vehicle_stats,
                y=['move','idle','load','unload'],
                y_label='Vehicle',
                x='name',
                x_label='Occupancy',
                stack='normalize',
                horizontal=True
            )

with tab2:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("## General")
        st.number_input(
            "Real-time factor",
            min_value=1,
            value=st.session_state.real_time_factor,
            key='real_time_factor',
            on_change=update_real_time_factor,
            disabled=True
        )
    with col2:
        st.markdown("## Vehicle")
        use_terminal_tractors = st.toggle("Terminal Tractor", value=True)
        if use_terminal_tractors:
            st.slider(
                'Number of Terminal Tractors',
                min_value=1,
                max_value=7,
                key='num_terminal_tractors',
                value=st.session_state.num_terminal_tractors,
                on_change=on_input_change,
                disabled=st.session_state.disable_inputs
            )
            st.number_input(
                "Speed (km/h)",
                value=st.session_state.terminal_tractor_speed,
                key='terminal_tractor_speed',
                min_value=5.0,
                max_value=45.0,
                on_change=update_vehicle_properties
            )
            st.number_input(
                "Capacity per terminal tractor",
                value=st.session_state.terminal_tractor_capacity,
                key='terminal_tractor_capacity',
                disabled=True
            )
            use_loading_times = st.toggle("Use (un)loading times", value=False)
            if use_terminal_tractors and use_loading_times:
                st.markdown(":stopwatch: **Times**")
                st.number_input(
                    "Load Time (s)",
                    value=st.session_state.terminal_tractor_load_time,
                    key='terminal_tractor_load_time',
                    on_change=update_vehicle_properties
                )
                st.number_input(
                    "Unload Time (s)",
                    value=st.session_state.terminal_tractor_unload_time,
                    key='terminal_tractor_unload_time',
                    on_change=update_vehicle_properties
                )
            else:
                st.session_state.terminal_tractor_load_time = 0
                st.session_state.terminal_tractor_unload_time = 0
                update_vehicle_properties()
            use_emissions = st.toggle("Use emissions", value=False)
            if use_terminal_tractors and use_emissions:
                st.markdown(":smoking: **Emissions**")
                st.number_input(
                    "CO2 Emission (g/km)",
                    value=st.session_state.terminal_tractor_co2_emission,
                    key='terminal_tractor_co2_emission',
                    on_change=update_vehicle_properties
                )
                st.number_input(
                    "NOx Emission (g/km)",
                    value=st.session_state.terminal_tractor_nox_emission,
                    key='terminal_tractor_nox_emission',
                    on_change=update_vehicle_properties
                )
                st.number_input(
                    "Noise Pollution (dB)",
                    value=st.session_state.terminal_tractor_noise_pollution,
                    key='terminal_tractor_noise_pollution',
                    on_change=update_vehicle_properties
                )
                st.number_input(
                    "Land Use (m3)",
                    value=st.session_state.terminal_tractor_land_use,
                    key='terminal_tractor_land_use',
                    on_change=update_vehicle_properties
                )
            else:
                st.session_state.terminal_tractor_co2_emission = 0
                st.session_state.terminal_tractor_nox_emission = 0
                st.session_state.terminal_tractor_noise_pollution = 0
                st.session_state.terminal_tractor_land_use = 0
                update_vehicle_properties()
            use_battery = st.toggle("Use battery", value=False)
            if use_terminal_tractors and use_battery:
                st.markdown(":battery: **Battery**")
                st.number_input(
                    "Battery Capacity (kWh)",
                    value=st.session_state.terminal_tractor_battery_capacity,
                    key='terminal_tractor_battery_capacity',
                    on_change=update_vehicle_properties
                )
                st.number_input(
                    "Energy Consumption - Driving (kW)",
                    value=st.session_state.terminal_tractor_energy_consumption_moving,
                    key='energy_consumption_moving',
                    on_change=update_vehicle_properties
                )
                st.number_input(
                    "Energy Consumption - Idling (kW)",
                    value=st.session_state.terminal_tractor_energy_consumption_idling,
                    key='energy_consumption_idling',
                    on_change=update_vehicle_properties
                )
                st.number_input(
                    "Low Battery Threshold (kWh)",
                    value=st.session_state.terminal_tractor_battery_threshold,
                    key='terminal_tractor_battery_threshold',
                    on_change=update_vehicle_properties
                )
                st.number_input(
                    "Charge Speed (kW)",
                    value=st.session_state.terminal_tractor_charge_speed,
                    key='terminal_tractor_charge_speed',
                    on_change=update_vehicle_properties
                )
            else:
                st.session_state.terminal_tractor_battery_capacity = 0
                st.session_state.terminal_tractor_energy_consumption_moving = 0
                st.session_state.terminal_tractor_energy_consumption_idling = 0
                st.session_state.terminal_tractor_battery_threshold = 0
                st.session_state.terminal_tractor_charge_speed = 0
                update_vehicle_properties()
        else:
            st.session_state.num_terminal_tractors = 0
    with col3:
        st.markdown("## Trip")
    auto_refresh = st.sidebar.checkbox('Auto Refresh?', st.session_state.auto_refresh)
    if auto_refresh:
        number = st.sidebar.number_input('Refresh rate in seconds', value=st.session_state.sleep_time)
        st.session_state.sleep_time = number
    if auto_refresh:
        st.session_state.do_refresh = False
        time.sleep(st.session_state.sleep_time)
        st.session_state.do_refresh = True
        st.rerun()
