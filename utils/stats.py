"""
Module for updating vehicle and cumulative statistics.

This module collects real-time statistics from all vehicles, updates both 
instantaneous and cumulative statistics, and returns a combined DataFrame.
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import Optional
from utils.classes import Vehicle, Trip


def update_statistics() -> pd.DataFrame:
    """
    Update and compile real-time and cumulative statistics for all vehicles.

    For each vehicle, a new instantaneous statistics row is added to the vehicle's 
    statistics DataFrame, and the cumulative statistics are updated based on the 
    vehicle's current status and activity durations.

    Returns
    -------
    pd.DataFrame
        A DataFrame containing the latest cumulative statistics for all vehicles.
    """
    response = pd.DataFrame()
    vehicles = Vehicle.get_all_vehicles()

    for vehicle in vehicles:
        # Cache the current time for consistency within this iteration
        now = datetime.now()

        # Create new entry for instantaneous vehicle statistics
        new_row = pd.DataFrame([{
            'timestamp': now,
            'id': vehicle.id,
            'lat': 0,  # Placeholder: update if vehicle has a location attribute
            'lng': 0,  # Placeholder: update if vehicle has a location attribute
            'current_trip': vehicle.current_trip,
            'current_action': vehicle.current_action,
            'status': vehicle.status,
            'battery_level': 100,  # Assumed default; update as needed
            'co2_emission': 0,  # g/km
            'nox_emission': 0,  # g/km
            'noise_pollution': 0,  # dB
            'weight': 0,
        }])
        vehicle.statistics = pd.concat([vehicle.statistics, new_row], ignore_index=True)

        # --- Update Cumulative Statistics ---
        # Get the timestamp of the last cumulative statistics entry for this vehicle.
        last_entry = vehicle.cum_statistics.iloc[-1]
        dt_last = last_entry['timestamp']
        delta_seconds = (now - dt_last).total_seconds()

        # Initialize variables to be updated.
        move: float = last_entry['move']
        idle: float = last_entry['idle']
        wait: float = last_entry['wait']
        load_time_val: float = last_entry['load']
        unload_time_val: float = last_entry['unload']
        charging: float = last_entry['charging']
        failed: float = last_entry['failed']
        empty_driving: float = last_entry['empty_driving']
        full_driving: float = last_entry['full_driving']
        utilization: float = last_entry['utilization']

        # Use Python 3.10 match-case for different statuses.
        match vehicle.status:
            case 'move':
                move += delta_seconds

                if vehicle.current_action == 0:
                    # Vehicle is moving empty.
                    empty_driving += delta_seconds
                    # Full driving remains unchanged.
                    previous_utilization = last_entry['utilization'] * (dt_last - vehicle.cum_statistics.iloc[0]['timestamp']).total_seconds()
                    current_utilization = 0
                    utilization = (previous_utilization + current_utilization) / ((now - vehicle.cum_statistics.iloc[0]['timestamp']).total_seconds())
                else:
                    # Count the number of completed load and unload actions.
                    load_count = 0
                    unload_count = 0
                    for i in range(vehicle.current_action):
                        action = vehicle.current_trip.actions[i]
                        if action.action_type == 'load' and action.lifecycle == 'completed':
                            load_count += 1
                        elif action.action_type == 'unload' and action.lifecycle == 'completed':
                            unload_count += 1

                    if (load_count - unload_count) == vehicle.load_capacities:
                        # Vehicle is full.
                        full_driving += delta_seconds
                    elif unload_count == load_count:
                        # Vehicle is empty.
                        empty_driving += delta_seconds

                    curr_util = (load_count - unload_count) / vehicle.load_capacities
                    previous_utilization = last_entry['utilization'] * (dt_last - vehicle.cum_statistics.iloc[0]['timestamp']).total_seconds()
                    current_utilization = curr_util * delta_seconds
                    utilization = (previous_utilization + current_utilization) / ((now - vehicle.cum_statistics.iloc[0]['timestamp']).total_seconds())

            case 'idle':
                idle += delta_seconds
                previous_utilization = last_entry['utilization'] * (dt_last - vehicle.cum_statistics.iloc[0]['timestamp']).total_seconds()
                current_utilization = 0
                utilization = (previous_utilization + current_utilization) / ((now - vehicle.cum_statistics.iloc[0]['timestamp']).total_seconds())

            case 'wait':
                wait += delta_seconds

            case 'load':
                load_time_val += delta_seconds
                previous_utilization = last_entry['utilization'] * (dt_last - vehicle.cum_statistics.iloc[0]['timestamp']).total_seconds()
                current_utilization = 0
                utilization = (previous_utilization + current_utilization) / ((now - vehicle.cum_statistics.iloc[0]['timestamp']).total_seconds())

            case 'unload':
                unload_time_val += delta_seconds
                previous_utilization = last_entry['utilization'] * (dt_last - vehicle.cum_statistics.iloc[0]['timestamp']).total_seconds()
                current_utilization = 0
                utilization = (previous_utilization + current_utilization) / ((now - vehicle.cum_statistics.iloc[0]['timestamp']).total_seconds())

            case 'charging':
                charging += delta_seconds

            case 'failed':
                failed += delta_seconds

        # Calculate total time the vehicle has been in the system.
        time_in_system = (now - vehicle.cum_statistics.iloc[0]['timestamp']).total_seconds()

        # Calculate total traveled distance from the schedule.
        travel_distance = 0.0
        for _, row in vehicle.schedule.iterrows():
            trip: Optional[Trip] = Trip.get_by_id(row['task_id'])
            if trip is not None:
                actions = trip.get_actions()
                for action in actions:
                    if action.action_type == 'move':
                        travel_distance += action.route.length * (action.progress / 100)

        # Create a new cumulative statistics row.
        new_cum_row = pd.DataFrame([{
            'timestamp': now,
            'id': vehicle.id,
            'name': vehicle.name,
            'time_in_system': time_in_system,    # time that has passed since vehicle was initialized (in sec)
            'move': move,                        # % driving (either full or empty)       
            'wait': wait,                        # % standing still while out-and-about
            'load': load_time_val,               # % load time of cargo onto vehicle
            'unload': unload_time_val,           # % unload time of cargo out of vehicle (i.e., at customer)
            'idle': idle,                        # % time vehicle is idle (no job can be executed)
            'charging': charging,                # % time vehicle is charging
            'failed': failed,                    # % time vehicle is failed (note: these 6 percentages should sum up to 100.) 
            'empty_driving': empty_driving,      # % driving completly empty
            'full_driving': full_driving,        # % driving completly full (i.e., number of goods == load capacity)
            'utilization': utilization,
            'travel_distance': travel_distance,  # total (kilo)meters driven (real)
            'entries': vehicle.entries,          # total # of cargo loaded onto vehicle
            'exits': vehicle.exits,              # total # of cargo unloaded from vehicle
            'energy_consumption': 0,
            'co2_emission': 0,                   # g/km
            'nox_emission': 0,                   # g/km
            'noise_pollution': 0,                # dB
            'land_use': 0,                       # m3/hour
        }])
        vehicle.cum_statistics = pd.concat([vehicle.cum_statistics, new_cum_row], ignore_index=True)
        response = pd.concat([response, new_cum_row], ignore_index=True)

    return response
