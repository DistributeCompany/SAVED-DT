import streamlit as st
import time
import random
import numpy as np
import pandas as pd
from datetime import datetime

import folium
from folium.plugins import Fullscreen
from streamlit_folium import st_folium

from utils.classes import Location, Trip, Actor, Route, Action, Vehicle

from utils.osmnx import get_graph_from_place, get_shortest_path, get_route_length, get_coordinates, get_interpolated_position
from utils.charts import get_gantt_chart
from utils.entities import *
from utils.entities import get_trips, get_vehicles, get_actions_of_trip
from utils.stats import update_statistics
from utils.tables import *
import osmnx as ox

st.set_page_config(
    page_title="Digital Model",
    page_icon=":world_map:️",
    layout="wide",
)

#CONSTANTS
HUB_LOCATION = {'lat': 52.239623555802815, 'lng': 6.853921115398408}

# Maintain session states
if "center" not in st.session_state:
    st.session_state["center"] = [52.32104656977127, 6.646610524501365]
if "zoom" not in st.session_state:
    st.session_state["zoom"] = 15
if "markers" not in st.session_state:   
    st.session_state["markers"] = []
if "destinations" not in st.session_state:   
    st.session_state["destinations"] = []   #Folium.Marker
if "sleep_time" not in st.session_state:
    st.session_state.sleep_time = 2
if "auto_refresh" not in st.session_state:
    st.session_state.auto_refresh = True
if "do_refresh" not in st.session_state:
    st.session_state.do_refresh = False
if "static_locations" not in st.session_state:
    st.session_state.static_locations = []
if "polylines" not in st.session_state:
    st.session_state.polylines = []
if 'disable_inputs' not in st.session_state:
    st.session_state.disable_inputs = False
if 'clicked_before_reset' not in st.session_state:
    st.session_state.clicked_before_reset = {'lat': 0.0, 'lng': 0.0}
if 'clicked_before_creating_trip' not in st.session_state:
    st.session_state.clicked_before_creating_trip = {'lat': 0.0, 'lng': 0.0}
if 'selected_rows' not in st.session_state:
    st.session_state.selected_rows = {"rows":[],"columns":[]}
if 'create_trip' not in st.session_state:
    st.session_state.create_trip = []

# OTM
if "locations" not in st.session_state:
    st.session_state.locations = [] #not sure whether required
if "trips" not in st.session_state:
    st.session_state.trips = []    
if "actors" not in st.session_state:
    st.session_state.actors = []  #not sure whether required 
if "routes" not in st.session_state:
    st.session_state.routes = []  #not sure whether required     
if "actions" not in st.session_state:
    st.session_state.actions = []  #not sure whether required     
if "vehicles" not in st.session_state:
    st.session_state.vehicles = []
if "vehicle_markers" not in st.session_state:
    st.session_state.vehicle_markers = [] #Folium.CircleMarker

# Terminal Tractors
if "num_terminal_tractors" not in st.session_state:
    st.session_state.num_terminal_tractors = 1
if 'terminal_tractor_capacity' not in st.session_state:
    st.session_state.terminal_tractor_capacity = 1  
if 'terminal_tractor_speed' not in st.session_state:
    st.session_state.terminal_tractor_speed = 15.0
if 'terminal_tractor_load_time' not in st.session_state:
    st.session_state.terminal_tractor_load_time = 0
if 'terminal_tractor_unload_time' not in st.session_state:
    st.session_state.terminal_tractor_unload_time = 0
if 'terminal_tractor_co2_emission' not in st.session_state:
    st.session_state.terminal_tractor_co2_emission = 0 #g/km
if 'terminal_tractor_nox_emission' not in st.session_state:
    st.session_state.terminal_tractor_nox_emission = 0 #g/km    
if 'terminal_tractor_noise_pollution' not in st.session_state:
    st.session_state.terminal_tractor_noise_pollution = 0 #dB
if 'terminal_tractor_land_use' not in st.session_state:
    st.session_state.terminal_tractor_land_use = 0.03 #m3        
if 'terminal_tractor_energy_consumption_moving' not in st.session_state:
    st.session_state.terminal_tractor_energy_consumption_moving = 0 #kW
if 'terminal_tractor_energy_consumption_idling' not in st.session_state:
    st.session_state.terminal_tractor_energy_consumption_idling = 0 #kW
if 'terminal_tractor_battery_capacity' not in st.session_state:
    st.session_state.terminal_tractor_battery_capacity = 0 #kWh
if 'terminal_tractor_battery_threshold' not in st.session_state:
    st.session_state.terminal_tractor_battery_threshold = 0 #kWh     
if 'terminal_tractor_charge_speed' not in st.session_state:
    st.session_state.terminal_tractor_charge_speed = 0 #kW   
  
if "real_time_factor" not in st.session_state:
    st.session_state.real_time_factor = 1

# OSM
if "graph" not in st.session_state:
    #optionally pass parameter on network_type, defaults to 'drive'
    st.session_state.graph = get_graph_from_place("XL Businesspark Twente",network_type='all')

tab1, tab2, tab3 = st.tabs(["Map", "Inputs", "Outputs"])

def on_input_change():
    st.session_state['vehicles'] = create_vehicles(num_vehicles=st.session_state.num_terminal_tractors,type="terminal_tractor")
    st.session_state['vehicle_markers'] = []
    for vehicle in st.session_state['vehicles']:
        st.session_state['vehicle_markers'].append(vehicle.marker)

def update_real_time_factor():
    vehicles = Vehicle.get_all_vehicles()
    for vehicle in vehicles:
        vehicle.update_instance_parameter('actual_speed',vehicle.average_speed*st.session_state['real_time_factor'])

def update_vehicle_properties():
    vehicles = Vehicle.get_all_vehicles() #TODO: currently updates all values for street robot, should be vehicle-type specific
    for vehicle in vehicles:
        vehicle.update_instance_parameter('average_speed',st.session_state.terminal_tractor_speed/3.6)
        vehicle.update_instance_parameter('actual_speed',vehicle.average_speed*st.session_state['real_time_factor'])
        vehicle.update_instance_parameter('load_time',st.session_state.terminal_tractor_load_time)    
        vehicle.update_instance_parameter('unload_time',st.session_state.terminal_tractor_unload_time)
        vehicle.update_instance_parameter('co2_emission', st.session_state.terminal_tractor_co2_emission)
        vehicle.update_instance_parameter('nox_emission', st.session_state.terminal_tractor_nox_emission)
        vehicle.update_instance_parameter('noise_pollution', st.session_state.terminal_tractor_noise_pollution)
        vehicle.update_instance_parameter('land_use', st.session_state.terminal_tractor_land_use)
        vehicle.update_instance_parameter('battery_capacity', st.session_state.terminal_tractor_battery_capacity)
        vehicle.update_instance_parameter('energy_consumption_moving', st.session_state.terminal_tractor_energy_consumption_moving)
        vehicle.update_instance_parameter('energy_consumption_idling', st.session_state.terminal_tractor_energy_consumption_idling)
        vehicle.update_instance_parameter('battery_threshold', st.session_state.terminal_tractor_battery_threshold)
        vehicle.update_instance_parameter('charge_speed', st.session_state.terminal_tractor_charge_speed)

# Side-bar settings
st.sidebar.markdown("## Inputs")

def delete_all_trips():
    # Classes to reset
    classes = [Trip, Actor, Action, Route, Location]

    # Reset classes
    for cls in classes:
        if cls == Location:
            # Only keep micro-hub
            cls.delete_all_customers()
        else:
            cls.delete_all_instances()

    # Enable input parameters
    st.session_state.disable_inputs = False

    # Remove all Destination markers from map
    st.session_state.destinations = []
    st.session_state.clicked_before_reset = st_data['last_object_clicked']

st.sidebar.button("Delete all trips?", on_click=delete_all_trips)

def add_new_delivery():
    if st_data['last_object_clicked']:

        # Check if user's last_click has already been clicked on
        filtered_list = [marker for marker in st.session_state['static_locations'] if marker.location[0] == st_data['last_object_clicked']['lat'] and marker.location[1] == st_data['last_object_clicked']['lng']]
        
        # If new click on a location, add it to trip list (but not a click on a vehicle)
        if filtered_list and 'tractor' not in st_data['last_object_clicked_popup'] and st_data['last_object_clicked'] != st.session_state['clicked_before_creating_trip']:
            
            # Get location
            location = Location.get_by_georeference([st_data['last_object_clicked']['lat'],st_data['last_object_clicked']['lng']])

            # Append Location to the to-be-created Trip (excluding first Location such as to be able to create a round-trip ending at start location)
            if location is not None:
                if len(st.session_state['create_trip']) == 0:
                    st.session_state['create_trip'].append(location)
                elif st.session_state['create_trip'][-1] != location:
                    st.session_state['create_trip'].append(location)
                    
    return st.session_state["static_locations"]

def create_map(markers,user_markers,microhubs,routes):
    global m
    m = folium.Map(location=st.session_state["center"], zoom_start=st.session_state["zoom"],width=1600)
    Fullscreen().add_to(m)
    # Vehicle Data
    fg = folium.FeatureGroup(name="Vehicles")
    for marker in markers:
        fg.add_child(marker)

    # Location Data
    fg2 = folium.FeatureGroup(name="UserMarkers")
    for marker in user_markers:
        fg2.add_child(marker)    

    # Microhub Data
    fg3 = folium.FeatureGroup(name="Microhubs")
    for hub in microhubs:
        fg3.add_child(hub)

    # Route data
    fg4 = folium.FeatureGroup(name='Routes')
    for route in routes:
        fg4.add_child(route)


    st_data = st_folium(
        m,
        center=st.session_state["center"],
        zoom=15,
        key="new",
        feature_group_to_add=[fg,fg2,fg3,fg4],
        height=400,
        width=1600,
    )      

    # Add layer control
    folium.LayerControl().add_to(m)

    return st_data

def color_change(val):
    color_map = {
        'draft': 'background-color: #EDD8AB',
        'requested': 'background-color: #ACE5EE',
        'confirmed': 'background-color: #EDC8AB',
        'in_transit': 'background-color: #ABEDD1',
    }
    # Return the color based on the value
    return color_map.get(val, '')  # Default color (no color)

def color_change_action(val):
    #TODO: Change colors
    "requested" "planned" "projected" "actual" "realized"
    color_map = {
        'requested': 'background-color: #ACE5EE',
        'planned': 'background-color: #EDC8AB',
        'projected': 'background-color: #ABEDD1',
        'actual': 'background-color: #ABEDD1',
        'realized': 'background-color: #ABEDD1',
    }
    # Return the color based on the value
    return color_map.get(val, '')  # Default color (no color)    

def create_new_trip():
    # Ensure that the last_clicked marker is not re-intialized when 'Delete All Trips' button is clicked
    if st.session_state.clicked_before_reset['lat'] != st_data['last_object_clicked']['lat'] and st.session_state.clicked_before_reset['lng'] != st_data['last_object_clicked']['lng']:
        
        # Reset latest click by user before reset
        st.session_state.clicked_before_reset = {'lat': 0.0, 'lng': 0.0}

        # Create a Location where user clicked (optional params: actors, actions, constraint)
       # location, location_marker = create_location(st_data['last_clicked']['lat'],st_data['last_clicked']['lng'],'customer')
        
        # Add to locations session state (= list of instances of Location Class)
      # st.session_state["locations"].append(location)

        # Add to destinations session state (= list of Folium Marker objects)
      #  st.session_state["destinations"].append(location_marker)  


        # Get all actors involved in this trip
        actors = []
        for location in st.session_state['create_trip']:
            # Add first actor of location to actors list
            actors.append(location.actors[0])

        # Create a Trip (optional params: vehicle and actions)
        trip = create_trip(actors)

        # Remember which markers belong to this trip (currently only one)
        #trip.marker = location.marker

        routes = []
        actions_to_add = []
        for idx, row in to_create_trip.iterrows():
            # Create a Route from origin to destination
            origin = row['from_location']
            destination = row['to_location']
            route_actors = [row['from_actor'],row['to_actor']]
            route = create_route(route_actors,st.session_state.graph, origin=origin, destination=destination)
            routes.append(route)

            # Add to routes session state (= list of instances of Route Class)
            st.session_state["routes"].append(route)

            # Actions to add:
            actions_to_add.append(
                {'sequence_nr': len(actions_to_add),
                 'type': 'move',
                 'origin': origin,
                 'destination': destination,
                 'route': route,
                 'trip': trip})

        # Create Actions for Trip
        if st.session_state["static_locations"]:
            for ac in actions_to_add:
                # Create actions (for now only 'move' action)
                action = create_action(ac['origin'],
                                        ac['destination'],
                                        sequence_nr=ac['sequence_nr'],
                                        route=ac['route'],
                                        trip=ac['trip'],
                                        actiontype=ac['type']
                                        )
            # Update sessions state of actions
            st.session_state["actions"] = Action.get_all_actions()

        else:
            raise Exception("No micro-hub available. Please check st.session_state.microhubs")
        
        # Remember last clicked location of this trip. Otherwise after refresh, a new trip is automatically created with this location as the first location.
        #TODO: suppose you want the next trip to start at the last location of the current trip. Then 'add_new_delivery' will not initiate a trip. hmmmm.
        st.session_state['clicked_before_creating_trip'] = {'lat': st.session_state['create_trip'][-1].georeference[0], 'lng': st.session_state['create_trip'][-1].georeference[1]}
        
        print(f"Overwriting session state: {st.session_state['clicked_before_creating_trip']}")
        
        # Reset list of locations
        st.session_state['create_trip'] = []
        
        # Remember last 
        

# Get data for Tables
trips = get_trips()
vehicles = get_vehicles()

def reset_trip():
    st.session_state.create_trip = []  

def get_currently_creating_trip():
    trip_list = []
    for i in range(len(st.session_state.create_trip) - 1):
        pair = {"from": st.session_state.create_trip[i].name,
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
    st.markdown("# Manual Mode")
    st.write(
        """Click map to add a delivery. Might take a bit to reflect your interaction with the map. Enjoy!"""
    )    
    # Create/update map
    st_data = create_map(st.session_state["vehicle_markers"],st.session_state["destinations"],st.session_state["static_locations"],st.session_state["polylines"])    
    
    # Divide page in two columns
    left, right = st.columns(2)
    
    with left:
        # At first render add all static locations
        if not st.session_state['static_locations']:
            # Create a Location for all static locations (optional params: actors, actions, constraint)
            locations = create_locations('locations.json')

            # Create an actor per set of locations belonging to same company
            if "CTT" in locations[0][0].name:
                previous_company = "CTT"
            elif "BOL" in locations[0][0].name:
                previous_company = "Bolk"
            elif "BLK" in locations[0][0].name:
                previous_company = "Bleckmann"
            elif "TBL" in locations[0][0].name:
                previous_company = "Timberland"

            # First actor
            actor = create_actor(locations[0][0],name=previous_company)

            for location in locations:
                # Add to locations session state (= list of instances of Location Class)
                st.session_state["locations"].append(location[0])

                # Add to static_locations session state (= list of Folium Marker objects)
                st.session_state["static_locations"].append(location[1])  

                # Create an actor per set of locations belonging to same company
                if "CTT" in location[0].name:
                    current_company = "CTT"
                elif "BOL" in location[0].name:
                    current_company = "Bolk"
                elif "BLK" in location[0].name:
                    current_company = "Bleckmann"
                elif "TBL" in location[0].name:
                    current_company = "Timberland"

                if current_company != previous_company:
                    actor = create_actor(location[0],name=current_company)
                    previous_company = current_company

                # Link location to actor
                location[0].actors = actor

                # Link actor to location
                actor[0].locations.append(location[0])

                
            # Create inital number of vehicles and remember list of Vehicle instances in session state
            st.session_state['vehicles'] = create_vehicles(st.session_state.num_terminal_tractors,
                                                           type="terminal_tractor",
                                                           average_speed=st.session_state.terminal_tractor_speed/3.6,
                                                           load_time=st.session_state.terminal_tractor_load_time,
                                                           unload_time=st.session_state.terminal_tractor_unload_time)
            st.session_state['vehicle_markers'] = []
            for vehicle in st.session_state['vehicles']:
                st.session_state['vehicle_markers'].append(vehicle.marker)

        if st.session_state['create_trip']:
            global to_create_trip
            # Show Create Trip table
            st.markdown('### Creating Trip')
            to_create_trip = get_currently_creating_trip()

            # Columns to hide
            if 'from_location' in to_create_trip.keys():
                columns_to_hide = ['from_location','to_location','from_actor','to_actor']
            else:
                columns_to_hide = []

            # Filter out the columns to hide
            filtered_trips = to_create_trip.drop(columns=columns_to_hide)

            st.data_editor(filtered_trips,
                        use_container_width=True)
            
            if st.session_state['create_trip']:
                st.button("Create Trip",on_click=create_new_trip)
                st.button("Reset Trip", type="primary",on_click=reset_trip)

        if not trips.empty:
            # Create Trip table filtered on 'draft'
            st.markdown("### To Be Planned Trips")

            filtered_df = trips[trips['status'].isin(['draft'])]
            
            # Columns to hide
            columns_to_hide = ['polyline','marker','progress','length']

            # Filter out the columns to hide
            filtered_trips = filtered_df.drop(columns=columns_to_hide)

            # Create editable trip table that allows users to assign vehicle to trip
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
                        disabled=['name','creation_date','status','from','to','id'],
                        hide_index=True,

                        use_container_width=True
            )

            # Assign vehicle to trip based on all edited rows of user (most probably one at the time)
            for row, vehicle in st.session_state.trip_edit['edited_rows'].items():
                # Try to assign vehicle to trip. Only 'draft' or 'requested' status can be assigned a vehicle, otherwise ValueError is raised. 
                success = Vehicle.get_by_vehicle_name(vehicle['vehicle']).assign_to_trip(Trip.get_by_id(edited_df.iloc[row]['id']))
        else:
            # Reset session state on disabling inputs
            st.session_state['disable_inputs'] = False

    with right:
        # Check if user clicked on map
        did_user_click = add_new_delivery()      

        if not trips.empty:
            st.markdown('''### All Trips''')
            # Get filters from user
            selected_options = st.multiselect("Filter trips based on status",
                                                options=['all','draft','requested','confirmed','in_transit','completed','cancelled','accepted','modified'],
                                                default=['all'])    
            
            # After first trip is initiated, disable the input section in sidebar
            st.session_state['disable_inputs'] = True

            # Filter trip data based on user input
            if 'all' not in selected_options:
                filtered_df = trips[trips['status'].isin(selected_options)]
            else:
                filtered_df = trips

            # Columns to hide
            columns_to_hide = ['polyline','marker']

            # Filter out the columns to hide
            filtered_trips = filtered_df.drop(columns=columns_to_hide)

            # Apply style to DataFrame
            styled_and_filtered_trips = filtered_trips.style.applymap(color_change,subset=['status'])
            
            # Create trip list
            trip_list = st.dataframe(
                styled_and_filtered_trips,
                key="data",
                on_select="rerun",
                selection_mode=["single-row"], #TODO: adjust to multi-row to show multiple routes?
                column_config={
                    "progress": st.column_config.ProgressColumn(
                        "progress",
                        help="The progress of the trip",
                        min_value=0,
                        max_value=100,
                    ),
                },
                use_container_width=True,
                hide_index=True,
                )
            
            # Get rows that user selected
            selected_rows = trip_list.selection
            st.session_state['selected_rows'] = selected_rows

            # Get polyline(s) of selected trip(s)
            st.session_state["polylines"] = []
            for row in st.session_state['selected_rows']['rows']:
                route = trips.iloc[row]['polyline']
                if route not in st.session_state["polylines"]:
                    st.session_state["polylines"].append(route)

                # Add Datatable to shows details of Trip
                trip = Trip.get_by_id(trips.iloc[row]['id'])
                st.write(f"Details of {trip.name}")
                actions = get_actions_of_trip(trip)
                styled_actions = actions.style.applymap(color_change_action,subset=['lifecycle'])
                action_list = st.dataframe(
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


    st.markdown('''## Detailed Trip View''')
    # Get names of all trips
    options = [trip.name for trip in Trip.get_all_trips()]

    # Get filters from user
    selected_trips = st.multiselect("Filter trips based on name",options=options)    

    # Reset polyline(s) of selected trip(s)
    st.session_state["polylines"] = []

    # Add Datatable to shows details of Trip
    selected_actions = pd.DataFrame()
    for trip_name in selected_trips:
        trip = Trip.get_by_name(trip_name)
        df_actions = get_actions_of_trip(trip)
        selected_actions = pd.concat([selected_actions,df_actions],ignore_index=True)

        # Show all polylines of the trip on the map
        for action in trip.get_actions():
            if action.action_type == 'move' and action.route.polyline not in st.session_state['polylines']:
                st.session_state["polylines"].append(action.route.polyline)

    if not selected_actions.empty:
        styled_actions = selected_actions.style.applymap(color_change_action,subset=['lifecycle'])
        action_list = st.dataframe(
            styled_actions,
            column_config=get_trip_details_table_config(),    
            use_container_width=True,
            hide_index=True,

        )

    # Check if vehicle should start a trip
    trips_with_status_requested = Trip.get_by_status('requested')
    start_trips(trips_with_status_requested)

    # Update vehicle positions
    trips_with_status_in_transit = Trip.get_by_status('in_transit')
    st.session_state['vehicle_markers'], st.session_state['destinations'] = update_vehicle_positions(trips_with_status_in_transit,st.session_state['vehicle_markers'],st.session_state['destinations'])

# Plot Gantt Chart of Vehicle Schedule
    if not trips.empty:
        st.markdown('''## Schedule''')
        st.write(get_gantt_chart(True))

        # Update statistics
        latest_vehicle_stats = update_statistics()
        if not latest_vehicle_stats.empty:
            st.markdown('''## Vehicle Raw Data''')

            # Columns to hide
            columns_to_hide = ['id','energy_consumption','co2_emission','nox_emission','noise_pollution','land_use']

            # Filter out the columns to hide
            latest_vehicle_stats = latest_vehicle_stats.drop(columns=columns_to_hide)    

            # Update utilization such as to display percentage between 0-100%
            latest_vehicle_stats['utilization'] = latest_vehicle_stats['utilization']*100

            st.dataframe(latest_vehicle_stats,
                        column_config=get_vehicle_data_table_config(),
                        hide_index=True
            )

            st.markdown('''## Vehicle Occupancy''')
            st.bar_chart(latest_vehicle_stats,
                        y=['move','idle','load','unload'],
                        y_label='Vehicle',
                        x='name',
                        x_label='Occupancy',
                        stack='normalize',
                        horizontal=True)

with tab2:
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('''## General''')
        st.number_input("Real-time factor", min_value=1,value=1,key='real_time_factor',on_change=update_real_time_factor,disabled=True)
    with col2:
        st.markdown('''## Vehicle''')
        use_terminal_tractors = st.toggle("Terminal Tractor",value=True)
        if use_terminal_tractors:
            slider_value = st.slider(
                'Number of Terminal Tractors',
                min_value=1,
                max_value=10,
                key='num_terminal_tractors',
                value=st.session_state.num_terminal_tractors,
                on_change=on_input_change,
                disabled=st.session_state.disable_inputs
                )  
            st.number_input("Speed (km/h)", value=st.session_state.terminal_tractor_speed, key='terminal_tractor_speed',min_value=5.0,max_value=45.0,on_change=update_vehicle_properties)
            st.number_input("Capacity per terminal tractor", value=st.session_state.terminal_tractor_capacity, key='terminal_tractor_capacity', disabled=True)
            use_loading_times = st.toggle("Use (un)loading times",value=True)
            if use_terminal_tractors and use_loading_times:
                st.markdown(':stopwatch: **Times**')
                st.number_input("Load Time (s)", value=st.session_state.terminal_tractor_load_time,key='terminal_tractor_load_time', on_change=update_vehicle_properties)    
                st.number_input("Unload Time (s)", value=st.session_state.terminal_tractor_unload_time,key='terminal_tractor_unload_time',on_change=update_vehicle_properties)
            else:
                st.session_state.terminal_tractor_load_time = 0
                st.session_state.terminal_tractor_unload_time = 0
                update_vehicle_properties()
            use_emissions = st.toggle("Use emissions", value=True)
            if use_terminal_tractors and use_emissions:
                st.markdown(':smoking: **Emissions**')
                st.number_input("CO2 Emission (g/km)", value=st.session_state.terminal_tractor_co2_emission,key='terminal_tractor_co2_emission',on_change=update_vehicle_properties)
                st.number_input("NOx Emission (g/km)", value=st.session_state.terminal_tractor_nox_emission,key='terminal_tractor_nox_emission',on_change=update_vehicle_properties)
                st.number_input("Noise Pollution (dB)", value=st.session_state.terminal_tractor_noise_pollution,key='terminal_tractor_noise_pollution',on_change=update_vehicle_properties)
                st.number_input("Land Use (m3)", value=st.session_state.terminal_tractor_land_use,key='terminal_tractor_land_use',on_change=update_vehicle_properties)
            else:
                st.session_state.terminal_tractor_co2_emission = 0
                st.session_state.terminal_tractor_nox_emission = 0
                st.session_state.terminal_tractor_noise_pollution = 0
                st.session_state.terminal_tractor_land_use = 0
                update_vehicle_properties()

            use_battery = st.toggle("Use battery", value=False)
            if use_terminal_tractors and use_battery:
                st.markdown(':battery: **Battery**')
                st.number_input("Battery Capacity (kWh)", value=st.session_state.terminal_tractor_battery_capacity,key='terminal_tractor_battery_capacity',on_change=update_vehicle_properties)
                st.number_input("Energy Consumption - Driving (kW)", value=st.session_state.energy_consumption_moving,key='energy_consumption_moving',on_change=update_vehicle_properties)
                st.number_input("Energy Consumption - Idling (kW)", value=st.session_state.energy_consumption_idling,key='energy_consumption_idling',on_change=update_vehicle_properties)
                st.number_input("Low Battery Threshold (kWh)", value=st.session_state.terminal_tractor_battery_threshold,key='terminal_tractor_battery_threshold',on_change=update_vehicle_properties)
                st.number_input("Charge Speed (kW)", value=st.session_state.terminal_tractor_charge_speed,key='terminal_tractor_charge_speed',on_change=update_vehicle_properties)
            else:
                st.session_state.terminal_tractor_battery_capacity = 0
                st.session_state.energy_consumption_moving = 0
                st.session_state.energy_consumption_idling = 0
                st.session_state.terminal_tractor_battery_threshold = 0
                st.session_state.terminal_tractor_charge_speed = 0
                update_vehicle_properties()

        else:
            st.session_state.num_terminal_tractors = 0

    with col3:
        st.markdown('''## Trip''')             
auto_refresh = st.sidebar.checkbox('Auto Refresh?', st.session_state.auto_refresh)

if auto_refresh:
    number = st.sidebar.number_input('Refresh rate in seconds', value=st.session_state.sleep_time)
    st.session_state.sleep_time = number


if auto_refresh:
    st.session_state.do_refresh = False
    time.sleep(st.session_state.sleep_time)
    st.session_state.do_refresh = True
    st.rerun()    

# CODE GRAVEYARD