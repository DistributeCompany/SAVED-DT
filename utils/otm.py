import pandas as pd
import json
import os

# Define paths
base_dir = os.path.abspath(os.path.join(__file__, "../../"))  # Navigate one level up from current script location
input_excel_path = os.path.join(base_dir, 'static', 'trip_raw_data.xlsx')
output_json_path = os.path.join(base_dir, 'static', 'generated_trip.json')

# Load the Excel file
trips_df = pd.read_excel(input_excel_path , sheet_name='Trips')
locations_df = pd.read_excel(input_excel_path , sheet_name='Locations')
transport_equipment_df = pd.read_excel(input_excel_path , sheet_name='TransportEquipment')

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

# Initialize JSON structure
trip_json = {
    "id": trips_df.iloc[0]['TripID'],
    "name": trips_df.iloc[0]['TripName'],
    "status": "planned",
    "transportMode": "road",
    "vehicle": {
        "entity": {
            "id": trips_df.iloc[0]['VehicleID'],
            "name": trips_df.iloc[0]['VehicleName'],
            "entityType": "vehicle"
        },
        "associationType": "inline"
    },
    "actors": [],
    "actions": []
}

# Populate actors
actors = trips_df[['ActorID', 'ActorName', 'Role']].drop_duplicates()
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
for _, action in trips_df.iterrows():
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
    # Add consignment if applicable
    if pd.notna(action['ConsignmentID']):
        action_data['entity']['consignment'] = {
            "entity": {
              "id": action['ConsignmentID'],
              "name": "Container with goods"
            },
            "associationType": "inline"
        }
    # Add constraints if applicable
    if pd.notna(action['ConstraintStartTime']) and pd.notna(action['ConstraintEndTime']):
        action_data['entity']['constraint'] = {
            "id": action['ConstraintID'],
            "name": action['ConstraintName'],
            "value": {
                "startTime": action['ConstraintStartTime'],
                "endTime": action['ConstraintEndTime'],
                "type": "timeWindowConstraint"
            },
            "enforceability": action['Enforceability'],
        }
    trip_json['actions'].append(action_data)

# Write the JSON output
with open(output_json_path, 'w') as f:
    json.dump(trip_json, f, indent=4)

print(f"JSON file has been created: {output_json_path}")
