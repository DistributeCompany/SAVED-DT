
from typing import List
from datetime import datetime, timedelta
import uuid
import pandas as pd

class Location:
    """
    A class to represent a Location.

    Attributes:
    ----------
    _instances : list
        A class attribute that stores all instances of Location.
    _total_instances : int
        A class attribute that stores the total number of Location instances created.

    Instance Attributes:
    ----------
    georeference : list
        The latitude and longitude of the location.
    name : str, optional
        The name of the location. Default is "".
    type : str, optional
        The type of the location (e.g., 'customer', 'warehouse'). Default is 'customer'.
    actors : list, optional
        The actors related to the location. Default is None.
    actions : list, optional
        The actions related to the location. Default is None.
    constraint : Any, optional
        The constraints related to the location. Default is None.
    marker : Any, optional
        The marker for visualization purposes. Default is None.
    creation_date : datetime
        The date and time when the location was created.
    last_modified : datetime
        The date and time when the location was last modified.
    id : str
        The unique identifier of the location.

    Class Methods:
    -------
    get_by_id(id: str) -> 'Location':
        Returns the location instance matched by id.
    get_by_type(type: str) -> List['Location']:
        Returns a list of locations of a specific type.
    get_all_locations() -> List['Location']:
        Returns a list of all locations.
    get_total_locations() -> int:
        Returns the total number of locations created.
    delete_all_customers():
        Deletes all customer-type locations.

    Example:
    -------
    location = Location(georeference=[34.0522, -118.2437], name="Los Angeles")
    """

    _instances = []
    _total_instances = 0

    def __init__(self, georeference, name="", type="customer", actors=None, actions=None, constraint=None, marker=None):
        """
        Initialize a new Location instance.

        Parameters:
        ----------
        georeference : list
            [latitude, longitude] of the location.
        name : str, optional
            Name of the location. Defaults to an empty string.
        type : str, optional
            Type of the location (e.g., 'customer', 'warehouse'). Defaults to 'customer'.
        actors : list, optional
            Actors related to the location. Defaults to None.
        actions : list, optional
            Actions related to the location. Defaults to None.
        constraint : Any, optional
            Constraints related to the location. Defaults to None.
        marker : Any, optional
            Marker for visualization purposes. Defaults to None.
        """
        
        # OTM
        self.id = str(uuid.uuid4())  # Generate a unique identifier for the location
        self.name = name
        self.creation_date = datetime.now()
        self.last_modified = datetime.now()
        self.georeference = georeference  # [lat, lng]
        self.type = type
        self.actors = actors
        self.actions = actions
        self.constraint = constraint
        
        # Custom
        self.marker = marker

        Location._instances.append(self)  # Add the new instance to the list of instances
        Location._total_instances += 1  # Increment the total instances counter

    @classmethod
    def get_by_id(cls, id: str) -> 'Location':
        """
        Get location based on UUID.

        Parameters:
        ----------
        id : str
            String representation of a UUID.

        Returns:
        -------
        Location
            The location instance with the specified UUID, or None if not found.
        """
        return next((location for location in cls._instances if location.id == id), None)

    @classmethod
    def get_by_name(cls, name: str) -> 'Location':
        """
        Get location based on name.

        Parameters:
        ----------
        id : str
            String representation of a name.

        Returns:
        -------
        Location
            The location instance with the specified name, or None if not found.
        """
        return next((location for location in cls._instances if location.name == name), None)   
    
    @classmethod
    def get_by_georeference(cls, georeference: List[float]) -> 'Location':
        return next((location for location in cls._instances if location.georeference == georeference), None)

    @classmethod
    def get_by_type(cls, type: str) -> List['Location']:
        """
        Get all locations of a specific type.

        Parameters:
        ----------
        type : str
            The type of locations to retrieve.

        Returns:
        -------
        List[Location]
            List of locations of the specified type.
        """
        return [location for location in cls._instances if location.type == type]

    @classmethod
    def get_all_locations(cls) -> List['Location']:
        """
        Get all location instances.

        Returns:
        -------
        List[Location]
            List of all location instances.
        """
        return cls._instances

    @classmethod
    def get_total_locations(cls) -> int:
        """
        Get the total number of location instances initialized.

        Returns:
        -------
        int
            The total number of locations.
        """
        return cls._total_instances

    @classmethod
    def delete_all_customers(cls):
        """
        Delete all customer-type location instances.
        """
        cls._instances = [location for location in cls._instances if location.type != 'customer']
        cls._total_instances = len(cls._instances)  # Update the total instances counter

class Trip:
    """
    A class to represent a Trip.

    Attributes:
    ----------
    VALID_STATUS: list
        A class attribute that stores all allowed values for the instance attribute 'status'.
    VALID_TRANSPORT_MODE: list
        A class attribute that stores all allowed values for the instance attribute 'transport_mode'.
    _instances : list
        A class attribute that stores all instances of Trip.
    _total_instances : int
        A class attribute that stores the total number of Trip instances created.

    Instance Attributes:
    ----------
    name : str, optional
        The name of the Trip. Default is "".
    status : str, optional
        The status of the trip (e.g., 'draft', 'requested', 'confirmed', 'in_transit', 'completed', 'cancelled'). Default is 'requested'.
    transport_mode : str, optional
        The method of transport used for the trip (e.g., 'road', 'air', 'sea'). Default is 'road'.
    vehicle : Vehicle, optional
        The vehicle assigned to this trip. Default is None.
    actors : list, optional
        The actors associated with this trip. Default is [].
    actions : list, optional
        The actions associated with this trip. Default is [].
    constraint : Any, optional
        The constraint associated with this trip. Default is None.
    marker : Folium.Marker, optional
        The Folium.Marker object of the destination of this trip. Default is None.
    progress : int, optional
        An integer denoting how far the trip is completed [0-100%]. Default is 0.
    creation_date : datetime
        The date and time when the trip was created.
    last_modified : datetime
        The date and time when the trip was last modified.
    id : str
        The unique identifier of the trip.

    Class Methods:
    -------
    get_by_id(id: str) -> 'Trip':
        Returns the trip instance matched by id.
    get_by_status(status: str) -> List['Trip']:
        Returns a list of all trips matched by status.
    get_all_trips() -> List['Trip']:
        Returns a list of all trips.
    get_total_trips() -> int:
        Returns the total number of trips created.
    delete_all_instances():
        Deletes all trip instances.

    Instance Methods:
    -------
    add_action(action: Action) -> bool:
        Adds action to trip instance

    Example:
    -------
    trip = Trip(name=f"Trip {Trip.get_total_trips()}")
    """

    VALID_STATUS = ['draft','requested','confirmed','in_transit','completed','cancelled','accepted','modified']
    VALID_TRANSPORT_MODES = ['maritime','road','rail','air','inlandWaterway'] 
    _instances = []
    _total_instances = 0

    def __init__(self, name="", status="draft", transport_mode="road", vehicle=None, actors=None, actions=None, constraint=None, marker=None, progress=0):
        """
        Initialize a new Trip instance.

        Parameters:
        ----------
        name : str, optional
            The name of the Trip. Defaults to "".
        status : str, optional
            The status of the trip (e.g., 'draft', 'requested', 'confirmed', 'in transit', 'completed', 'cancelled'). Defaults to 'draft'.
        transport_mode : str, optional
            The method of transport used for the trip (e.g., 'road', 'air', 'sea'). Defaults to 'road'.
        vehicle : Vehicle, optional
            The vehicle assigned to this trip. Defaults to None.
        actors : list, optional
            The actors associated with this trip. Defaults to [].
        actions : list, optional
            The actions associated with this trip. Defaults to [].
        constraint : Any, optional
            The constraint associated with this trip. Defaults to None.
        marker : Folium.Marker, optional
            The Folium.Marker object of the destination of this trip. Defaults to None.
        progress : int, optional
            An integer denoting how far the trip is completed [0-100%]. Defaults to 0.

        Raises:
        ------
        ValueError: If the 'status' or 'transport_mode' is not in the list of supported values.            
        """

        if status not in Trip.VALID_STATUS:
                raise ValueError(f"Status '{status}' is not a valid status. Valid status are: {', '.join(Trip.VALID_STATUS)}")
        if transport_mode not in Trip.VALID_TRANSPORT_MODES:
                raise ValueError(f"Transport mode '{transport_mode}' is not a valid mode. Valid modes are: {', '.join(Trip.VALID_TRANSPORT_MODES)}")
        
        # OTM
        self.id = str(uuid.uuid4())  # Generate a unique identifier for the trip
        self.name = name
        self.status = status
        self.transport_mode = transport_mode
        self.vehicle = vehicle
        self.actors = actors if actors is not None else []
        self.actions = actions if actions is not None else []
        self.constraint = constraint
        self.creation_date = datetime.now()
        self.last_modified = datetime.now()

        # Custom
        self.marker = marker
        self.progress = progress

        Trip._instances.append(self)  # Add the new instance to the list of instances
        Trip._total_instances += 1  # Increment the total instances counter

    def get_actions(self) -> List['Action']:
        return self.actions
    
    def add_action(self, action) -> bool:
        self.actions.append(action)
        self.last_modified = datetime.now()
        return True
    
    def get_total_route_length(self) -> int:
        route_length = 0
        for ac in self.actions:
            route_length += ac.route.length
        return route_length

    def update_instance_parameter(self, parameter, value):
        """
        Update the parameter of a class instance to a given value.

        Parameters:
        self: object
            The class instance whose parameter needs to be updated.
        parameter: str
            The name of the parameter to be updated.
        value: any
            The new value to set for the parameter.
        """
        setattr(self, parameter, value)
        self.last_modified = datetime.now()

        if parameter == 'status' and self.vehicle is not None:
            # Also update status in schedule of vehicle
            self.vehicle.schedule.loc[self.vehicle.schedule['task_id'] == self.id, 'status'] = value

    @classmethod
    def get_by_id(cls, id: str) -> 'Trip':
        """
        Get trip based on UUID.

        Parameters:
        ----------
        id : str
            String representation of a UUID.

        Returns:
        -------
        Trip
            The trip instance with the specified UUID, or None if not found.
        """
        return next((trip for trip in cls._instances if trip.id == id), None)

    @classmethod
    def get_by_name(cls, name: str) -> 'Trip':
        """
        Get trip based on name.

        Parameters:
        ----------
        id : str
            String representation of a name.

        Returns:
        -------
        Trip
            The trip instance with the specified name, or None if not found.
        """
        return next((trip for trip in cls._instances if trip.name == name), None)

    @classmethod
    def get_by_status(cls, status: str) -> List['Trip']:
        return [i for i in cls._instances if i.status == status]
    
    @classmethod
    def get_all_trips(cls) -> List['Trip']:
        """
        Get all trip instances.

        Returns:
        -------
        List[Trip]
            List of all trip instances.
        """
        return cls._instances

    @classmethod
    def get_total_trips(cls) -> int:
        """
        Get the total number of trip instances initialized.

        Returns:
        -------
        int
            The total number of trips.
        """
        return cls._total_instances
    @classmethod
    def delete_all_instances(cls):
        """
        Delete all trip instances.

        This method clears the list of trip instances and resets the total instances counter.
        """
        cls._instances.clear() 
        cls._total_instances = 0

class Actor:
    """
    A class to represent an Actor.

    Attributes:
    ----------
    _instances : list
        A class attribute that stores all instances of Actor.
    _total_instances : int
        A class attribute that stores the total number of Actor instances created.

    Instance Attributes:
    ----------
    location : Location
        The location associated with the actor.
    name : str, optional
        The name of the actor. Default is "".
    creation_date : datetime
        The date and time when the actor was created.
    last_modified : datetime
        The date and time when the actor was last modified.
    id : str
        The unique identifier of the actor.

    Class Methods:
    -------
    get_by_id(id: str) -> List['Actor']:
        Returns a list of actor instances matched by id.
    get_all_actors() -> List['Actor']:
        Returns a list of all actors.
    get_total_actors() -> int:
        Returns the total number of actors created.
    delete_all_instances():
        Deletes all actor instances.

    Example:
    -------
    actor = Actor(location=some_location, name="John Doe")
    """

    _instances = []
    _total_instances = 0

    def __init__(self, location, name=""):
        """
        Initialize a new Actor instance.

        Parameters:
        ----------
        location : Location
            The location associated with the actor.
        name : str, optional
            The name of the actor. Defaults to an empty string.
        """
        # OTM
        self.id = str(uuid.uuid4())  # Generate a unique identifier for the actor
        self.name = name
        self.creation_date = datetime.now()
        self.last_modified = datetime.now()
        self.locations = [location]  # Location Class #TODO: Change to list [location]

        Actor._instances.append(self)  # Add the new instance to the list of instances
        Actor._total_instances += 1  # Increment the total instances counter

    @classmethod
    def get_by_id(cls, id: str) -> List['Actor']:
        """
        Get actor based on UUID.

        Parameters:
        ----------
        id : str
            String representation of a UUID.

        Returns:
        -------
        List[Actor]
            The actor instances with the specified UUID, or an empty list if not found.
        """
        return [i for i in cls._instances if i.id == id]

    @classmethod
    def get_all_actors(cls) -> List['Actor']:
        """
        Get all actor instances.

        Returns:
        -------
        List[Actor]
            List of all actor instances.
        """
        return cls._instances

    @classmethod
    def get_total_actors(cls) -> int:
        """
        Get the total number of actor instances initialized.

        Returns:
        -------
        int
            The total number of actors.
        """
        return cls._total_instances

    @classmethod
    def delete_all_instances(cls):
        """
        Delete all actor instances.

        This method clears the list of actor instances and resets the total instances counter.
        """
        cls._instances.clear()  # Clear the list of instances
        cls._total_instances = 0  # Reset the total instances counter

class Route:
    """
    A class to represent a Route.

    Attributes:
    ----------
    _instances : list
        A class attribute that stores all instances of Route.
    _total_instances : int
        A class attribute that stores the total number of Route instances created.

    Instance Attributes:
    ----------
    georeference : list
        List with coordinates of the route, used to plot a polyline on a map.
    name : str, optional
        The name of the route. Default is "".
    actors : list, optional
        The actors associated with this route. Default is None.
    length : float, optional
        The length of the route in meters. Default is None.
    nodes : list, optional
        The list of NodeIDs representing the route. Default is None.
    polyline : Folium.PolyLine, optional
        The Folium.PolyLine object used for visualization on a map. Default is None.
    creation_date : datetime
        The date and time when the route was created.
    last_modified : datetime
        The date and time when the route was last modified.
    id : str
        The unique identifier of the route.

    Class Methods:
    -------
    get_by_id(id: str) -> List['Route']:
        Returns a list of route instances matched by id.
    get_all_routes() -> List['Route']:
        Returns a list of all routes.
    get_total_routes() -> int:
        Returns the total number of routes created.
    delete_all_instances():
        Deletes all route instances.

    Example:
    -------
    route = Route(georeference=[[34.0522, -118.2437], [36.1699, -115.1398]], name="Route 1")
    """

    _instances = []
    _total_instances = 0

    def __init__(self, georeference, name="", actors=None, length=None, nodes=None, polyline=None, coordinates=None):
        """
        Initialize a new Route instance.

        Parameters:
        ----------
        georeference : list
            List with coordinates of the route.
        name : str, optional
            The name of the route. Defaults to an empty string.
        actors : list, optional
            The actors associated with this route. Defaults to None.
        length : float, optional
            The length of the route in meters. Defaults to None.
        nodes : list, optional
            The list of NodeIDs representing the route. Defaults to None.
        polyline : Folium.PolyLine, optional
            The Folium.PolyLine object used for visualization on a map. Defaults to None.
        coordinates: list['tuple']
            The list containing the coordinates describing the polyline. Defaults to None.
        """

        # OTM
        self.id = str(uuid.uuid4())  # Generate a unique identifier for the route
        self.name = name
        self.creation_date = datetime.now()
        self.last_modified = datetime.now()
        self.actors = actors
        self.georeference = georeference  # List with coordinates of the route

        # Custom
        self.length = length  # Length of the route in meters
        self.nodes = nodes  # List of NodeIDs
        self.polyline = polyline  # Folium.PolyLine object for visualization
        self.coordinates = coordinates # List with coordinates of polyline

        Route._instances.append(self)  # Add the new instance to the list of instances
        Route._total_instances += 1  # Increment the total instances counter

    @classmethod
    def get_by_id(cls, id: str) -> List['Route']:
        """
        Get route based on UUID.

        Parameters:
        ----------
        id : str
            String representation of a UUID.

        Returns:
        -------
        List[Route]
            The route instances with the specified UUID, or an empty list if not found.
        """
        return [route for route in cls._instances if route.id == id]

    @classmethod
    def get_all_routes(cls) -> List['Route']:
        """
        Get all route instances.

        Returns:
        -------
        List[Route]
            List of all route instances.
        """
        return cls._instances

    @classmethod
    def get_total_routes(cls) -> int:
        """
        Get the total number of route instances initialized.

        Returns:
        -------
        int
            The total number of routes.
        """
        return cls._total_instances

    @classmethod
    def delete_all_instances(cls):
        """
        Delete all route instances.

        This method clears the list of route instances and resets the total instances counter.
        """
        cls._instances.clear()  # Clear the list of instances
        cls._total_instances = 0  # Reset the total instances counter

class Action:
    """
    A class to represent an Action. 'move', 'load' and 'unload' only. 

    Attributes:
    ----------
    _instances : list
        A class attribute that stores all instances of Action.
    _total_instances : int
        A class attribute that stores the total number of Action instances created.

    Instance Attributes:
    ----------
    actiontype : str, optional
        The type of action. Default is "move".
    name : str, optional
        The name of the action. Default is "".
    lifecycle : str, optional
        The lifecycle status of the action. Default is "requested".
    transport_mode : str, optional
        The mode of transport for the action. Default is None.
    trip : Trip, optional
        The trip associated with the action. Default is None.
    _from : Location, optional
        The starting location of the action. Default is None.
    _to : Location, optional
        The destination location of the action. Default is None.
    timeformat : str, optional
        The format of the time attributes. Default is 'dateTime'.
    start_time : datetime, optional
        The start time of the action. Default is None.
    end_time : datetime, optional
        The end time of the action. Default is None.
    route : Route, optional
        The route associated with the action. Default is None.
    constraint : Any, optional
        The constraint associated with the action. Default is None.
    creation_date : datetime
        The date and time when the action was created.
    last_modified : datetime
        The date and time when the action was last modified.
    id : str
        The unique identifier of the action.

    Class Methods:
    -------
    get_by_id(id: str) -> List['Action']:
        Returns a list of action instances matched by id.
    get_all_actions() -> List['Action']:
        Returns a list of all actions.
    get_total_actions() -> int:
        Returns the total number of actions created.
    delete_all_instances():
        Deletes all action instances.

    Example:
    -------
    action = Action(actiontype="move", name="Move Action")
    """
    #TODO: add enum validation of 'lifecycle'. 

    _instances = []
    _total_instances = 0

    def __init__(self, sequence_nr=None, actiontype="move", name="", lifecycle="requested", transport_mode=None, trip=None,
                 _from=None, _to=None, timeformat='dateTime', duration=None, start_time=None, end_time=None, location=None,
                 route=None, constraint=None, progress=0):
        """
        Initialize a new Action instance.

        Parameters:
        ----------
        actiontype : str, optional
            The type of action. Defaults to "move".
        name : str, optional
            The name of the action. Defaults to an empty string.
        lifecycle : str, optional
            The lifecycle status of the action. Defaults to "requested".
        transport_mode : str, optional
            The mode of transport for the action. Defaults to None.
        trip : Trip, optional
            The trip associated with the action. Defaults to None.
        _from : Location, optional
            The starting location of the action. Defaults to None.
        _to : Location, optional
            The destination location of the action. Defaults to None.
        timeformat : str, optional
            The format of the time attributes. Defaults to 'dateTime'.
        start_time : datetime, optional
            The start time of the action. Defaults to None.
        end_time : datetime, optional
            The end time of the action. Defaults to None.
        route : Route, optional
            The route associated with the action. Defaults to None.
        constraint : Any, optional
            The constraint associated with the action. Defaults to None.
        """

        # OTM
        self.id = str(uuid.uuid4())  # Generate a unique identifier for the action
        self.name = name
        self.creation_date = datetime.now()
        self.last_modified = datetime.now()
        self.action_type = actiontype # Options: move, load, unload
        self.lifecycle = lifecycle
        self.transport_mode = transport_mode
        self.sequence_nr = sequence_nr
        self.trip = trip  # Trip Class
        self._from = _from  # Location Class
        self._to = _to  # Location Class
        self.time_format = timeformat
        self.duration = duration # only used for 'load' and 'unload' actions (in seconds)
        self.location = location # only used for 'load' and 'unload' actions (instance of Location class)
        self.start_time = start_time
        self.end_time = end_time
        self.route = route  # Route Class
        self.constraint = constraint
        
        # Custom
        self.progress = progress

        Action._instances.append(self)  # Add the new instance to the list of instances
        Action._total_instances += 1  # Increment the total instances counter

    def update_instance_parameter(self, parameter, value):
        """
        Update the parameter of a class instance to a given value.

        Parameters:
        self: object
            The class instance whose parameter needs to be updated.
        parameter: str
            The name of the parameter to be updated.
        value: any
            The new value to set for the parameter.
        """
        setattr(self, parameter, value)
        self.last_modified = datetime.now()

    @classmethod
    def get_by_id(cls, id: str) -> List['Action']:
        """
        Get action based on UUID.

        Parameters:
        ----------
        id : str
            String representation of a UUID.

        Returns:
        -------
        List[Action]
            The action instances with the specified UUID, or an empty list if not found.
        """
        return [i for i in cls._instances if i.id == id]

    @classmethod
    def get_all_actions(cls) -> List['Action']:
        """
        Get all action instances.

        Returns:
        -------
        List[Action]
            List of all action instances.
        """
        return cls._instances

    @classmethod
    def get_total_actions(cls) -> int:
        """
        Get the total number of action instances initialized.

        Returns:
        -------
        int
            The total number of actions.
        """
        return cls._total_instances

    @classmethod
    def delete_all_instances(cls):
        """
        Delete all action instances.

        This method clears the list of action instances and resets the total instances counter.
        """
        cls._instances.clear()  # Clear the list of instances
        cls._total_instances = 0  # Reset the total instances counter

class Vehicle:
    """
    A class to represent a Vehicle.

    Attributes:
    ----------
    _instances : list
        A class attribute that stores all instances of Vehicle.
    _total_instances : int
        A class attribute that stores the total number of Vehicle instances created.

    Instance Attributes:
    ----------
    id : str
        The unique identifier of the vehicle.
    name : str, optional
        The name of the vehicle. Default is "".
    vehicle_type : str, optional
        The type of vehicle. Default is "".
    fuel : str, optional
        The fuel type used by the vehicle. Default is None.
    average_fuel_consumption : float, optional
        The average fuel consumption of the vehicle. Default is None.
    emission_standard : str, optional
        The emission standard of the vehicle. Default is None.
    load_capacities : dict, optional
        The load capacities of the vehicle. Default is None.
    length : float, optional
        The length of the vehicle. Default is None.
    height : float, optional
        The height of the vehicle. Default is None.
    width : float, optional
        The width of the vehicle. Default is None.
    license_plate : str, optional
        The license plate number of the vehicle. Default is None.
    empty_weight : float, optional
        The empty weight of the vehicle. Default is None.
    actors : list, optional
        The actors associated with the vehicle. Default is None.
    sensors : list, optional
        The sensors associated with the vehicle. Default is None.
    actions : list, optional
        The actions associated with the vehicle. Default is None.
    marker : Folium.CircleMarker, optional
        The Folium.CircleMarker object for visualization on a map. Default is None.
    creation_date : datetime
        The date and time when the vehicle was created.
    last_modified : datetime
        The date and time when the vehicle was last modified.

    Class Methods:
    -------
    get_by_id(id: str) -> 'Vehicle':
        Returns the vehicle instance matched by id.
    get_by_type(vehicle_type: str) -> List['Vehicle']:
        Returns a list of vehicle instances matched by type.
    get_all_vehicles() -> List['Vehicle']:
        Returns a list of all vehicles.
    delete_last_x(number: int) -> bool:
        Deletes the last 'number' of vehicle instances.
    get_by_vehicle_name(name: str) -> 'Vehicle':
        Returns the vehicle instance matched by name.
    get_total_vehicles() -> int:
        Returns the total number of vehicles created.

    Example:
    -------
    vehicle = Vehicle(name="Truck", vehicle_type="Heavy")
    """

    _instances = []
    _total_instances = 0

    def __init__(self, name="", vehicle_type="", fuel=None, average_fuel_consumption=None, emission_standard=None, load_capacities=1,
                 length=None, height=None, width=None, license_plate=None, empty_weight=None, actors=None, sensors=None, actions=None, marker=None, status='idle',
                 load_time=0, unload_time=0, co2_emission=0, nox_emission=0, noise_pollution=0, land_use=0, battery_capacity=0,
                 energy_consumption_moving=0, energy_consumption_idling=0,battery_threshold=0,charge_speed=0, average_speed=(4.0/3.6)):
        """
        Initialize a new Vehicle instance.

        Parameters:
        ----------
        id : str, optional
            The unique identifier of the vehicle. Defaults to a new UUID.
        name : str, optional
            The name of the vehicle. Defaults to an empty string.
        vehicle_type : str, optional
            The type of vehicle. Defaults to an empty string.
        fuel : str, optional
            The fuel type used by the vehicle. Defaults to None.
        average_fuel_consumption : float, optional
            The average fuel consumption of the vehicle. Defaults to None.
        emission_standard : str, optional
            The emission standard of the vehicle. Defaults to None.
        load_capacities : dict, optional
            The load capacities of the vehicle. Defaults to None.
        length : float, optional
            The length of the vehicle. Defaults to None.
        height : float, optional
            The height of the vehicle. Defaults to None.
        width : float, optional
            The width of the vehicle. Defaults to None.
        license_plate : str, optional
            The license plate number of the vehicle. Defaults to None.
        empty_weight : float, optional
            The empty weight of the vehicle. Defaults to None.
        actors : list, optional
            The actors associated with the vehicle. Defaults to None.
        sensors : list, optional
            The sensors associated with the vehicle. Defaults to None.
        actions : list, optional
            The actions associated with the vehicle. Defaults to None.
        marker : Folium.CircleMarker, optional
            The Folium.CircleMarker object for visualization on a map. Defaults to None.
        schedule : pd.DataFrame
            The schedule of the vehicle. Defaults to an empty DataFrame.
        current_trip : Trip
            The trip currently being executed by vehicle. Defaults to None.
        """

        # OTM
        self.id = str(uuid.uuid4())  # Generate a unique identifier for the vehicle
        self.name = name
        self.creation_date = datetime.now()
        self.last_modified = datetime.now()
        self.vehicle_type = vehicle_type
        self.fuel = fuel
        self.average_fuel_consumption = average_fuel_consumption
        self.emission_standard = emission_standard
        self.load_capacities = load_capacities
        self.length = length
        self.height = height
        self.width = width
        self.license_plate = license_plate
        self.empty_weight = empty_weight
        self.actors = actors
        self.sensors = sensors
        self.actions = actions

        # Custom
        self.average_speed = average_speed # m/s
        self.actual_speed = self.average_speed
        self.marker = marker  # Folium.CircleMarker object for visualization
        self.schedule = pd.DataFrame(columns=['vehicle','task_id','task_name','start','end','status'])
        self.current_trip = None 
        self.current_action = None # Integer denoting the sequence_nr of the action currently being executed
        self.status = status # Defaults to 'idle'. Options: 'move', 'wait', 'load', 'unload', 'idle', 'charging', or 'failed'
        self.entries = 0
        self.exits = 0  	
        self.load_time = load_time
        self.unload_time = unload_time
        self.co2_emission = co2_emission
        self.nox_emission = nox_emission
        self.noise_pollution = noise_pollution
        self.land_use = land_use
        self.battery_capacity = battery_capacity
        self.energy_consumption_moving = energy_consumption_moving
        self.energy_consumption_idling = energy_consumption_idling
        self.battery_threshold = battery_threshold
        self.charge_speed = charge_speed

        self.statistics = pd.DataFrame(columns=[
            'timestamp',
            'id',
            'lat',
            'lng',
            'current_trip',
            'current_action',
            'status',
            'battery_level',
            'co2_emission', #g/km
            'nox_emission', #g/km
            'noise_pollution', # db
            'weight'
            ])
        self.cum_statistics = pd.DataFrame(columns=[
            'timestamp',
            'id',
            'name',
            'time_in_system',  # time that has passed since vehicle was initialized (in sec)
            'move',         # % driving (either full or empty)
            'wait',         # % standing still while out-and-about
            'load',         # % loading time of cargo onto vehicle
            'unload',       # % unloading time of cargo out of vehicle (i.e., at customer)
            'idle',          # % time vehicle is idle (no job can be executed)
            'charging',        # % time vehicle is charging
            'failed',          # % time vehicle is failed (note: these 6 percentages should sum up to 100.) 
            'empty_move',       # % driving empty
            'full_move',    # % driving full (e.g., with a parcel)
            'utilization',     # same as 'working'?
            'travel_distance', # total (kilo)meters driven (real)
            'entries',         # total # of cargo loaded onto vehicle
            'exits',            # total # of cargo unloaded from vehicle
            'energy_consumption',
            'co2_emission', #g/km
            'nox_emission', #g/km
            'noise_pollution', # db (does not make sense to have this as a cumulative statistic?)
            'land_use', #m3/hour
            ])
        
        # Initialize cumulative statistics
        start_cum_stats = pd.DataFrame([{'timestamp': datetime.now(),
                                         'move': 0,
                                         'idle': 0,
                                         'load': 0,
                                         'unload': 0,
                                         'wait': 0,
                                         'charging': 0,
                                         'failed': 0,
                                         'empty_driving': 0,
                                         'full_driving':0,
                                         'utilization': 0
                                         }])
        self.cum_statistics = pd.concat([self.cum_statistics,start_cum_stats],ignore_index=True)

        Vehicle._instances.append(self)  # Add the new instance to the list of instances
        Vehicle._total_instances += 1  # Increment the total instances counter

    def assign_to_trip(self, trip: 'Trip') -> bool:
        if trip.status not in ['draft','requested']:
            raise ValueError("Invalid trip status: must be 'requested' or 'draft'")
        else:
            # Assign vehicle to trip
            trip.vehicle = self

            # Update status
            trip.status = 'requested'

            # Set the durations of the 'load' and 'unload' actions and set the expected duration of all actions
            expected_duration = 0
            for action in trip.actions:
                if action.action_type == 'load':
                    action.update_instance_parameter('duration',self.load_time)
                    expected_duration += action.duration
                elif action.action_type == 'unload':
                    action.update_instance_parameter('duration',self.unload_time)
                    expected_duration += action.duration
                elif action.action_type == 'move':
                    expected_duration += action.route.length/self.average_speed
        
            if self.schedule.empty:
                # Set start time to now
                start = datetime.now()

                # Set expected end time based on average speed and route length
                end = start + timedelta(seconds=(expected_duration))
            elif self.current_trip is not None:
                # Vehicle is current busy with a different trip, immediately plan it after expected end of current schedule

                # Set start time to end time of last job in schedule
                start = self.schedule.iloc[-1]['end']

                # Set expected end time based on average speed and route length
                end = start + timedelta(seconds=(expected_duration))
            elif self.status != 'charging' and self.status != 'failed':
                # Vehicle is currently not performing a job and not charging and not failed
                
                # Set start time to now
                start = datetime.now()

                # Set expected end time
                end = start + timedelta(seconds=(expected_duration))               
            
            # Add to end of schedule
            new_task = pd.DataFrame([
                {'vehicle':self.name,
                 'task_id': trip.id, 
                'task_name': trip.name,
                'start':start,
                'end': end,
                'status': trip.status
                }
            ]
            )
            self.schedule = pd.concat([self.schedule,new_task],ignore_index=True)

            self.last_modified = datetime.now()

            return True

    def get_start_time_trip(self, trip_id: str):
        # Find the start value for the given task_id
        start_value = self.schedule.loc[self.schedule['task_id'] == trip_id, 'start'].values
        if len(start_value) > 0:
            return start_value[0]
        else:
            raise ValueError(f"Could not find {trip_id} in schedule {self.schedule} of vehicle {self.name}")
    
    def update_instance_parameter(self, parameter, value):
        """
        Update the parameter of a class instance to a given value.

        Parameters:
        self: object
            The class instance whose parameter needs to be updated.
        parameter: str
            The name of the parameter to be updated.
        value: any
            The new value to set for the parameter.
        """
        setattr(self, parameter, value)
        self.last_modified = datetime.now()

    @classmethod
    def get_by_id(cls, id: str) -> 'Vehicle':
        """
        Get vehicle based on UUID.

        Parameters:
        ----------
        id : str
            String representation of a UUID.

        Returns:
        -------
        Vehicle
            The vehicle instance with the specified UUID, or None if not found.
        """
        return next((i for i in cls._instances if i.id == id), None)

    @classmethod
    def get_by_type(cls, vehicle_type: str) -> List['Vehicle']:
        """
        Get vehicles based on type.

        Parameters:
        ----------
        vehicle_type : str
            The type of vehicles to retrieve.

        Returns:
        -------
        List[Vehicle]
            The list of vehicle instances with the specified type.
        """
        return [i for i in cls._instances if i.vehicle_type == vehicle_type]

    @classmethod
    def get_all_vehicles(cls) -> List['Vehicle']:
        """
        Get all vehicle instances.

        Returns:
        -------
        List[Vehicle]
            List of all vehicle instances.
        """
        return cls._instances

    @classmethod
    def delete_last_x(cls, number: int) -> bool:
        """
        Delete the last 'number' of vehicle instances.

        Parameters:
        ----------
        number : int
            The number of vehicle instances to delete.

        Returns:
        -------
        bool
            True if the operation was successful, False otherwise.
        """
        if len(cls._instances) >= number:
            cls._instances = cls._instances[:-number]
            return True
        else:
            return False

    @classmethod
    def get_by_vehicle_name(cls, name: str) -> 'Vehicle':
        """
        Get vehicle based on name.

        Parameters:
        ----------
        name : str
            Name representation of the vehicle.

        Returns:
        -------
        Vehicle
            The vehicle instance with the specified name, or None if not found.
        """
        return next((vehicle for vehicle in cls._instances if vehicle.name == name), None)
    
    @classmethod
    def get_schedules(cls) -> list[list]:
        # Initialize schedules by getting the schedule of the first vehicle
        schedules = cls._instances[0].schedule #DataFrame

        # Loop over all remaining vehicles and add schedules to DataFrame
        for vehicle in cls._instances[1:]:
            schedules = pd.concat([schedules,vehicle.schedule])

        return schedules

    @classmethod
    def get_total_vehicles(cls) -> int:
        """
        Get the total number of vehicles instances initialized.

        Returns:
        -------
        int
            The total number of vehicles.
        """
        return cls._total_instances
    

class Goods:
    """
    A class to represent Goods.

    Attributes:
    ----------
    VALID_TYPES : list
        A list of valid types for Goods, such as 'transport_equipment' and 'items'.
    VALID_EQUIPMENT_TYPES : list
        A list of valid equipment types for Goods, such as 'trailer', 'box', 'load_carrier', and 'pallet'.
    _instances : list
        A class attribute that stores all instances of Goods.
    _total_instances : int
        A class attribute that stores the total number of Goods instances created.

    Instance Attributes:
    ----------
    id : str
        The unique identifier of the Goods instance.
    name : str, optional
        The name of the Goods instance. Default is an empty string.
    description : str, optional
        A description of the Goods. Default is None.
    remark : str, optional
        Any additional remarks about the Goods. Default is None.
    barcode : str, optional
        The barcode associated with the Goods. Default is None.
    quantity : int, optional
        The quantity of the Goods. Default is None.
    weight : float, optional
        The weight of the Goods. Default is None.
    gross_weight : float, optional
        The gross weight of the Goods. Default is None.
    height : float, optional
        The height of the Goods. Default is None.
    width : float, optional
        The width of the Goods. Default is None.
    length : float, optional
        The length of the Goods. Only applicable for items. Default is None.
    load_meters : float, optional
        The load meters of the Goods. Only applicable for transport_equipment. Default is None.
    contained_goods : list, optional
        A list of Goods contained within this Goods instance. Only applicable for transport_equipment. Default is None.
    equipment_type : str, optional
        The type of equipment associated with the Goods. Only applicable for transport_equipment. Default is an empty string.
    adr : str, optional
        The ADR (Agreement concerning the International Carriage of Dangerous Goods by Road) classification of the Goods. Only applicable for items. Default is None.
    product_type : str, optional
        The product type of the Goods. Only applicable for items. Default is None.
    packaging_material : str, optional
        The packaging material used for the Goods. Only applicable for items. Default is None.
    classification_lines : list, optional
        A list of classification lines associated with the Goods. Default is None.
    actors : list, optional
        The actors associated with the Goods. Default is None.
    constraint : dict, optional
        Any constraints associated with the Goods. Default is None.
    license_plate : str, optional
        The license plate associated with the Goods, if applicable. Only applicable for transport_equipment. Default is None.
    marker : Folium.CircleMarker, optional
        A Folium.CircleMarker object for visualizing the Goods on a map. Default is None.
    creation_date : datetime
        The date and time when the Goods instance was created.
    last_modified : datetime
        The date and time when the Goods instance was last modified.

    Methods:
    -------
    update_instance_parameter(parameter: str, value: any) -> None:
        Updates a specific parameter of the Goods instance to a new value.
    get_by_id(id: str) -> 'Goods':
        Returns the Goods instance matched by the given id.
    get_by_type(goods_type: str) -> List['Goods']:
        Returns a list of Goods instances that match the specified type.
    get_all_goods() -> List['Goods']:
        Returns a list of all Goods instances.
    get_by_goods_name(name: str) -> 'Goods':
        Returns the Goods instance matched by the given name.
    get_total_goods() -> int:
        Returns the total number of Goods instances created.

    Example:
    -------
    goods = Goods(type="transport_equipment", name="Trailer1")
    """


    VALID_TYPES = ['transport_equipment', 'items']
    VALID_EQUIPMENT_TYPES = ['trailer','box','load_carrier','pallet']
    _instances = []
    _total_instances = 0

    def __init__(self, type="transport_equipment", name="", description=None, remark=None, barcode=None, quantity=None, weight=None, gross_weight=None,
                height=None, width=None, length=None, load_meters=None, contained_goods=None, equipment_type="", adr=None, product_type=None, packaging_material=None,
                classification_lines=None, actors=None, constraint=None, license_plate=None, marker=None):
        """
        Initialize a new Goods instance.

        Parameters:
        ----------
        type : str, optional
            The type of the Goods, either 'transport_equipment' or 'items'. Defaults to 'transport_equipment'.
        name : str, optional
            The name of the Goods. Defaults to an empty string.
        description : str, optional
            A brief description of the Goods. Defaults to None.
        remark : str, optional
            Additional remarks about the Goods. Defaults to None.
        barcode : str, optional
            The barcode associated with the Goods. Defaults to None.
        quantity : int, optional
            The quantity of the Goods. Defaults to None.
        weight : float, optional
            The weight of the Goods. Defaults to None.
        gross_weight : float, optional
            The gross weight of the Goods. Defaults to None.
        height : float, optional
            The height of the Goods. Defaults to None.
        width : float, optional
            The width of the Goods. Defaults to None.
        length : float, optional
            The length of the Goods. Only applicable for items. Defaults to None.
        load_meters : float, optional
            The load meters of the Goods. Only applicable for transport_equipment. Defaults to None.
        contained_goods : list, optional
            A list of other Goods instances contained within this Goods instance. Only applicable for transport_equipment. Defaults to None.
        equipment_type : str, optional
            The type of equipment associated with the Goods, such as 'trailer' or 'box'. Only applicable for transport_equipment. Defaults to an empty string.
        adr : str, optional
            The ADR classification for hazardous Goods. Only applicable for items. Defaults to None.
        product_type : str, optional
            The product type of the Goods. Only applicable for items. Defaults to None.
        packaging_material : str, optional
            The material used for packaging the Goods. Only applicable for items. Defaults to None.
        classification_lines : list, optional
            A list of classification lines associated with the Goods. Defaults to None.
        actors : list, optional
            A list of actors (e.g., companies or individuals) associated with the Goods. Defaults to None.
        constraint : dict, optional
            Constraints associated with the Goods (e.g., legal or operational constraints). Defaults to None.
        license_plate : str, optional
            The license plate number, if applicable to the Goods. Only applicable for transport_equipment. Defaults to None.
        marker : Folium.CircleMarker, optional
            A Folium.CircleMarker object for visualizing the Goods on a map. Defaults to None.

        Raises:
        -------
        ValueError
            If the provided type is not a valid Goods type.
            If the provided equipment_type is not a valid equipment type.

        Example:
        -------
        goods = Goods(type="items", name="Pallet", weight=150.0)
        """

        if type not in Goods.VALID_TYPES:
            raise ValueError(f"Type '{type}' is not a Goods  type. Valid Goods types are: {', '.join(Goods.VALID_TYPES)}")
        if equipment_type not in Goods.VALID_EQUIPMENT_TYPES:
                raise ValueError(f"Equipment type '{equipment_type}' is not an Equipment type. Valid Equipment types are: {', '.join(Goods.VALID_EQUIPMENT_TYPES)}")
        
        # OTM
        self.id = str(uuid.uuid4())  # Generate a unique identifier for the vehicle
        self.name = name
        self.creation_date = datetime.now()
        self.last_modified = datetime.now()
        self.description = description
        self.remark = remark
        self.barcode = barcode
        self.quantity = quantity
        self.weight = weight
        self.gross_weight = gross_weight
        self.width = width
        self.height = height
        self.length = length # only for items
        self.adr = adr # only for items 
        self.product_type = product_type # only for items
        self.packaging_material = packaging_material # only for items
        self.load_meters = load_meters # only for transport_equipment
        self.contained_goods = contained_goods # only for transport_equipment
        self.equipment_type = equipment_type # only for transport_equipment
        self.license_plate = license_plate # only for transport_equipment
        self.classification_lines = classification_lines
        self.actors = actors
        self.constraint = constraint

        # Custom
        self.marker = marker  # Folium.CircleMarker object for visualization

        Goods._instances.append(self)  # Add the new instance to the list of instances
        Goods._total_instances += 1  # Increment the total instances counter
    
    @classmethod
    def get_by_id(cls, id: str) -> 'Goods':
        """
        Retrieve a Goods instance by its unique identifier.

        Parameters:
        ----------
        id : str
            The unique identifier (UUID) of the Goods instance.

        Returns:
        -------
        Goods
            The Goods instance with the specified id, or None if not found.

        Example:
        -------
        goods = Goods.get_by_id("123e4567-e89b-12d3-a456-426614174000")
        """
        return next((i for i in cls._instances if i.id == id), None)


    @classmethod
    def get_by_type(cls, goods_type: str) -> List['Goods']:
        """
        Retrieve a list of Goods instances by their type.

        Parameters:
        ----------
        goods_type : str
            The type of Goods to filter by (e.g., 'transport_equipment', 'items').

        Returns:
        -------
        List[Goods]
            A list of Goods instances that match the specified type.

        Example:
        -------
        goods_list = Goods.get_by_type("items")
        """
        return [i for i in cls._instances if i.type == goods_type]


    @classmethod
    def get_all_goods(cls) -> List['Goods']:
        """
        Retrieve all Goods instances.

        Returns:
        -------
        List[Goods]
            A list of all Goods instances created.

        Example:
        -------
        all_goods = Goods.get_all_goods()
        """
        return cls._instances


    @classmethod
    def get_by_goods_name(cls, name: str) -> 'Goods':
        """
        Retrieve a Goods instance by its name.

        Parameters:
        ----------
        name : str
            The name of the Goods instance.

        Returns:
        -------
        Goods
            The Goods instance with the specified name, or None if not found.

        Example:
        -------
        goods = Goods.get_by_goods_name("Pallet")
        """
        return next((goods for goods in cls._instances if goods.name == name), None)


    @classmethod
    def get_total_goods(cls) -> int:
        """
        Get the total number of Goods instances created.

        Returns:
        -------
        int
            The total number of Goods instances.

        Example:
        -------
        total_goods = Goods.get_total_goods()
        """
        return cls._total_instances


    def update_instance_parameter(self, parameter: str, value: any) -> None:
        """
        Update a specific parameter of the Goods instance.

        Parameters:
        ----------
        parameter : str
            The name of the parameter to update.
        value : any
            The new value to assign to the parameter.

        Returns:
        -------
        None

        Example:
        -------
        goods.update_instance_parameter("weight", 200.0)
        """
        setattr(self, parameter, value)
        self.last_modified = datetime.now()
