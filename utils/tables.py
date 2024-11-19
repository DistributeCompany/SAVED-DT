import streamlit as st

def get_trip_details_table_config():
    column_config = {
                    "name": st.column_config.TextColumn(
                    "Name",
                    help="The name of the trip.",
                    ),
                    "sequence_nr": st.column_config.NumberColumn(
                    "Action Number",
                    help="The number indicating the sequence of the actions of this trip.",
                    min_value=0,
                    format="%d",
                ),
                    "lifecyle": st.column_config.TextColumn(
                    "Lifecycle",
                    help="The lifecyle of the action.",
                    ),     
                    "action_type": st.column_config.TextColumn(
                    "Type of Action",
                    help="The type of action.",
                    ),        
                    "from": st.column_config.ListColumn(
                    "Origin",
                    help="The origin of this action.",
                    ),  
                    "to": st.column_config.ListColumn(
                    "Destination",
                    help="The destination of this action. If the action takes place at a single location. Origin = Destination.",
                    ),      
                    "length": st.column_config.NumberColumn(
                    "Length",
                    help="The length of the route between origin and destination or None is irrelevant.",
                    format="%.2f",
                    ),        
                    "start_time": st.column_config.DatetimeColumn(
                    "Start",
                    help="The time the action started.",
                    disabled=True,
                    format="HH:mm:ss",
                    ),                                                                                                           
                    "progress": st.column_config.ProgressColumn(
                        "Progress",
                        help="The progress of the action",
                        min_value=0,
                        max_value=100,
                    ),                         


            }

    return column_config
def get_vehicle_data_table_config():
    column_config={
                    "timestamp": st.column_config.DatetimeColumn(
                    "Last Update",
                    help="The time the data was last updated.",
                    disabled=True,
                    format="HH:mm:ss",
                    ),                         
                    "name": st.column_config.TextColumn(
                    "Vehicle",
                    help="The name of the vehicle",
                    ),
                    "time_in_system": st.column_config.NumberColumn(
                        "Time in System (s)",
                        help="The total time the vehicle has been in the system.",
                        min_value=0,
                        format="%d",
                    ),
                    "move": st.column_config.NumberColumn(
                        "Moving (s)",
                        help="The total time the vehicle has been moving.",
                        min_value=0,
                        format="%d",
                    ),
                    "wait": st.column_config.NumberColumn(
                        "Waiting (s)",
                        help="The total time the vehicle has been waiting.",
                        min_value=0,
                        format="%d",
                    ),
                    "load": st.column_config.NumberColumn(
                        "Loading (s)",
                        help="The total time the vehicle has been loading.",
                        min_value=0,
                        format="%d",
                    ),
                    "unload": st.column_config.NumberColumn(
                        "Unloading (s)",
                        help="The total time the vehicle has been unloading.",
                        min_value=0,
                        format="%d",
                    ),      
                    "idle": st.column_config.NumberColumn(
                        "Idling (s)",
                        help="The total time the vehicle has been idling.",
                        min_value=0,
                        format="%d",
                    ),      
                    "charging": st.column_config.NumberColumn(
                        "Charging (s)",
                        help="The total time the vehicle has been charging.",
                        min_value=0,
                        format="%d",
                    ),           
                    "empty_driving": st.column_config.NumberColumn(
                        "Driving Empty (s)",
                        help="The total time the vehicle has driven completely empty.",
                        min_value=0,
                        format="%d",
                    ),    
                    "full_driving": st.column_config.NumberColumn(
                        "Driving Full (s)",
                        help="The total time the vehicle has driven completely full.",
                        min_value=0,
                        format="%d",
                    ),                                
                    "utilization": st.column_config.NumberColumn(
                        "Utilization",
                        help="The utilization of the vehicle measured in percentage of time the vehicle is moving and either partially or fully loaded. Also see tab 'More Information'.",
                        min_value=0,
                        format="%.2f%%",
                    ),    
                    "travel_distance": st.column_config.NumberColumn(
                        "Travelled distance (m)",
                        help="The total travelled distance in meters.",
                        min_value=0,
                        format="%d",
                    ),    
                    "entries": st.column_config.NumberColumn(
                        "Entries",
                        help="The total number of goods loaded.",
                        min_value=0,
                        format="%d",
                    ),  
                    "exits": st.column_config.NumberColumn(
                        "Exits",
                        help="The total number of goods unloaded.",
                        min_value=0,
                        format="%d",
                    )
                }
    return column_config