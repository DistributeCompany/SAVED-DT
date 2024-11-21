import os
import pandas as pd
import json

# Define base directory dynamically
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Construct input path and output directory
input_excel_path = os.path.join(base_dir, 'static', 'trip_raw_data.xlsx')
output_dir = os.path.join(base_dir, 'static', 'generated_trips')

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# Load the Excel file
trips_df = pd.read_excel(input_excel_path, sheet_name='Trips')
locations_df = pd.read_excel(input_excel_path, sheet_name='Locations')
transport_equipment_df = pd.read_excel(input_excel_path, sheet_name='TransportEquipment')

# Function to find location details by ID
def get_location_details(location_id):
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

# Function to get transport equipment details
def get_transport_equipment_details(equipment_id):
    equipment = transport_equipment_df[transport_equipment_df['EquipmentID'] == equipment_id]
    if not equipment.empty:
        equipment = equipment.iloc[0]
        return {
            "id": equipment['EquipmentID'],
            "description": equipment['Description'],
            "licensePlate": equipment['LicensePlate']
        }
    return None

# Iterate over unique TripIDs
unique_trip_ids = trips_df['TripID'].unique()

for trip_id in unique_trip_ids:
    # Filter data for the current trip
    trip_data = trips_df[trips_df['TripID'] == trip_id]
    
    # Initialize JSON structure
    trip_json = {
        "id": trip_id,
        "name": trip_data.iloc[0]['TripName'],
        "status": "planned",
        "transportMode": "road",
        "vehicle": {
            "entity": {
                "id": trip_data.iloc[0]['VehicleID'],
                "name": trip_data.iloc[0]['VehicleName'],
                "entityType": "vehicle"
            },
            "associationType": "inline"
        },
        "actors": [],
        "actions": []
    }
    
    # Populate actors
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
        # Add 'from' and 'to' locations if applicable
        if pd.notna(action['FromLocationID']):
            action_data['entity']['from'] = {
                "entity": get_location_details(action['FromLocationID']),
                "associationType": "inline"
            }
        if pd.notna(action['ToLocationID']):
            action_data['entity']['to'] = {
                "entity": get_location_details(action['ToLocationID']),
                "associationType": "inline"
            }
        # Add transport equipment if applicable
        if pd.notna(action['TransportEquipmentID']):
            action_data['entity']['transportEquipment'] = {
                "entity": get_transport_equipment_details(action['TransportEquipmentID']),
                "associationType": "inline"
            }
        # Add constraints if applicable
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
    
    # Write JSON file for the current trip
    output_file_path = os.path.join(output_dir, f"{trip_id}.json")
    with open(output_file_path, 'w') as f:
        json.dump(trip_json, f, indent=4)

    print(f"Generated JSON for TripID {trip_id} at: {output_file_path}")
