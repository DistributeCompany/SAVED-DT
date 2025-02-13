import streamlit as st 


st.markdown(
'''    
# System Classes Overview

This system is designed according to the [Open Trip Model (OTM5)](https://otm5.opentripmodel.org/) specification. It models key entities and operations on the XL Businesspark Almelo.

---

## Action

**Purpose:**  
Represents an operational step within a trip (e.g., 'move', 'load', 'unload'). In the current model, the only supported action type is **move**, which captures the process of moving a vehicle along a route between two locations.

**Key Attributes:**
- **Action Type & Lifecycle:**  
  Indicates that the action is a "move" and tracks its status (e.g., *requested*, *planned*, *actual*).
- **Timing & Routing:**  
  Records start and end times and links the action to a specific route that the vehicle follows.
- **Associations:**  
  Each action is part of a trip and defines both an origin and a destination location.

---

## Actor

**Purpose:**  
Models a stakeholder in the system (e.g., Bolk, CTT, Timberland)

**Key Attributes:**
- **Identification:**  
  Each actor has a unique identifier and a name.
- **Location Association:**  
  Actors are linked to one or more locations.

---

## Constraint

**Purpose:**  
Intended to model business rules, operational limits, and other constraints. It is currently not yet implemented, but will eventually handle conditions like vehicle capacity limits, routing restrictions, and time-window restrictions according to OTM5 standard.

---

## Goods

**Purpose:**  
Represents items or transport equipment involved in the logistics process. This class is designed for future extensions and can model:
- **Transport Equipment:**  
  Equipment such as trailers, boxes, load carriers, or pallets used for transporting cargo.
- **Items:**  
  Individual goods or products being shipped.

*Note: Although not actively used in the current implementation, this class provides the foundation for modeling e.g., the chassis behind the vehicle.*

---

## Location

**Purpose:**  
Represents a geographical point using latitude and longitude coordinates. Locations serve as origins or destinations.

**Key Attributes:**
- **Coordinates:**  
  The [latitude, longitude] pair uniquely defines the location.
- **Type:**  
  Used to describe the type of location, e.g., Entrance, Dock, Temporary Parking, Loading Lane, Tractor Parking. 
- **Visualization:**  
  Locations are visualized on maps using markers.

---

## Route

**Purpose:**  
Captures the path that a vehicle takes between two locations.

**Key Attributes:**
- **Geospatial Data:**  
  A series of coordinates (a polyline) that define the travel path.
- **Measurement:**  
  Includes the total route length and the specific network nodes (derived from OSMnx).
- **Visualization:**  
  The route can be rendered on a map, providing a visual context for navigation and planning (select the trip in the Detailed Trip View table).

---

## Sensor  

**Purpose:**  
Placeholder class. Not yet implemented, but probably required for further development towards a Digital Shadow. Caputures data from real-life on-vehicle or on-site sensors (e.g., GPS, camera feeds, ...)

---

## Trip

**Purpose:**  
Models a transport trip. A trip represents the entire process of transporting goods from an origin to a destination (possibly via other locations).

**Key Attributes:**
- **Identification & Status:**  
  Each trip has a unique identifier, a name, and a status (e.g., *draft*, *requested*, *completed*) that reflects its current stage.
- **Mode of Transport:**  
  Records the method of transportation (such as road, rail, air, or maritime). Road is only relevant for now. 
- **Associations:**  
  Links the trip with a vehicle, a series of actions, and involved actors.
- **Metrics:**  
  Calculates overall route length and tracks progress throughout the journey.

---

## Vehicle

**Purpose:**  
Represents the (autonomous) terminal tractors in the system.

**Key Attributes:**
- **Identification & Specifications:**  
  Each vehicle is uniquely identified and characterized by its name, type, dimensions, fuel type, emissions data, and load capacities.
- **Performance Metrics:**  
  Tracks information such as average speed, fuel consumption, battery capacity, and various operational statistics (e.g., moving time, idle time).
- **Operational Status & Scheduling:**  
  Maintains a real-time schedule and cumulative statistics.
- **Associations:**  
  A vehicle is linked to trips and actions.


# Known Issues

- The Digital Model does not continue when switching between the tabs in the sidebar. Stay in the Digital Model for now. 
- The osmnx library is used to calculate routes between two points on the map. This typically results in a very rough route, as osmnx is not very detailled on XL Businesspark Almelo. Route generation should be replaced with more detailled routes (e.g., polylines) between all possible origin-destination pairs. This information may come from simulations of the autonomous vehicle carried out by HAN Automative Research. 
- The model crashes when trying to create a trip between two locations very close by. It cannot compute a route using the osmnx library. Restart Streamlit to recover. 

''',
unsafe_allow_html=True
)