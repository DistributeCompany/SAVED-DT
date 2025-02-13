"""
Stand-alone module for manually creating OTM-based messages based on Excel input. 

The Excel input can be found in /static/trip_raw_data.xlsx

The generated JSON messages are outputted to /example_otm_messages/generated_trips
"""

import os
import json
import pandas as pd
from typing import Optional, Dict, Any
from datetime import datetime

def get_base_dir() -> str:
    """
    Get the base directory of the project.

    Returns:
        str: The base directory.
    """
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_excel_data(base_dir: str) -> Dict[str, pd.DataFrame]:
    """
    Load trip, location, and transport equipment data from an Excel file.

    Parameters:
        base_dir (str): The base directory of the project.

    Returns:
        dict: A dictionary containing the DataFrames for trips, locations, and transport equipment.
    """
    input_excel_path = os.path.join(base_dir, 'static', 'trip_raw_data.xlsx')
    trips_df = pd.read_excel(input_excel_path, sheet_name='Trips')
    locations_df = pd.read_excel(input_excel_path, sheet_name='Locations')
    transport_equipment_df = pd.read_excel(input_excel_path, sheet_name='TransportEquipment')
    return {
        'trips': trips_df,
        'locations': locations_df,
        'transport_equipment': transport_equipment_df
    }

def ensure_output_directory(base_dir: str) -> str:
    """
    Ensure that the output directory exists.

    Parameters:
        base_dir (str): The base directory of the project.

    Returns:
        str: The path to the output directory.
    """
    output_dir = os.path.join(base_dir, 'example_otm_messages', 'generated_trips')
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

def get_location_details(location_id: Any, locations_df: pd.DataFrame) -> Optional[Dict[str, Any]]:
    """
    Retrieve location details from the locations DataFrame by location ID.

    Parameters:
        location_id (Any): The location ID to search for.
        locations_df (pd.DataFrame): The DataFrame containing location data.

    Returns:
        dict or None: A dictionary with location details if found; otherwise, None.
    """
    location = locations_df[locations_df['LocationID'] == location_id]
    if not location.empty:
        location = location.iloc[0]
        return {
            "id": location['LocationID'],
            "name": location['LocationName'],
            "geoReference": {
                "lat": location['Latitude'],
                "lon": location['Longitude'],
                "type": "latLonPointGeoReference"
            }
        }
    return None

def get_transport_equipment_details(equipment_id: Any, transport_equipment_df: pd.DataFrame) -> Optional[Dict[str, Any]]:
    """
    Retrieve transport equipment details from the DataFrame by equipment ID.

    Parameters:
        equipment_id (Any): The equipment ID to search for.
        transport_equipment_df (pd.DataFrame): The DataFrame containing transport equipment data.

    Returns:
        dict or None: A dictionary with equipment details if found; otherwise, None.
    """
    equipment = transport_equipment_df[transport_equipment_df['EquipmentID'] == equipment_id]
    if not equipment.empty:
        equipment = equipment.iloc[0]
        return {
            "id": equipment['EquipmentID'],
            "description": equipment['Description'],
            "licensePlate": equipment['LicensePlate']
        }
    return None

def generate_trip_json(
    trip_id: Any,
    trips_df: pd.DataFrame,
    locations_df: pd.DataFrame,
    transport_equipment_df: pd.DataFrame
) -> Dict[str, Any]:
    """
    Generate a JSON structure for a given trip.

    Parameters:
        trip_id (Any): The trip ID.
        trips_df (pd.DataFrame): The DataFrame containing trip data.
        locations_df (pd.DataFrame): The DataFrame containing location data.
        transport_equipment_df (pd.DataFrame): The DataFrame containing transport equipment data.

    Returns:
        dict: A dictionary representing the trip in JSON format.
    """
    trip_data = trips_df[trips_df['TripID'] == trip_id]
    if trip_data.empty:
        raise ValueError(f"No data found for TripID {trip_id}")
    
    trip_row = trip_data.iloc[0]
    trip_json = {
        "id": trip_id,
        "name": trip_row['TripName'],
        "status": "planned",
        "transportMode": "road",
        "vehicle": {
            "entity": {
                "id": trip_row['VehicleID'],
                "name": trip_row['VehicleName'],
                "entityType": "vehicle"
            },
            "associationType": "inline"
        },
        "actors": [],
        "actions": []
    }
    
    # Populate actors by dropping duplicates
    actors = trip_data[['ActorID', 'ActorName', 'Role']].drop_duplicates()
    for _, actor in actors.iterrows():
        if pd.notna(actor['ActorID']):
            trip_json['actors'].append({
                "entity": {
                    "id": actor['ActorID'],
                    "name": actor['ActorName']
                },
                "roles": [actor['Role']],
                "associationType": "inline"
            })
    
    # Populate actions
    for _, action in trip_data.iterrows():
        action_data = {
            "entity": {
                "id": action['ActionID'],
                "name": action['ActionName'],
                "lifecycle": "planned",
                "sequenceNr": action['SequenceNumber'],
                "actionType": action['ActionType']
            },
            "associationType": "inline"
        }
        if pd.notna(action['FromLocationID']):
            action_data['entity']['from'] = {
                "entity": get_location_details(action['FromLocationID'], locations_df),
                "associationType": "inline"
            }
        if pd.notna(action['ToLocationID']):
            action_data['entity']['to'] = {
                "entity": get_location_details(action['ToLocationID'], locations_df),
                "associationType": "inline"
            }
        if pd.notna(action['TransportEquipmentID']):
            action_data['entity']['transportEquipment'] = {
                "entity": get_transport_equipment_details(action['TransportEquipmentID'], transport_equipment_df),
                "associationType": "inline"
            }
        if pd.notna(action['ConstraintStartTime']) and pd.notna(action['ConstraintEndTime']):
            action_data['entity']['constraint'] = {
                "id": action['ConstraintID'],
                "name": action['ConstraintName'] if pd.notna(action['ConstraintName']) else "",
                "value": {
                    "startTime": action['ConstraintStartTime'],
                    "endTime": action['ConstraintEndTime'],
                    "type": "timeWindowConstraint"
                },
                "enforceability": "preference"
            }
        trip_json['actions'].append(action_data)
    
    return trip_json

def main() -> None:
    """
    Main function to generate JSON files for each trip.
    """
    base_dir = get_base_dir()
    data = load_excel_data(base_dir)
    trips_df = data['trips']
    locations_df = data['locations']
    transport_equipment_df = data['transport_equipment']
    
    output_dir = ensure_output_directory(base_dir)
    unique_trip_ids = trips_df['TripID'].unique()
    
    for trip_id in unique_trip_ids:
        trip_json = generate_trip_json(trip_id, trips_df, locations_df, transport_equipment_df)
        output_file_path = os.path.join(output_dir, f"{trip_id}.json")
        with open(output_file_path, 'w', encoding='utf-8') as f:
            json.dump(trip_json, f, indent=4)
        print(f"Generated JSON for TripID {trip_id} at: {output_file_path}")

if __name__ == '__main__':
    main()
