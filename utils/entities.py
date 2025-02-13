from utils.classes import Location, Trip, Actor, Route, Action, Vehicle
from utils.osmnx import get_shortest_path, get_route_length, get_coordinates, get_interpolated_position
from utils.osm import create_custom_icon
from folium import Marker, PolyLine, CircleMarker, CustomIcon
import pandas as pd
import random
from datetime import datetime
import json

def create_trip(actors,vehicle=None):
    """
    Create an instance of the Trip Class.

    Parameters:
    - actors (list[Actor]): List of Actors connected to this trip. 
    - vehicle (Vehicle): The vehicle assigned to this trip. Default is None.

    Returns:
    - Trip: A new instance of the Trip Class. 
    """    

    # Create instance of Trip Class
    trip = Trip(name=f"Trip {Trip.get_total_trips()}",actors=actors,vehicle=vehicle) #status defaults to 'draft'

    return trip

def create_actor(location,name=f"Actor {Actor.get_total_actors()}"):

    # Create instance of Actor Class 
    actor = Actor(location,name=name)

    # Link Actor to Location
    location.actors = [actor]

    # Link Location to Actor (NOTE: Currently one Location per Actor)
    actor.locations = [location]

    return [actor]

def create_route(actors,graph,origin,destination):
    # Get shortest path between origin and destination based on Dijkstra (returns list of node IDs)
    # Optional parameter 'weight', default to 'travel_time'.
    nodes = get_shortest_path(graph,origin.georeference,destination.georeference)

    # Get length of route
    length_in_meters = get_route_length(graph,nodes)

    # Get coordinates of nodes in route
    coordinates = get_coordinates(graph,nodes)

    # Create Polyline between origin and destination
    line = PolyLine(
            locations=coordinates,
            color="#DC143C",
            weight=5,
            tooltip=f"{origin.name} to {destination.name}") 
    
    # Create instance of Route Class
    route = Route(name=f"{origin.name} to {destination.name}",
                  georeference=coordinates,
                  actors=actors,
                  length=length_in_meters,
                  nodes=nodes,
                  polyline=line,
                  coordinates=coordinates)
    
    return route

def create_action(origin=None,destination=None,duration=None,location=None,sequence_nr=None,route=None,trip=None,constraint=None, action_type='move'):
    '''
    Action 0: from micro-hub to customer
    Action 1: from customer to micro-hub
    '''

    # Create 'move' action from micro-hub to customer
    action = Action(sequence_nr=sequence_nr,
                    name=f"Action {Action.get_total_actions()}",
                    action_type=action_type,
                    _from=origin,
                    _to=destination,
                    location=location,
                    route=route,
                    trip=trip,
                    duration=duration,
                    constraint=constraint)
    
    # Add action to trip
    trip.add_action(action)

    return action

def create_location(lat: float, lng: float, type: str,actors=None,actions=None,constraint=None):
    # Create instance of Location Class
    location = Location(
        georeference=[lat,lng],
        type=type,
        name=f"Location {Location.get_total_locations()}",
        actors=actors,
        actions=actions,
        constraint=constraint)

    # Create custom icon
    if type == 'customer':
        custom_icon = create_custom_icon(icon='home',color='blue')
    elif type == 'warehouse':
        custom_icon = create_custom_icon(icon='warehouse',color='green')
    else:
        custom_icon = create_custom_icon()

    location_marker = Marker(
        location=location.georeference,
        popup=f"{location.name} \nid: {location.id} \nCreated on: {location.creation_date}",
        icon=custom_icon
        )
    
    # Link Location to Folium Marker
    location.marker = location_marker  

    return location, location_marker

def create_vehicles(num_vehicles, type, average_speed=(15.0/3.6), load_time=0, unload_time=0, load_capacities=1):
    if type == 'terminal_tractor':
        # Get the number of already initiated terminal tractors
        num_terminal_tractors = len(Vehicle.get_by_type(vehicle_type="terminal_tractor"))

        if num_terminal_tractors < num_vehicles:
            for i in range(num_vehicles - num_terminal_tractors):
                # Initialize Terminal Tractor at an appropriate Tractor Parking

                # Get all Tractor Parkings
                tractor_parkings = Location.get_by_type('tractor_parking')

                # Create a custom icon
                icon_path = 'images/terminal_tractor.png'
                icon_width = 50
                custom_icon = CustomIcon(icon_image=icon_path, icon_size=(icon_width, icon_width/2.3))
                
                # Create Marker using the next available tractor parking
                # Updated index: num_terminal_tractors + i ensures that if there are zero tractors,
                # the first element (index 0) is used.
                vehicle_marker = Marker(
                    icon=custom_icon,
                    location=tractor_parkings[num_terminal_tractors + i].georeference,
                    popup=f"{type} {Vehicle.get_total_vehicles()}",
                )               

                # Create instance of Vehicle class
                Vehicle(name=f"{type} {Vehicle.get_total_vehicles()}",
                        vehicle_type=type,
                        marker=vehicle_marker,
                        average_speed=average_speed)
        elif num_terminal_tractors > num_vehicles:
            response = Vehicle.delete_last_x(num_terminal_tractors - num_vehicles)
            if response:
                print(f"Deleted {num_terminal_tractors - num_vehicles} {type}")
            else:
                print(f"Did not delete {type}")
        else:
            # No changes in number of terminal tractors
            pass

        return Vehicle.get_all_vehicles()
    
def get_trips(filter=None):
    #TODO: implement filter (e.g., based on status of trip)
    trip_list = []
    for trip in Trip.get_all_trips():
        if trip.vehicle is not None:
            vehicle = trip.vehicle.name
        else:
            vehicle = trip.vehicle

        # Get length of all 'move' actions
        length = 0
        for action in trip.actions:
            if action.action_type == 'move':
                length += action.route.length

        trip_dict = {
            "name": trip.name,
            "creation_date": trip.creation_date,
            "status": trip.status,
            "from": [trip.actions[0]._from.name],
            "to": [trip.actions[0]._to.name],
            "vehicle": vehicle,
            "length": length,
            "progress": trip.progress,
            "id": trip.id,
            "polyline": trip.actions[0].route.polyline, #Hardcode
            "marker" : trip.marker,
        }
        # Add dictionary to list
        trip_list.append(trip_dict)

    return pd.DataFrame(trip_list)

def get_vehicles(filter=None):
    #TODO: implement filter (e.g., based on status of vehicle)
    vehicle_list = []
    for vehicle in Vehicle.get_all_vehicles():
        vehicle_dict = {
            "id": vehicle.id,
            "name": vehicle.name,
            "date": vehicle.creation_date,
            "type":vehicle.vehicle_type,
        }
        vehicle_list.append(vehicle_dict)
    return pd.DataFrame(vehicle_list)

def get_actions_of_trip(trip,filter=None):
    action_list = []
    for action in trip.get_actions():
        if action.action_type == 'load' or action.action_type == 'unload':
            _from = action.location.name
            _to = action.location.name
            length = None
        elif action.action_type == 'move':
            _from = action._from.name
            _to = action._to.name
            length = action.route.length
        action_dict = {
            "name": trip.name,         
            "sequence_nr": action.sequence_nr,
            "lifecycle": action.lifecycle,
            "action_type": action.action_type,
            "from": [_from],
            "to": [_to],
            "length": length,
            "start_time": action.start_time,
            "progress": action.progress,

        }
        action_list.append(action_dict)
    return pd.DataFrame(action_list)


def start_trips(trips_with_status_requested):
    if trips_with_status_requested is not None:
        for trip in trips_with_status_requested:
                # Check of a vehicle is assigned to trip
                if trip.vehicle is not None:
                    # Get start time of trip in schedule of vehicle
                    start_time = trip.vehicle.get_start_time_trip(trip.id)

                    if datetime.now() > pd.to_datetime(start_time) and trip.vehicle.current_trip is None:
                        # Start trip
                        trip.update_instance_parameter('status','in_transit')

                        # Set vehicle to current trip
                        trip.vehicle.update_instance_parameter('current_trip',trip)

                        # Set vehicle to execute first action of trip
                        trip.vehicle.update_instance_parameter('current_action',0)

                        # Update first Action 
                        trip.actions[0].update_instance_parameter('start_time',datetime.now())
                        trip.actions[0].update_instance_parameter('lifecycle','actual')

                        # Update status of vehicle
                        trip.vehicle.update_instance_parameter('status',trip.actions[0].action_type)
                        trip.vehicle.update_instance_parameter('entries',trip.vehicle.entries + 1) #TODO: change to actual number of cargo going into vehicle  (and only if succesfull)

def update_vehicle_positions(trips_with_status_in_transit,vehicle_markers,destination_markers):
    if trips_with_status_in_transit is not None:
        for trip in trips_with_status_in_transit:
            if trip.actions[trip.vehicle.current_action].progress < 100:
                # Calculate the elapsed time
                elapsed_time = datetime.now() - trip.actions[0].start_time

                # Convert elapsed time to seconds
                elapsed_seconds = elapsed_time.total_seconds()

                # Calculate the expected duration of the trip in seconds
                expected_duration = 0
                for action in trip.actions:
                    if action.action_type == 'load':
                        expected_duration += action.duration
                    elif action.action_type == 'unload':
                        expected_duration += action.duration
                    elif action.action_type == 'move':
                        expected_duration += action.route.length/trip.vehicle.actual_speed


                # Calculate progress as a fraction of the TOTAL TRIP (between 0 and 1)
                #progress_fraction = (elapsed_seconds * trip.vehicle.actual_speed) / trip.get_total_route_length()
                progress_fraction = (elapsed_seconds / expected_duration)
                # Ensure the progress is between 0 and 1
                progress_fraction = min(max(progress_fraction, 0), 1)

                # Scale progress to be between 0 and 100 and convert to an integer
                progress_trip = int(progress_fraction * 100)

                # Update progress of trip
                trip.update_instance_parameter('progress',progress_trip)


                # Calculate progress of the CURRENT ACTION as a fraction

                # Calculate the elapsed time since start of current action
                elapsed_time = datetime.now() - trip.actions[trip.vehicle.current_action].start_time

                # Convert elapsed time to seconds
                elapsed_seconds = elapsed_time.total_seconds()

                if trip.actions[trip.vehicle.current_action].duration == 0:
                    progress_fraction = 1 #avoid division-by-zero error
                elif trip.actions[trip.vehicle.current_action].action_type == 'load':
                    progress_fraction = (elapsed_seconds / trip.actions[trip.vehicle.current_action].duration)
                elif trip.actions[trip.vehicle.current_action].action_type == 'unload':
                    progress_fraction = (elapsed_seconds / trip.actions[trip.vehicle.current_action].duration)
                elif trip.actions[trip.vehicle.current_action].action_type == 'move':
                    # Calculate progress as a fraction of the action (between 0 and 1)
                    progress_fraction = (elapsed_seconds * trip.vehicle.actual_speed) / trip.actions[trip.vehicle.current_action].route.length

                # Ensure the progress is between 0 and 1
                progress_fraction = min(max(progress_fraction, 0), 1)

                # Scale progress to be between 0 and 100 and convert to an integer
                progress_action = int(progress_fraction * 100)

                trip.actions[trip.vehicle.current_action].update_instance_parameter('progress',progress_action)
                
                # Calculate new position based on progress
                if trip.actions[trip.vehicle.current_action].action_type == 'move':
                    position = get_interpolated_position(trip.actions[trip.vehicle.current_action].route.coordinates, progress_action)

                    # Remove old vehicle marker
                    if trip.vehicle.marker in vehicle_markers:
                        vehicle_markers.remove(trip.vehicle.marker)

                    # Create new vehicle marker with updated position
                    # Create a custom icon
                        icon_path = 'images/terminal_tractor.png'
                        icon_width = 50
                        custom_icon = CustomIcon(icon_image=icon_path, icon_size=(icon_width, icon_width/2.3))
                        # Create Marker
                        vehicle_marker = Marker(
                            icon=custom_icon,
                            location=position,
                            popup=f"{trip.vehicle.name} - {progress_trip}",
                        )        
                    # Append new vehicle marker to session state
                    vehicle_markers.append(vehicle_marker)

                    # Update marker in vehicle instance
                    trip.vehicle.update_instance_parameter('marker',vehicle_marker)
            else:
                # Action is completed
                trip.actions[trip.vehicle.current_action].update_instance_parameter('lifecycle','completed')
                trip.actions[trip.vehicle.current_action].update_instance_parameter('end_time',datetime.now())

                # Update number of exits for 'unload' action:
                if trip.actions[trip.vehicle.current_action].action_type == 'unload':
                    trip.vehicle.update_instance_parameter('exits',trip.vehicle.exits + 1) #TODO: change to actual number of cargo exiting into vehicle (and only if succesfull)

                # Set vehicle to execute next action of trip
                if trip.vehicle.current_action < len(trip.actions)-1:
                    trip.vehicle.update_instance_parameter('current_action',trip.vehicle.current_action + 1)
                    trip.actions[trip.vehicle.current_action].update_instance_parameter('lifecycle','actual')
                    trip.actions[trip.vehicle.current_action].update_instance_parameter('start_time',datetime.now())
                    
                    # Update status of vehicle to action_type of current action
                    trip.vehicle.update_instance_parameter('status',trip.actions[trip.vehicle.current_action].action_type)
                    
                else:
                    # Trip is completed
                    trip.update_instance_parameter('status','completed')

                    # Set vehicle's current trip and action to None
                    trip.vehicle.update_instance_parameter('current_trip',None)
                    trip.vehicle.update_instance_parameter('current_action',None)

                    # Update status of vehicle
                    trip.vehicle.update_instance_parameter('status','idle')

                    # Remove marker after trip is completed
                    if trip.marker in destination_markers:
                        destination_markers.remove(trip.marker)
                        
    return vehicle_markers,destination_markers

def get_location_type(location_name):
    if 'Entrance' in location_name:
        return 'entrance'
    elif 'Tractor Parking' in location_name:
        return 'tractor_parking'
    elif 'Semitrailer Parking' in location_name:
        return 'semi_trailer_parking'
    elif 'Loading Lane' in location_name:
        return 'loading_lane'
    elif 'Exit' in location_name:
        return 'exit'
    elif 'Temporary  Parking ' in location_name:
        return 'temporary_parking'
    elif 'Docking Gate' in location_name:
        return 'dock'

def create_locations(file_name,filter=None):
    all_locations = []
    with open(file_name, "r") as jsonfile:
        locations = json.load(jsonfile) # Reading the file
        for key in locations.keys():
            # Create locations
            for location in locations[key]:
                name = location['Sub-Location']
                identifier = location['Identifier ']
                lat = location['Latitude ']
                lng = location['Longitude ']

                # Get type of location based on name
                type = get_location_type(name)
                
                # Create instance of Location Class
                loc = Location(
                    georeference=[lat,lng],
                    location_type=type,
                    name=identifier,
                    actors=None,
                    actions=None,
                    constraint=None)
                
                
                if type == 'entrance':
                    custom_icon = create_custom_icon(icon='door-open',color='orange')
                elif type == 'tractor_parking':
                    custom_icon = create_custom_icon(icon='square-parking',color='lightred')
                elif type == 'semi_trailer_parking':
                    custom_icon = create_custom_icon(icon='trailer',color='purple')
                elif type == 'loading_lane':
                    custom_icon = create_custom_icon(icon='grip-lines-vertical',color='green')
                elif type == 'exit':
                    custom_icon = create_custom_icon(icon='door-closed',color='gray')
                elif type == 'temporary_parking':
                    custom_icon = create_custom_icon(icon='home',color='beige')
                elif type == 'dock':
                    custom_icon = create_custom_icon(icon='truck-ramp-box',color='cadetblue')
                else:
                    custom_icon = create_custom_icon()

                location_marker = Marker(
                    location=loc.georeference,
                    popup = f"<b>Name:</b> {name}<br><b>ID:</b> {loc.name}<br><b>Georeference:</b> [{lat:.6f}, {lng:.6f}]",
                    icon=custom_icon
                    )
                
                # Link Location to Folium Marker
                loc.marker = location_marker  

                all_locations.append(tuple([loc,location_marker]))
        jsonfile.close()
    return all_locations