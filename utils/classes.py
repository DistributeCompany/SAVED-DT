import uuid
import pandas as pd

from folium import Marker
from typing import List, Optional, Any
from datetime import datetime, timedelta

class Action:
    """
    A class to represent an Action. NOTE: 'move' only.

    Attributes:
    ----------
    _instances : list
        A class attribute that stores all instances of Action.
    _total_instances : int
        A class attribute that stores the total number of Action instances created.

    Instance Attributes:
    ----------
    action_type : str, optional
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
    time_format : str, optional
        The format of the time attributes. Default is "dateTime".
    start_time : datetime, optional
        The start time of the action. Default is None.
    end_time : datetime, optional
        The end time of the action. Default is None.
    route : Route, optional
        The route associated with the action. Default is None.
    constraint : Constraint, optional
        The constraint associated with the action. Default is None.
    creation_date : datetime
        The date and time when the action was created.
    last_modified : datetime
        The date and time when the action was last modified.
    id : str
        The unique identifier of the action.

    Class Methods:
    -------
    get_by_id(id: str) -> List[Action]
        Returns a list of action instances matched by id.
    get_all_actions() -> List[Action]
        Returns a list of all actions.
    get_total_actions() -> int
        Returns the total number of actions created.
    delete_all_instances()
        Deletes all action instances.

    Example:
    -------
    action = Action(action_type="move", name=f"Action {Action.get_total_actions()}")
    """

    VALID_LIFECYCLES: List[str] = ["requested", "planned", "projected", "actual", "realized"]
    VALID_ACTION_TYPES: List[str] = ["move"]  # Only "move" is allowed for now

    _instances: List['Action'] = []
    _total_instances: int = 0

    def __init__(self,
                 sequence_nr: Optional[int] = None,
                 action_type: str = "move",
                 name: str = "",
                 lifecycle: str = "requested",
                 transport_mode: Optional[str] = None,
                 trip: Optional['Trip'] = None,
                 _from: Optional['Location'] = None,
                 _to: Optional['Location'] = None,
                 time_format: str = "dateTime",
                 duration: Optional[float] = None,
                 start_time: Optional[datetime] = None,
                 end_time: Optional[datetime] = None,
                 location: Optional['Location'] = None,
                 route: Optional['Route'] = None,
                 constraint: Optional['Constraint'] = None,
                 progress: int = 0) -> None:
        """
        Initialize a new Action instance.

        Parameters:
        ----------
        sequence_nr : int, optional
            The sequence number of the action. Default is None.
        action_type : str, optional
            The type of action. Must be "move". Default is "move".
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
        time_format : str, optional
            The format of the time attributes. Default is "dateTime".
        duration : float, optional
            The duration of the action (only used for other action types; not applicable for "move"). Default is None.
        start_time : datetime, optional
            The start time of the action. Default is None.
        end_time : datetime, optional
            The end time of the action. Default is None.
        location : Location, optional
            The location associated with the action (only used for other action types). Default is None.
        route : Route, optional
            The route associated with the action. Default is None.
        constraint : Constraint, optional
            The constraint associated with the action. Default is None.
        progress : int, optional
            The progress of the action. Default is 0.

        Raises:
        ------
        ValueError:
            If 'lifecycle' or 'action_type' is not in the list of supported values.
        """
        if lifecycle not in Action.VALID_LIFECYCLES:
            raise ValueError(f"Lifecycle '{lifecycle}' is not valid. Valid lifecycles are: {', '.join(Action.VALID_LIFECYCLES)}")
        if action_type not in Action.VALID_ACTION_TYPES:
            raise ValueError(f"Action type '{action_type}' is not valid. Valid types are: {', '.join(Action.VALID_ACTION_TYPES)}")
        
        # Core attributes
        self.id: str = str(uuid.uuid4())  # Generate a unique identifier for the action
        self.name: str = name
        self.creation_date: datetime = datetime.now()
        self.last_modified: datetime = datetime.now()
        self.action_type: str = action_type  # Only "move" is currently allowed
        self.lifecycle: str = lifecycle
        self.transport_mode: Optional[str] = transport_mode
        self.sequence_nr: Optional[int] = sequence_nr
        self.trip: Optional['Trip'] = trip
        self._from: Optional['Location'] = _from
        self._to: Optional['Location'] = _to
        self.time_format: str = time_format
        self.duration: Optional[float] = duration  # Only applicable when 'time_format' is set to 'duration'
        self.location: Optional['Location'] = location  # Not used for "move"
        self.start_time: Optional[datetime] = start_time
        self.end_time: Optional[datetime] = end_time
        self.route: Optional['Route'] = route
        self.constraint: Optional['Constraint'] = constraint

        # Custom attributes
        self.progress: int = progress

        # Register the instance
        Action._instances.append(self)
        Action._total_instances += 1

    def update_instance_parameter(self, parameter: str, value: Any) -> None:
        """
        Update the parameter of this action instance to a given value.

        Parameters:
        ----------
        parameter : str
            The name of the parameter to update.
        value : any
            The new value for the parameter.
        """
        setattr(self, parameter, value)
        self.last_modified = datetime.now()

    @classmethod
    def get_by_id(cls, id: str) -> List['Action']:
        """
        Retrieve the action instances with the specified UUID.

        Parameters:
        ----------
        id : str
            The unique identifier (UUID) of the action.

        Returns:
        -------
        List[Action]
            A list of Action instances with the specified UUID, or an empty list if not found.
        """
        return [action for action in cls._instances if action.id == id]

    @classmethod
    def get_all_actions(cls) -> List['Action']:
        """
        Retrieve all action instances.

        Returns:
        -------
        List[Action]
            A list of all Action instances.
        """
        return cls._instances.copy()

    @classmethod
    def get_total_actions(cls) -> int:
        """
        Retrieve the total number of action instances created.

        Returns:
        -------
        int
            The total number of actions.
        """
        return cls._total_instances

    @classmethod
    def delete_all_instances(cls) -> None:
        """
        Delete all action instances.

        This method clears the list of action instances and resets the total instances counter.
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
    id : str
        The unique identifier of the actor.
    name : str
        The name of the actor.
    locations : list
        A list containing the locations associated with the actor.
    creation_date : datetime
        The date and time when the actor was created.
    last_modified : datetime
        The date and time when the actor was last modified.

    Class Methods:
    -------
    get_by_id(id: str) -> List[Actor]
        Retrieve the actor instances with the specified UUID.
    get_all_actors() -> List[Actor]
        Retrieve a list of all actor instances.
    get_total_actors() -> int
        Retrieve the total number of actors created.
    delete_all_instances()
        Delete all actor instances.

    Example:
    -------
    actor = Actor(locations=[some_location], name=f"Actor {Actor.get_total_actors()}")
    """

    _instances: List['Actor'] = []
    _total_instances: int = 0

    def __init__(self, locations: List['Location'], name: str = "") -> None:
        """
        Initialize a new Actor instance.

        Parameters:
        ----------
        locations : list
            A list of Location objects associated with the actor.
        name : str, optional
            The name of the actor. Default is "".
        """
        self.id: str = str(uuid.uuid4())  # Generate a unique identifier for the actor
        self.name: str = name
        self.creation_date: datetime = datetime.now()
        self.last_modified: datetime = datetime.now()
        self.locations: List['Location'] = locations  # List of associated locations

        Actor._instances.append(self)  # Add the new instance to the list of instances
        Actor._total_instances += 1  # Increment the total instances counter

    def __repr__(self) -> str:
        """
        Return an unambiguous string representation of the Actor instance.

        Returns:
        -------
        str
            A string representation of the Actor instance.
        """
        return f"Actor(id='{self.id}', name='{self.name}')"

    @classmethod
    def get_by_id(cls, id: str) -> List['Actor']:
        """
        Retrieve the actor instances with the specified UUID.

        Parameters:
        ----------
        id : str
            The unique identifier (UUID) of the actor.

        Returns:
        -------
        List[Actor]
            A list of Actor instances with the specified UUID, or an empty list if not found.
        """
        return [actor for actor in cls._instances if actor.id == id]

    @classmethod
    def get_all_actors(cls) -> List['Actor']:
        """
        Retrieve all actor instances.

        Returns:
        -------
        List[Actor]
            A list of all Actor instances.
        """
        return cls._instances.copy()

    @classmethod
    def get_total_actors(cls) -> int:
        """
        Retrieve the total number of actor instances created.

        Returns:
        -------
        int
            The total number of actors.
        """
        return cls._total_instances

    @classmethod
    def delete_all_instances(cls) -> None:
        """
        Delete all actor instances.

        This method clears the list of actor instances and resets the total instances counter.
        """
        cls._instances.clear()
        cls._total_instances = 0

class Constraint:
    '''
    TODO: Implement Constraint class. See https://otm5.opentripmodel.org/ for details. 
    '''
    pass

class Goods:
    """
    NOTE: CURRENTLY NOT IN USE. Might be useful to model chassis/containers in the model. 

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
    goods_type : str
        The type of the Goods, either 'transport_equipment' or 'items'.
    name : str
        The name of the Goods. Default is an empty string.
    description : Optional[str]
        A description of the Goods. Default is None.
    remark : Optional[str]
        Additional remarks about the Goods. Default is None.
    barcode : Optional[str]
        The barcode associated with the Goods. Default is None.
    quantity : Optional[int]
        The quantity of the Goods. Default is None.
    weight : Optional[float]
        The weight of the Goods. Default is None.
    gross_weight : Optional[float]
        The gross weight of the Goods. Default is None.
    height : Optional[float]
        The height of the Goods. Default is None.
    width : Optional[float]
        The width of the Goods. Default is None.
    length : Optional[float]
        The length of the Goods (only applicable for items). Default is None.
    load_meters : Optional[float]
        The load meters of the Goods (only applicable for transport_equipment). Default is None.
    contained_goods : Optional[List[Goods]]
        A list of Goods contained within this Goods instance (only applicable for transport_equipment). Default is None.
    equipment_type : str
        The type of equipment associated with the Goods (only applicable for transport_equipment). Default is an empty string.
    adr : Optional[str]
        The ADR classification for hazardous Goods (only applicable for items). Default is None.
    product_type : Optional[str]
        The product type of the Goods (only applicable for items). Default is None.
    packaging_material : Optional[str]
        The packaging material used for the Goods (only applicable for items). Default is None.
    classification_lines : Optional[List[str]]
        A list of classification lines associated with the Goods. Default is None.
    actors : Optional[List[Actor]]
        A list of actors associated with the Goods. Default is None.
    constraint : Optional[Constraint]
        Constraints associated with the Goods. Default is None.
    license_plate : Optional[str]
        The license plate associated with the Goods (only applicable for transport_equipment). Default is None.
    marker : Optional['Folium.CircleMarker']
        A Folium.CircleMarker object for visualizing the Goods on a map. Default is None.
    creation_date : datetime
        The date and time when the Goods instance was created.
    last_modified : datetime
        The date and time when the Goods instance was last modified.

    Methods:
    -------
    update_instance_parameter(parameter: str, value: any) -> None:
        Updates a specific parameter of the Goods instance to a new value.
    get_by_id(id: str) -> Optional[Goods]:
        Returns the Goods instance matched by the given id.
    get_by_type(goods_type: str) -> List[Goods]:
        Returns a list of Goods instances that match the specified type.
    get_all_goods() -> List[Goods]:
        Returns a list of all Goods instances.
    get_by_goods_name(name: str) -> Optional[Goods]:
        Returns the Goods instance matched by the given name.
    get_total_goods() -> int:
        Returns the total number of Goods instances created.

    Example:
    -------
    goods = Goods(goods_type="transport_equipment", name="Trailer1")
    """

    VALID_TYPES: List[str] = ['transport_equipment', 'items']
    VALID_EQUIPMENT_TYPES: List[str] = ['trailer', 'box', 'load_carrier', 'pallet']
    _instances: List['Goods'] = []
    _total_instances: int = 0

    def __init__(self,
                 goods_type: str = "transport_equipment",
                 name: str = "",
                 description: Optional[str] = None,
                 remark: Optional[str] = None,
                 barcode: Optional[str] = None,
                 quantity: Optional[int] = None,
                 weight: Optional[float] = None,
                 gross_weight: Optional[float] = None,
                 height: Optional[float] = None,
                 width: Optional[float] = None,
                 length: Optional[float] = None,
                 load_meters: Optional[float] = None,
                 contained_goods: Optional[List['Goods']] = None,
                 equipment_type: str = "",
                 adr: Optional[str] = None,
                 product_type: Optional[str] = None,
                 packaging_material: Optional[str] = None,
                 classification_lines: Optional[List[str]] = None,
                 actors: Optional[List['Actor']] = None,
                 constraint: Optional['Constraint'] = None,
                 license_plate: Optional[str] = None,
                 marker: Optional['Marker'] = None) -> None:
        """
        Initialize a new Goods instance.

        Parameters:
        ----------
        goods_type : str, optional
            The type of the Goods, either 'transport_equipment' or 'items'. Defaults to 'transport_equipment'.
        name : str, optional
            The name of the Goods. Defaults to an empty string.
        description : str, optional
            A description of the Goods. Defaults to None.
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
            The length of the Goods (only applicable for items). Defaults to None.
        load_meters : float, optional
            The load meters of the Goods (only applicable for transport_equipment). Defaults to None.
        contained_goods : list, optional
            A list of Goods instances contained within this Goods instance (only applicable for transport_equipment). Defaults to None.
        equipment_type : str, optional
            The type of equipment associated with the Goods (only applicable for transport_equipment). Defaults to an empty string.
        adr : str, optional
            The ADR classification for hazardous Goods (only applicable for items). Defaults to None.
        product_type : str, optional
            The product type of the Goods (only applicable for items). Defaults to None.
        packaging_material : str, optional
            The packaging material used for the Goods (only applicable for items). Defaults to None.
        classification_lines : list, optional
            A list of classification lines associated with the Goods. Defaults to None.
        actors : list, optional
            A list of actors associated with the Goods. Defaults to None.
        constraint : Constraint, optional
            Constraints associated with the Goods. Defaults to None.
        license_plate : str, optional
            The license plate associated with the Goods (only applicable for transport_equipment). Defaults to None.
        marker : Folium.Marker, optional
            A Folium.Marker object for visualizing the Goods on a map. Defaults to None.

        Raises:
        -------
        ValueError:
            If the provided goods_type is not valid.
            If goods_type is 'transport_equipment' and the provided equipment_type is not in VALID_EQUIPMENT_TYPES.

        Example:
        -------
        goods = Goods(goods_type="transport_equipment", name="Trailer1")
        """
        if goods_type not in Goods.VALID_TYPES:
            raise ValueError(f"Goods type '{goods_type}' is not valid. Valid types are: {', '.join(Goods.VALID_TYPES)}")
        # Only validate equipment_type if goods_type is 'transport_equipment'
        if goods_type == 'transport_equipment' and equipment_type not in Goods.VALID_EQUIPMENT_TYPES:
            raise ValueError(f"Equipment type '{equipment_type}' is not valid. Valid equipment types are: {', '.join(Goods.VALID_EQUIPMENT_TYPES)}")
        
        self.id: str = str(uuid.uuid4())
        self.goods_type: str = goods_type
        self.name: str = name
        self.creation_date: datetime = datetime.now()
        self.last_modified: datetime = datetime.now()
        self.description: Optional[str] = description
        self.remark: Optional[str] = remark
        self.barcode: Optional[str] = barcode
        self.quantity: Optional[int] = quantity
        self.weight: Optional[float] = weight
        self.gross_weight: Optional[float] = gross_weight
        self.height: Optional[float] = height
        self.width: Optional[float] = width
        self.length: Optional[float] = length
        self.load_meters: Optional[float] = load_meters
        self.contained_goods: Optional[List['Goods']] = contained_goods
        self.equipment_type: str = equipment_type
        self.adr: Optional[str] = adr
        self.product_type: Optional[str] = product_type
        self.packaging_material: Optional[str] = packaging_material
        self.classification_lines: Optional[List[str]] = classification_lines
        self.actors: List['Actor'] = actors
        self.constraint: Optional['Constraint'] = constraint
        self.license_plate: Optional[str] = license_plate
        self.marker: Optional['Marker'] = marker

        Goods._instances.append(self)
        Goods._total_instances += 1

    def update_instance_parameter(self, parameter: str, value: Any) -> None:
        """
        Update a specific parameter of the Goods instance to a new value.

        Parameters:
        ----------
        parameter : str
            The name of the parameter to update.
        value : any
            The new value to assign to the parameter.

        Example:
        -------
        goods.update_instance_parameter("weight", 200.0)
        """
        setattr(self, parameter, value)
        self.last_modified = datetime.now()

    @classmethod
    def get_by_id(cls, id: str) -> Optional['Goods']:
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
        return next((g for g in cls._instances if g.id == id), None)

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
        return [g for g in cls._instances if g.goods_type == goods_type]

    @classmethod
    def get_all_goods(cls) -> List['Goods']:
        """
        Retrieve all Goods instances.

        Returns:
        -------
        List[Goods]
            A list of all Goods instances.

        Example:
        -------
        all_goods = Goods.get_all_goods()
        """
        return cls._instances.copy()

    @classmethod
    def get_by_goods_name(cls, name: str) -> Optional['Goods']:
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
        return next((g for g in cls._instances if g.name == name), None)

    @classmethod
    def get_total_goods(cls) -> int:
        """
        Retrieve the total number of Goods instances created.

        Returns:
        -------
        int
            The total number of Goods instances.

        Example:
        -------
        total_goods = Goods.get_total_goods()
        """
        return cls._total_instances
    
class Location:
    """
    A class to represent a geographical location.

    Attributes:
    ----------
    _instances : list
        A class attribute that stores all instances of Location.
    _total_instances : int
        A class attribute that stores the total number of Location instances created.

    Instance Attributes:
    ----------
    id : str
        The unique identifier for the location.
    georeference : list
        [latitude, longitude] of the location.
    name : str
        The name of the location.
    location_type : str
        The type of the location (e.g., 'customer', 'warehouse').
    actors : list
        The actors associated with the location.
    actions : list
        The actions associated with the location.
    constraint : Constraint
        The constraints related to the location.
    marker : folium.Marker
        The marker for visualization purposes.
    creation_date : datetime
        The timestamp when the location was created.
    last_modified : datetime
        The timestamp when the location was last modified.

    Class Methods:
    -------
    get_by_id(id: str) -> Location
        Retrieve a location instance by its unique identifier.
    get_by_name(name: str) -> Location
        Retrieve a location instance by its name.
    get_by_georeference(georeference: list) -> Location
        Retrieve a location instance by its georeference.
    get_by_type(location_type: str) -> list
        Retrieve all location instances of a specific type.
    get_all_locations() -> list
        Retrieve all location instances.
    get_total_locations() -> int
        Retrieve the total number of location instances.
    delete_all_by_type(location_type: str)
        Delete all location instances of a specific type.
    delete_all_customers()
        Delete all location instances with type 'customer'.

    Example:
    -------
    location = Location(georeference=[52.3217964912184, 6.63325033523122], name="BOL_DG_01")
    """

    _instances: List['Location'] = []
    _total_instances: int = 0

    def __init__(self,
                 georeference: List[float],
                 name: str = "",
                 marker: Marker = None,
                 location_type: str = "customer",
                 actors: Optional[List['Actor']] = None,
                 actions: Optional[List['Action']] = None,
                 constraint: Optional['Constraint'] = None) -> None:
        """
        Initialize a new Location instance.

        Parameters:
        ----------
        georeference : list
            [latitude, longitude] of the location.
        name : str, optional
            The name of the location. Default is "".
        marker : folium.Marker, optional
            The marker for visualization purposes. Default is None.
        location_type : str, optional
            The type of the location (e.g., 'customer', 'warehouse'). Default is "customer".
        actors : list, optional
            The actors associated with the location. Default is None.
        actions : list, optional
            The actions associated with the location. Default is None.
        constraint : Constraint, optional
            The constraints related to the location. Default is None.

        """
        self.id: str = str(uuid.uuid4())  # Unique identifier for the location
        self.georeference: List[float] = georeference
        self.name: str = name
        self.location_type: str = location_type
        self.actors: List['Actor'] = actors if actors is not None else []
        self.actions: List['Action'] = actions if actions is not None else []
        self.constraint: Optional['Constraint'] = constraint
        self.marker: Marker = marker
        self.creation_date: datetime = datetime.now()
        self.last_modified: datetime = datetime.now()

        # Register the new instance
        Location._instances.append(self)
        Location._total_instances += 1

    def __repr__(self) -> str:
        """
        Return an unambiguous string representation of the Location instance.

        Returns:
        -------
        str
            A string representation of the instance.
        """
        return (f"Location(id='{self.id}', name='{self.name}', "
                f"location_type='{self.location_type}', georeference={self.georeference})")

    @classmethod
    def get_by_id(cls, id: str) -> Optional['Location']:
        """
        Retrieve a location instance by its unique identifier.

        Parameters:
        ----------
        id : str
            The unique identifier (UUID) of the location.

        Returns:
        -------
        Location
            The matching Location instance, or None if not found.
        """
        return next((location for location in cls._instances if location.id == id), None)

    @classmethod
    def get_by_name(cls, name: str) -> Optional['Location']:
        """
        Retrieve a location instance by its name.

        Parameters:
        ----------
        name : str
            The name of the location.

        Returns:
        -------
        Location
            The matching Location instance, or None if not found.
        """
        return next((location for location in cls._instances if location.name == name), None)

    @classmethod
    def get_by_georeference(cls, georeference: List[float]) -> Optional['Location']:
        """
        Retrieve a location instance by its georeference.

        Parameters:
        ----------
        georeference : list
            [latitude, longitude] of the location.

        Returns:
        -------
        Location
            The matching Location instance, or None if not found.
        """
        return next((location for location in cls._instances if location.georeference == georeference), None)

    @classmethod
    def get_by_type(cls, location_type: str) -> List['Location']:
        """
        Retrieve all location instances of a specific type.

        Parameters:
        ----------
        location_type : str
            The type of locations to retrieve.

        Returns:
        -------
        list
            A list of Location instances matching the specified type.
        """
        return [location for location in cls._instances if location.location_type == location_type]

    @classmethod
    def get_all_locations(cls) -> List['Location']:
        """
        Retrieve all location instances.

        Returns:
        -------
        list
            A list of all Location instances.
        """
        # Return a copy to prevent external modifications to the internal list
        return cls._instances.copy()

    @classmethod
    def get_total_locations(cls) -> int:
        """
        Retrieve the total number of location instances created.

        Returns:
        -------
        int
            The total number of locations.
        """
        return cls._total_instances

    @classmethod
    def delete_all_by_type(cls, location_type: str) -> None:
        """
        Delete all location instances of a specific type.

        Parameters:
        ----------
        location_type : str
            The type of locations to delete.
        """
        cls._instances = [location for location in cls._instances if location.location_type != location_type]
        cls._total_instances = len(cls._instances)

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
    id : str
        The unique identifier of the route.
    georeference : list
        List with coordinates of the route, used to plot a polyline on a map.
    name : str
        The name of the route.
    actors : list, optional
        The actors associated with this route.
    length : float, optional
        The length of the route in meters.
    nodes : list, optional
        The list of NodeIDs representing the origin and destination of the route. See get_nearest_nodes() in utils/osmnx.py.
    polyline : Folium.PolyLine, optional
        The Folium.PolyLine object used for visualization on a map.
    coordinates : list of tuple, optional
        The list containing the coordinates describing the polyline.
    creation_date : datetime
        The date and time when the route was created.
    last_modified : datetime
        The date and time when the route was last modified.

    Class Methods:
    -------
    get_by_id(id: str) -> List[Route]
        Returns a list of route instances matched by id.
    get_all_routes() -> List[Route]
        Returns a list of all routes.
    get_total_routes() -> int
        Returns the total number of routes created.
    delete_all_instances()
        Deletes all route instances.

    Example:
    -------
    route = Route(georeference=[[52.3229271502237, 6.63141817575306], [52.322017377683, 6.63347914168028]], name=f"{origin_location.name} to {destination_location.name}")
    """

    _instances: list = []
    _total_instances: int = 0

    def __init__(self,
                 georeference: list,
                 name: str = "",
                 actors: Optional[List['Actor']] = None,
                 length: float = None,
                 nodes: list = None,  # List of node IDs from the osmnx library
                 polyline=None,
                 coordinates: list = None) -> None:
        """
        Initialize a new Route instance.

        Parameters:
        ----------
        georeference : list
            List with coordinates of the route.
        name : str, optional
            The name of the route. Default is "".
        actors : list, optional
            The actors associated with this route. Default is None.
        length : float, optional
            The length of the route in meters. Default is None.
        nodes : list, optional
            The list of NodeIDs representing the origin and destination of the route. See get_nearest_nodes() in utils/osmnx.py.
        polyline : Folium.PolyLine, optional
            The Folium.PolyLine object used for visualization on a map. Default is None.
        coordinates : list of tuple, optional
            The list containing the coordinates describing the polyline. Default is None.
        """
        self.id: str = str(uuid.uuid4())  # Generate a unique identifier for the route
        self.georeference: list = georeference
        self.name: str = name
        self.actors: List['Actor'] = actors if actors is not None else []
        self.length: float = length
        self.nodes: list = nodes
        self.polyline = polyline
        self.coordinates: list = coordinates
        self.creation_date = datetime.now()
        self.last_modified = datetime.now()

        Route._instances.append(self)  # Add the new instance to the list of instances
        Route._total_instances += 1      # Increment the total instances counter

    def __repr__(self) -> str:
        """
        Return an unambiguous string representation of the Route instance.

        Returns:
        -------
        str
            A string representation of the Route instance.
        """
        return f"Route(id='{self.id}', name='{self.name}')"

    @classmethod
    def get_by_id(cls, id: str) -> list:
        """
        Retrieve the route instances with the specified UUID.

        Parameters:
        ----------
        id : str
            String representation of a UUID.

        Returns:
        -------
        list
            The route instances with the specified UUID, or an empty list if not found.
        """
        return [route for route in cls._instances if route.id == id]

    @classmethod
    def get_all_routes(cls) -> list:
        """
        Retrieve all route instances.

        Returns:
        -------
        list
            A list of all Route instances.
        """
        return cls._instances.copy()

    @classmethod
    def get_total_routes(cls) -> int:
        """
        Retrieve the total number of route instances created.

        Returns:
        -------
        int
            The total number of routes.
        """
        return cls._total_instances

    @classmethod
    def delete_all_instances(cls) -> None:
        """
        Delete all route instances.

        This method clears the list of route instances and resets the total instances counter.
        """
        cls._instances.clear()
        cls._total_instances = 0

class Sensor:
    '''
    TODO: Implement Sensor class. See https://otm5.opentripmodel.org/ for details. 

    Can be useful to represent real-world sensors (either on-vehicle or on-site) in a Digital Shadow / Digital Twin setting.
    '''
    pass

class Trip:
    """
    A class to represent a Trip.

    Attributes:
    ----------
    VALID_STATUS : list
        A class attribute that stores all allowed values for the instance attribute 'status'.
    VALID_TRANSPORT_MODES : list
        A class attribute that stores all allowed values for the instance attribute 'transport_mode'.
    _instances : list
        A class attribute that stores all instances of Trip.
    _total_instances : int
        A class attribute that stores the total number of Trip instances created.

    Instance Attributes:
    ----------
    id : str
        The unique identifier of the trip.
    name : str
        The name of the Trip.
    status : str
        The status of the trip (e.g., 'draft', 'requested', 'confirmed', 'in_transit', 'completed', 'cancelled', 'accepted', 'modified').
    transport_mode : str
        The method of transport used for the trip (e.g., 'maritime', 'road', 'rail', 'air', 'inlandWaterway').
    vehicle : Vehicle
        The vehicle assigned to this trip.
    actors : list
        The actors associated with this trip.
    actions : list
        The actions associated with this trip.
    constraint : Constraint
        The constraint associated with this trip.
    marker : folium.Marker
        The Folium.Marker object of the destination of this trip.
    progress : int
        An integer denoting how far the trip is completed [0-100%].
    creation_date : datetime
        The date and time when the trip was created.
    last_modified : datetime
        The date and time when the trip was last modified.

    Class Methods:
    -------
    get_by_id(id: str) -> Trip
        Retrieve the trip instance matched by id.
    get_by_name(name: str) -> Trip
        Retrieve the trip instance matched by name.
    get_by_status(status: str) -> list
        Retrieve all trip instances with a given status.
    get_all_trips() -> list
        Retrieve a list of all trip instances.
    get_total_trips() -> int
        Retrieve the total number of trips created.
    delete_all_instances()
        Delete all trip instances.

    Instance Methods:
    -------
    add_action(action: Action) -> bool
        Adds an action to the trip instance.
    get_actions() -> list
        Returns the list of actions associated with the trip.
    get_total_route_length() -> int
        Calculates and returns the total route length of the trip.
    update_instance_parameter(parameter: str, value: any)
        Updates a given parameter of the trip instance.

    Example:
    -------
    trip = Trip(name=f"Trip {Trip.get_total_trips()}")
    """

    VALID_STATUS: List[str] = ['draft', 'requested', 'confirmed', 'in_transit', 'completed', 'cancelled', 'accepted', 'modified']
    VALID_TRANSPORT_MODES: List[str] = ['maritime', 'road', 'rail', 'air', 'inlandWaterway']
    _instances: List['Trip'] = []
    _total_instances: int = 0

    def __init__(self,
                 name: str = "",
                 status: str = "draft",
                 transport_mode: str = "road",
                 marker: Optional['Marker'] = None,
                 vehicle: Optional['Vehicle'] = None,
                 actors: Optional[List['Actor']] = None,
                 actions: Optional[List['Action']] = None,
                 constraint: Optional['Constraint'] = None,
                 progress: int = 0) -> None:
        """
        Initialize a new Trip instance.

        Parameters:
        ----------
        name : str, optional
            The name of the Trip. Default is "".
        status : str, optional
            The status of the trip (e.g., 'draft', 'requested', 'confirmed', 'in_transit', 'completed', 'cancelled', 'accepted', 'modified'). Default is 'draft'.
        transport_mode : str, optional
            The method of transport used for the trip (e.g., 'maritime', 'road', 'rail', 'air', 'inlandWaterway'). Default is 'road'.
        marker : folium.Marker, optional
            The Folium.Marker object of the destination of this trip. Default is None.
        vehicle : Vehicle, optional
            The vehicle assigned to this trip. Default is None.
        actors : list, optional
            The actors associated with this trip. Default is [].
        actions : list, optional
            The actions associated with this trip. Default is [].
        constraint : Constraint, optional
            The constraint associated with this trip. Default is None.
        progress : int, optional
            An integer denoting how far the trip is completed [0-100%]. Default is 0.

        Raises:
        ------
        ValueError:
            If 'status' or 'transport_mode' is not in the list of supported values.
        """
        if status not in Trip.VALID_STATUS:
            raise ValueError(f"Status '{status}' is not a valid status. Valid statuses are: {', '.join(Trip.VALID_STATUS)}")
        if transport_mode not in Trip.VALID_TRANSPORT_MODES:
            raise ValueError(f"Transport mode '{transport_mode}' is not a valid mode. Valid modes are: {', '.join(Trip.VALID_TRANSPORT_MODES)}")
        
        self.id: str = str(uuid.uuid4())  # Generate a unique identifier for the trip
        self.name: str = name
        self.status: str = status
        self.transport_mode: str = transport_mode
        self.vehicle: Optional['Vehicle'] = vehicle
        self.actors: List['Actor'] = actors if actors is not None else []
        self.actions: List['Action'] = actions if actions is not None else []
        self.constraint: Optional['Constraint'] = constraint
        self.creation_date: datetime = datetime.now()
        self.last_modified: datetime = datetime.now()

        self.marker: Optional[Marker] = marker
        self.progress: int = progress

        Trip._instances.append(self)  # Add the new instance to the list of instances
        Trip._total_instances += 1  # Increment the total instances counter

    def get_actions(self) -> List['Action']:
        """
        Retrieve the list of actions associated with this trip.

        Returns:
        -------
        list
            A list of actions.
        """
        return self.actions

    def add_action(self, action: 'Action') -> bool:
        """
        Add an action to the trip instance.

        Parameters:
        ----------
        action : Action
            The action to add.

        Returns:
        -------
        bool
            True if the action was successfully added.
        """
        self.actions.append(action)
        self.last_modified = datetime.now()
        return True

    def get_total_route_length(self) -> int:
        """
        Calculate and return the total route length of the trip.

        This method sums up the route length from each action associated with the trip.

        Returns:
        -------
        int
            The total route length.
        """
        route_length = 0
        for ac in self.actions:
            # Assumes each action has a 'route' attribute with a 'length'
            # NOTE: Only 'move' actions have a route. If other action types are added, this method requires updating. 
            route_length += ac.route.length
        return route_length

    def update_instance_parameter(self, parameter: str, value: Any) -> None:
        """
        Update a given parameter of the trip instance.

        Parameters:
        ----------
        parameter : str
            The name of the parameter to update.
        value : any
            The new value for the parameter.
        """
        setattr(self, parameter, value)
        self.last_modified = datetime.now()

        if parameter == 'status' and self.vehicle is not None:
            # Also update status in the vehicle's schedule if applicable
            self.vehicle.schedule.loc[self.vehicle.schedule['task_id'] == self.id, 'status'] = value

    @classmethod
    def get_by_id(cls, id: str) -> Optional['Trip']:
        """
        Retrieve a trip instance by its unique identifier.

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
    def get_by_name(cls, name: str) -> Optional['Trip']:
        """
        Retrieve a trip instance by its name.

        Parameters:
        ----------
        name : str
            The name of the trip.

        Returns:
        -------
        Trip
            The trip instance with the specified name, or None if not found.
        """
        return next((trip for trip in cls._instances if trip.name == name), None)

    @classmethod
    def get_by_status(cls, status: str) -> List['Trip']:
        """
        Retrieve all trip instances with a given status.

        Parameters:
        ----------
        status : str
            The status to filter trips by.

        Returns:
        -------
        list
            A list of Trip instances with the specified status.
        """
        return [trip for trip in cls._instances if trip.status == status]

    @classmethod
    def get_all_trips(cls) -> List['Trip']:
        """
        Retrieve all trip instances.

        Returns:
        -------
        list
            A list of all Trip instances.
        """
        return cls._instances.copy()

    @classmethod
    def get_total_trips(cls) -> int:
        """
        Retrieve the total number of trip instances created.

        Returns:
        -------
        int
            The total number of trips.
        """
        return cls._total_instances

    @classmethod
    def delete_all_instances(cls) -> None:
        """
        Delete all trip instances.

        This method clears the list of trip instances and resets the total instances counter.
        """
        cls._instances.clear()
        cls._total_instances = 0

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
    name : str
        The name of the vehicle.
    vehicle_type : str
        The type of vehicle.
    fuel : str, optional
        The fuel type used by the vehicle.
    average_fuel_consumption : float, optional
        The average fuel consumption of the vehicle.
    emission_standard : str, optional
        The emission standard of the vehicle.
    load_capacities : dict, optional
        The load capacities of the vehicle. Default is 1.
    length : float, optional
        The length of the vehicle.
    height : float, optional
        The height of the vehicle.
    width : float, optional
        The width of the vehicle.
    license_plate : str, optional
        The license plate number of the vehicle.
    empty_weight : float, optional
        The empty weight of the vehicle.
    actors : list, optional
        The actors associated with the vehicle.
    sensors : list, optional
        The sensors associated with the vehicle.
    actions : list, optional
        The actions associated with the vehicle.
    marker : Folium.Marker, optional
        The Folium.Marker object for visualization on a map.
    status : str
        The current status of the vehicle (e.g., 'idle', 'move', 'wait', 'load', 'unload', 'charging', 'failed').
    average_speed : float
        The average speed of the vehicle in m/s.
    actual_speed : float
        The current speed of the vehicle in m/s.
    schedule : pd.DataFrame
        The schedule of the vehicle, with columns: ['vehicle','task_id','task_name','start','end','status'].
    current_trip : Trip, optional
        The trip currently being executed by the vehicle.
    current_action : int, optional
        The sequence number of the action currently being executed.
    load_time : float
        The expected load time (in seconds).
    unload_time : float
        The expected unload time (in seconds).
    co2_emission : float
        The CO2 emission of the vehicle (e.g., in g/km).
    nox_emission : float
        The NOx emission of the vehicle (e.g., in g/km).
    noise_pollution : float
        The noise pollution level (e.g., in dB).
    land_use : float
        The land use metric (e.g., in m³/hour).
    battery_capacity : float
        The battery capacity of the vehicle.
    energy_consumption_moving : float
        The energy consumption while moving.
    energy_consumption_idling : float
        The energy consumption while idling.
    battery_threshold : float
        The battery threshold level.
    charge_speed : float
        The charging speed.
    statistics : pd.DataFrame
        A DataFrame for recording periodic vehicle statistics.
    cum_statistics : pd.DataFrame
        A DataFrame for recording cumulative vehicle statistics.

    Class Methods:
    -------
    get_by_id(id: str) -> Vehicle
        Returns the vehicle instance matched by id.
    get_by_type(vehicle_type: str) -> List[Vehicle]
        Returns a list of vehicle instances matched by type.
    get_all_vehicles() -> List[Vehicle]
        Returns a list of all vehicle instances.
    delete_last_x(number: int) -> bool
        Deletes the last 'number' of vehicle instances.
    get_by_vehicle_name(name: str) -> Vehicle
        Returns the vehicle instance matched by name.
    get_schedules() -> pd.DataFrame
        Returns a list combining the schedules of all vehicles.
    get_total_vehicles() -> int
        Returns the total number of vehicles created.

    Example:
    -------
    vehicle = Vehicle(name=f"{type} {Vehicle.get_total_vehicles()}", vehicle_type="terminal_tractor")
    """

    _instances: list = []
    _total_instances: int = 0

    def __init__(self,
                 name: str = "",
                 vehicle_type: str = "",
                 fuel: Optional[str] = None,
                 average_fuel_consumption: Optional[float] = None,
                 emission_standard: Optional[str] = None,
                 load_capacities: Optional[dict] = 1, # Default value is 1
                 length: Optional[float] = None,
                 height: Optional[float] = None,
                 width: Optional[float] = None,
                 license_plate: Optional[str] = None,
                 empty_weight: Optional[float] = None,
                 actors: Optional[list['Actor']] = None,
                 sensors: Optional[list['Sensor']] = None,
                 actions: Optional[list['Action']] = None,
                 marker: Optional['Marker'] = None,
                 status: str = 'idle',
                 load_time: float = 0,
                 unload_time: float = 0,
                 co2_emission: float = 0,
                 nox_emission: float = 0,
                 noise_pollution: float = 0,
                 land_use: float = 0,
                 battery_capacity: float = 0,
                 energy_consumption_moving: float = 0,
                 energy_consumption_idling: float = 0,
                 battery_threshold: float = 0,
                 charge_speed: float = 0,
                 average_speed: float = (15/3.6)) -> None: # Default is 15km/h
        """
        Initialize a new Vehicle instance.

        Parameters:
        ----------
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
            The load capacities of the vehicle. Default is 1.
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
        status : str, optional
            The current status of the vehicle. Default is 'idle'.
        load_time : float, optional
            The load time (in seconds). Default is 0.
        unload_time : float, optional
            The unload time (in seconds). Default is 0.
        co2_emission : float, optional
            The CO2 emission (e.g., in g/km). Default is 0.
        nox_emission : float, optional
            The NOx emission (e.g., in g/km). Default is 0.
        noise_pollution : float, optional
            The noise pollution level (e.g., in dB). Default is 0.
        land_use : float, optional
            The land use metric (e.g., in m³/hour). Default is 0.
        battery_capacity : float, optional
            The battery capacity of the vehicle. Default is 0.
        energy_consumption_moving : float, optional
            The energy consumption while moving. Default is 0.
        energy_consumption_idling : float, optional
            The energy consumption while idling. Default is 0.
        battery_threshold : float, optional
            The battery threshold level. Default is 0.
        charge_speed : float, optional
            The charging speed. Default is 0.
        average_speed : float, optional
            The average speed of the vehicle in m/s. Default is 15/3.6.
        """

        # Core attributes
        self.id: str = str(uuid.uuid4())
        self.name: str = name
        self.creation_date: datetime = datetime.now()
        self.last_modified: datetime = datetime.now()
        self.vehicle_type: str = vehicle_type
        self.fuel: Optional[str] = fuel
        self.average_fuel_consumption: Optional[float] = average_fuel_consumption
        self.emission_standard: Optional[str] = emission_standard
        self.load_capacities: Optional[dict] = load_capacities
        self.length: Optional[float] = length
        self.height: Optional[float] = height
        self.width: Optional[float] = width
        self.license_plate: Optional[str] = license_plate
        self.empty_weight: Optional[float] = empty_weight
        self.actors: List['Actor'] = actors if actors is not None else []
        self.sensors: list['Sensor'] = sensors if sensors is not None else []
        self.actions: list['Action'] = actions if actions is not None else []

        # Custom attributes
        self.average_speed: float = average_speed  # in m/s
        self.actual_speed: float = self.average_speed # initialize as average speed
        self.marker: Optional['Marker'] = marker
        self.status: str = status
        self.load_time: float = load_time
        self.unload_time: float = unload_time
        self.co2_emission: float = co2_emission
        self.nox_emission: float = nox_emission
        self.noise_pollution: float = noise_pollution
        self.land_use: float = land_use
        self.battery_capacity: float = battery_capacity
        self.energy_consumption_moving: float = energy_consumption_moving
        self.energy_consumption_idling: float = energy_consumption_idling
        self.battery_threshold: float = battery_threshold
        self.charge_speed: float = charge_speed

        # Initialize schedule and statistics DataFrames
        self.schedule: pd.DataFrame = pd.DataFrame(columns=[
            'vehicle', 'task_id', 'task_name', 'start', 'end', 'status'
        ])
        self.current_trip: Optional['Trip'] = None
        self.current_action: Optional[int] = None  # sequence number of current action
        self.entries: int = 0
        self.exits: int = 0

        self.statistics: pd.DataFrame = pd.DataFrame(columns=[
            'timestamp',
            'id',
            'lat',
            'lng',
            'current_trip',
            'current_action',
            'status',
            'battery_level',
            'co2_emission',  # g/km
            'nox_emission',  # g/km
            'noise_pollution',  # dB
            'weight'
        ])
        self.cum_statistics: pd.DataFrame = pd.DataFrame(columns=[
            'timestamp',
            'id',
            'name',
            'time_in_system',   # seconds since initialization
            'move',             # % driving
            'wait',             # % waiting
            'load',             # % loading
            'unload',           # % unloading
            'idle',             # % idle
            'charging',         # % charging
            'failed',           # % failed
            'empty_move',       # % driving empty
            'full_move',        # % driving full
            'utilization',      # working %
            'travel_distance',  # kilometers driven
            'entries',          # total cargo loaded
            'exits',            # total cargo unloaded
            'energy_consumption',
            'co2_emission',     # g/km
            'nox_emission',     # g/km
            'noise_pollution',  # dB
            'land_use'          # m³/hour
        ])
        # Initialize cumulative statistics with starting values
        start_cum_stats = pd.DataFrame([{
            'timestamp': datetime.now(),
            'move': 0,
            'idle': 0,
            'load': 0,
            'unload': 0,
            'wait': 0,
            'charging': 0,
            'failed': 0,
            'empty_driving': 0,
            'full_driving': 0,
            'utilization': 0
        }])
        self.cum_statistics = pd.concat([self.cum_statistics, start_cum_stats], ignore_index=True)

        # Register the instance
        Vehicle._instances.append(self)
        Vehicle._total_instances += 1

    def assign_to_trip(self, trip: 'Trip') -> bool:
        """
        Assign the vehicle to a trip.

        Parameters:
        ----------
        trip : Trip
            The trip to which the vehicle will be assigned.

        Returns:
        -------
        bool
            True if the assignment was successful.

        Raises:
        ------
        ValueError:
            If the trip's status is not 'draft' or 'requested'.
        """

        if trip.status not in ['draft', 'requested']:
            raise ValueError("Invalid trip status: must be 'draft' or 'requested'")
        else:
            # Assign the vehicle to the trip
            trip.vehicle = self
            trip.status = 'requested'

            # Calculate expected duration based on actions in the trip
            expected_duration = 0
            for action in trip.actions:
                if action.action_type == 'load':
                    action.update_instance_parameter('duration', self.load_time)
                    expected_duration += action.duration
                elif action.action_type == 'unload':
                    action.update_instance_parameter('duration', self.unload_time)
                    expected_duration += action.duration
                elif action.action_type == 'move':
                    # NOTE: Assumes action.route.length is in meters
                    expected_duration += action.route.length / self.average_speed

            # Determine start and end times for the trip
            if self.schedule.empty:
                start = datetime.now()
                end = start + timedelta(seconds=expected_duration)
            elif self.current_trip is not None:
                start = self.schedule.iloc[-1]['end']
                end = start + timedelta(seconds=expected_duration)
            elif self.status not in ['charging', 'failed']:
                start = datetime.now()
                end = start + timedelta(seconds=expected_duration)
            else:
                # Fallback to current time if none of the conditions match
                start = datetime.now()
                end = start + timedelta(seconds=expected_duration)

            # Create a new task and add it to the schedule
            new_task = pd.DataFrame([{
                'vehicle': self.name,
                'task_id': trip.id,
                'task_name': trip.name,
                'start': start,
                'end': end,
                'status': trip.status
            }])
            self.schedule = pd.concat([self.schedule, new_task], ignore_index=True)
            self.last_modified = datetime.now()
            return True

    def get_start_time_trip(self, trip_id: str) -> 'datetime':
        """
        Retrieve the start time for a given trip from the vehicle's schedule.

        Parameters:
        ----------
        trip_id : str
            The ID of the trip.

        Returns:
        -------
        datetime
            The start time of the trip.

        Raises:
        ------
        ValueError:
            If the trip_id is not found in the schedule.
        """
        start_values = self.schedule.loc[self.schedule['task_id'] == trip_id, 'start'].values
        if len(start_values) > 0:
            return start_values[0]
        else:
            raise ValueError(f"Could not find trip_id {trip_id} in the schedule of vehicle {self.name}")

    def update_instance_parameter(self, parameter: str, value: any) -> None:
        """
        Update the parameter of this vehicle instance to a new value.

        Parameters:
        ----------
        parameter : str
            The name of the parameter to update.
        value : any
            The new value for the parameter.
        """
        setattr(self, parameter, value)
        self.last_modified = datetime.now()

    @classmethod
    def get_by_id(cls, id: str) -> Optional['Vehicle']:
        """
        Retrieve the vehicle instance with the specified UUID.

        Parameters:
        ----------
        id : str
            The UUID of the vehicle.

        Returns:
        -------
        Vehicle
            The matching vehicle instance, or None if not found.
        """
        return next((v for v in cls._instances if v.id == id), None)

    @classmethod
    def get_by_type(cls, vehicle_type: str) -> list:
        """
        Retrieve all vehicles of a specified type.

        Parameters:
        ----------
        vehicle_type : str
            The vehicle type to filter by.

        Returns:
        -------
        list
            A list of vehicle instances matching the specified type.
        """
        return [v for v in cls._instances if v.vehicle_type == vehicle_type]

    @classmethod
    def get_all_vehicles(cls) -> list:
        """
        Retrieve all vehicle instances.

        Returns:
        -------
        list
            A list of all vehicles.
        """
        return cls._instances.copy()

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
            True if deletion was successful, False otherwise.
        """
        if len(cls._instances) >= number:
            cls._instances = cls._instances[:-number]
            return True
        else:
            return False

    @classmethod
    def get_by_vehicle_name(cls, name: str) -> Optional['Vehicle']:
        """
        Retrieve the vehicle instance with the specified name.

        Parameters:
        ----------
        name : str
            The name of the vehicle.

        Returns:
        -------
        Vehicle
            The matching vehicle instance, or None if not found.
        """
        return next((v for v in cls._instances if v.name == name), None)

    @classmethod
    def get_schedules(cls) -> 'pd.DataFrame':
        """
        Retrieve a combined schedule of all vehicles.

        Returns:
        -------
        pd.DataFrame
            A DataFrame containing the concatenated schedules of all vehicles.
        """
        if not cls._instances:
            return pd.DataFrame()
        schedules = cls._instances[0].schedule.copy()
        for vehicle in cls._instances[1:]:
            schedules = pd.concat([schedules, vehicle.schedule])
        return schedules

    @classmethod
    def get_total_vehicles(cls) -> int:
        """
        Retrieve the total number of vehicles created.

        Returns:
        -------
        int
            The total number of vehicles.
        """
        return cls._total_instances