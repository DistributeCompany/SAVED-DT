import pandas as pd
from utils.classes import Vehicle, Trip
from datetime import datetime

def update_statistics():
    # Init response
    response = pd.DataFrame()

    # Get all vehicles
    vehicles = Vehicle.get_all_vehicles()

    # Loop over vehicles
    for vehicle in vehicles:
        # Create new entry for vehicle statistics
        new_row = pd.DataFrame([
            {
            'timestamp': datetime.now(),
            'id': vehicle.id,
            'lat': 0,
            'lng': 0,
            'current_trip': vehicle.current_trip,
            'current_action': vehicle.current_action,
            'status': vehicle.status,
            'battery_level': 100,
            'co2_emission': 0, #g/km
            'nox_emission': 0, #g/km
            'noise_pollution': 0, # db
            'weight': 0,
            }
            ])
        
        # Add new to to vehicle.statistics
        vehicle.statistics = pd.concat([vehicle.statistics,new_row],ignore_index=True)

        '''
        Update Cumulative Statistics
        '''
        
        match vehicle.status:
            case 'move':
                # Update move
                move = vehicle.cum_statistics.iloc[-1]['move'] + (datetime.now() - vehicle.cum_statistics.iloc[-1]['timestamp']).total_seconds()
                
                # Check if vehicle is 'moving empty'
                if vehicle.current_action == 0:
                    # First action is a 'move' -> so it's driving empty (towards somewhere) $TODO: check whether this is the case also for SAVED use case
                    empty_driving = vehicle.cum_statistics.iloc[-1]['empty_driving'] + (datetime.now() - vehicle.cum_statistics.iloc[-1]['timestamp']).total_seconds()
                    full_driving = vehicle.cum_statistics.iloc[-1]['full_driving']           

                    # Weighted utilization from start to previous entry
                    previous_utilization = vehicle.cum_statistics.iloc[-1]['utilization'] * (vehicle.cum_statistics.iloc[-1]['timestamp'] - vehicle.cum_statistics.iloc[0]['timestamp']).total_seconds()
                    
                    # Weighted utilization of current entry
                    current_utilization = 0

                    # Total weighted utilization
                    utilization = (previous_utilization + current_utilization) / (datetime.now() - vehicle.cum_statistics.iloc[0]['timestamp']).total_seconds()                             
                else:
                    # Count number of loads and unloads
                    load = 0
                    unload = 0
                    for i in range(vehicle.current_action):
                        if vehicle.current_trip.actions[i].action_type == 'load' and vehicle.current_trip.actions[i].lifecycle == 'completed':
                            load += 1
                        elif vehicle.current_trip.actions[i].action_type == 'unload'  and vehicle.current_trip.actions[i].lifecycle == 'completed':
                            unload += 1
                
                    if (load - unload) == vehicle.load_capacities:
                        # Vehicle is full
                        full_driving = vehicle.cum_statistics.iloc[-1]['full_driving'] + (datetime.now() - vehicle.cum_statistics.iloc[-1]['timestamp']).total_seconds()
                        empty_driving = vehicle.cum_statistics.iloc[-1]['empty_driving']
                    elif unload == load:
                        # Vehicle is empty
                        empty_driving = vehicle.cum_statistics.iloc[-1]['empty_driving'] + (datetime.now() - vehicle.cum_statistics.iloc[-1]['timestamp']).total_seconds()
                        full_driving = vehicle.cum_statistics.iloc[-1]['full_driving']
                    
                    current_utilization = (load - unload) / vehicle.load_capacities

                    # Weighted utilization from start to previous entry
                    previous_utilization = vehicle.cum_statistics.iloc[-1]['utilization'] * (vehicle.cum_statistics.iloc[-1]['timestamp'] - vehicle.cum_statistics.iloc[0]['timestamp']).total_seconds()
                    
                    # Weighted utilization of current entry
                    current_utilization = current_utilization * (datetime.now() - vehicle.cum_statistics.iloc[-1]['timestamp']).total_seconds()

                    # Total weighted utilization
                    utilization = (previous_utilization + current_utilization) / (datetime.now() - vehicle.cum_statistics.iloc[0]['timestamp']).total_seconds()

                # Remainder stays the same
                idle = vehicle.cum_statistics.iloc[-1]['idle']
                wait = vehicle.cum_statistics.iloc[-1]['wait']
                load = vehicle.cum_statistics.iloc[-1]['load']
                unload = vehicle.cum_statistics.iloc[-1]['unload']
                charging = vehicle.cum_statistics.iloc[-1]['charging']
                failed = vehicle.cum_statistics.iloc[-1]['failed']

            case 'idle':
                # Update idle
                idle = vehicle.cum_statistics.iloc[-1]['idle'] + (datetime.now() - vehicle.cum_statistics.iloc[-1]['timestamp']).total_seconds()
                
                # Remainder stays the same
                move = vehicle.cum_statistics.iloc[-1]['move']
                wait = vehicle.cum_statistics.iloc[-1]['wait']
                load = vehicle.cum_statistics.iloc[-1]['load']
                unload = vehicle.cum_statistics.iloc[-1]['unload']
                charging = vehicle.cum_statistics.iloc[-1]['charging']
                failed = vehicle.cum_statistics.iloc[-1]['failed']
                empty_driving = vehicle.cum_statistics.iloc[-1]['empty_driving']
                full_driving = vehicle.cum_statistics.iloc[-1]['full_driving']     
                # Weighted utilization from start to previous entry
                previous_utilization = vehicle.cum_statistics.iloc[-1]['utilization'] * (vehicle.cum_statistics.iloc[-1]['timestamp'] - vehicle.cum_statistics.iloc[0]['timestamp']).total_seconds()
                
                # Weighted utilization of current entry
                current_utilization = 0

                # Total weighted utilization
                utilization = (previous_utilization + current_utilization) / (datetime.now() - vehicle.cum_statistics.iloc[0]['timestamp']).total_seconds()

            case 'wait':
                # Update wait
                wait = vehicle.cum_statistics.iloc[-1]['wait'] + (datetime.now() - vehicle.cum_statistics.iloc[-1]['timestamp']).total_seconds()
                
                # Remainder stays the same
                move = vehicle.cum_statistics.iloc[-1]['move']
                idle = vehicle.cum_statistics.iloc[-1]['idle']
                load = vehicle.cum_statistics.iloc[-1]['load']
                unload = vehicle.cum_statistics.iloc[-1]['unload']
                charging = vehicle.cum_statistics.iloc[-1]['charging']
                failed = vehicle.cum_statistics.iloc[-1]['failed']
                empty_driving = vehicle.cum_statistics.iloc[-1]['empty_driving']
                full_driving = vehicle.cum_statistics.iloc[-1]['full_driving']                
            case 'load':
                # Update load
                load = vehicle.cum_statistics.iloc[-1]['load'] + (datetime.now() - vehicle.cum_statistics.iloc[-1]['timestamp']).total_seconds()
                
                # Remainder stays the same
                move = vehicle.cum_statistics.iloc[-1]['move']
                idle = vehicle.cum_statistics.iloc[-1]['idle']
                wait = vehicle.cum_statistics.iloc[-1]['wait']
                unload = vehicle.cum_statistics.iloc[-1]['unload']
                charging = vehicle.cum_statistics.iloc[-1]['charging']
                failed = vehicle.cum_statistics.iloc[-1]['failed']   
                empty_driving = vehicle.cum_statistics.iloc[-1]['empty_driving']
                full_driving = vehicle.cum_statistics.iloc[-1]['full_driving']      

                # Weighted utilization from start to previous entry
                previous_utilization = vehicle.cum_statistics.iloc[-1]['utilization'] * (vehicle.cum_statistics.iloc[-1]['timestamp'] - vehicle.cum_statistics.iloc[0]['timestamp']).total_seconds()
                
                # Weighted utilization of current entry
                current_utilization = 0

                # Total weighted utilization
                utilization = (previous_utilization + current_utilization) / (datetime.now() - vehicle.cum_statistics.iloc[0]['timestamp']).total_seconds()                    
            case 'unload':
                # Update unload
                unload = vehicle.cum_statistics.iloc[-1]['unload'] + (datetime.now() - vehicle.cum_statistics.iloc[-1]['timestamp']).total_seconds()
                
                # Remainder stays the same
                move = vehicle.cum_statistics.iloc[-1]['move']
                idle = vehicle.cum_statistics.iloc[-1]['idle']
                wait = vehicle.cum_statistics.iloc[-1]['wait']
                load = vehicle.cum_statistics.iloc[-1]['load']
                charging = vehicle.cum_statistics.iloc[-1]['charging']
                failed = vehicle.cum_statistics.iloc[-1]['failed']     
                empty_driving = vehicle.cum_statistics.iloc[-1]['empty_driving']
                full_driving = vehicle.cum_statistics.iloc[-1]['full_driving']       

                # Weighted utilization from start to previous entry
                previous_utilization = vehicle.cum_statistics.iloc[-1]['utilization'] * (vehicle.cum_statistics.iloc[-1]['timestamp'] - vehicle.cum_statistics.iloc[0]['timestamp']).total_seconds()
                
                # Weighted utilization of current entry
                current_utilization = 0

                # Total weighted utilization
                utilization = (previous_utilization + current_utilization) / (datetime.now() - vehicle.cum_statistics.iloc[0]['timestamp']).total_seconds()                                       
            case 'charging':
                # Update charging
                charging = vehicle.cum_statistics.iloc[-1]['charging'] + (datetime.now() - vehicle.cum_statistics.iloc[-1]['timestamp']).total_seconds()
                
                # Remainder stays the same
                move = vehicle.cum_statistics.iloc[-1]['move']
                idle = vehicle.cum_statistics.iloc[-1]['idle']
                wait = vehicle.cum_statistics.iloc[-1]['wait']
                load = vehicle.cum_statistics.iloc[-1]['load']
                unload = vehicle.cum_statistics.iloc[-1]['unload']
                failed = vehicle.cum_statistics.iloc[-1]['failed']  
                empty_driving = vehicle.cum_statistics.iloc[-1]['empty_driving']
                full_driving = vehicle.cum_statistics.iloc[-1]['full_driving']                
            case 'failed':
                # Update failed
                failed = vehicle.cum_statistics.iloc[-1]['failed'] + (datetime.now() - vehicle.cum_statistics.iloc[-1]['timestamp']).total_seconds()
                
                # Remainder stays the same
                move = vehicle.cum_statistics.iloc[-1]['move']
                idle = vehicle.cum_statistics.iloc[-1]['idle']
                wait = vehicle.cum_statistics.iloc[-1]['wait']
                load = vehicle.cum_statistics.iloc[-1]['load']
                unload = vehicle.cum_statistics.iloc[-1]['unload']
                charging = vehicle.cum_statistics.iloc[-1]['charging']  
                empty_driving = vehicle.cum_statistics.iloc[-1]['empty_driving']
                full_driving = vehicle.cum_statistics.iloc[-1]['full_driving']                


        # Get total time of vehicle in system
        time_in_system = (datetime.now() - vehicle.cum_statistics.iloc[0]['timestamp']).total_seconds()


        # Get total traveled distance
        travel_distance = 0
        for _, row in vehicle.schedule.iterrows():
            trip = Trip.get_by_id(row['task_id'])
            actions = trip.get_actions()
            for action in actions:
                if action.action_type == 'move':
                    travel_distance += action.route.length * (action.progress/100)

        # Create new row for cumulative statistics
        new_cum_row = pd.DataFrame([
            {
            'timestamp': datetime.now(),
            'id': vehicle.id,
            'name': vehicle.name,
            'time_in_system': time_in_system,   # time that has passed since vehicle was initialized (in sec)
            'move': move,                  # % driving (either full or empty)
            'wait': wait,                 # % standing still while out-and-about
            'load': load,                 # % load time of cargo onto vehicle
            'unload': unload,             # % unload time of cargo out of vehicle (i.e., at customer)
            'idle': idle ,                  # % time vehicle is idle (no job can be executed)
            'charging': charging,               # % time vehicle is charging
            'failed': failed,                   # % time vehicle is failed (note: these 6 percentages should sum up to 100.) 
            'empty_driving': empty_driving,                 # % driving completly empty
            'full_driving': full_driving,                  # % driving completly full (i.e., number of goods == load capacity)
            'utilization': utilization,                   # same as 'working'?
            'travel_distance': travel_distance,               # total (kilo)meters driven (real)
            'entries': vehicle.entries,                       # total # of cargo loaded onto vehicle
            'exits': vehicle.exits,                         # total # of cargo unloaded from vehicle
            'energy_consumption': 0,
            'co2_emission': 0,                  #g/km
            'nox_emission': 0,                  #g/km
            'noise_pollution': 0,               # db (does not make sense to have this as a cumulative statistic?)
            'land_use': 0,                      #m3/hour
            }
            ])
        
        # Add to cumulative statistics
        vehicle.cum_statistics = pd.concat([vehicle.cum_statistics,new_cum_row],ignore_index=True)

        # Response is the latest data on cumulative statistics of all vehicles (= list of DataFrames)
        response = pd.concat([response,new_cum_row],ignore_index=True)

    return response