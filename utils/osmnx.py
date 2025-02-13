"""
Module for retrieving and processing street network graphs using OSMnx,
and for calculating routes, distances, and (interpolated) vehicle positions.
"""

import osmnx as ox
import math
import pandas as pd
from typing import List, Tuple, Any

def get_graph_from_place(query: str, network_type: str = "drive") -> Any:
    """
    Download and model a street network for a given place.

    Parameters
    ----------
    query : str
        The place query (e.g., "Los Angeles, California, USA").
    network_type : str, optional
        The type of network to retrieve (default is "drive").

    Returns
    -------
    networkx.MultiDiGraph
        The street network graph.
    """
    G = ox.graph_from_place(query, network_type=network_type)

    # Add edge speeds and calculate edge travel times
    G = ox.routing.add_edge_speeds(G)
    G = ox.routing.add_edge_travel_times(G)
    return G

def get_nearest_nodes(G: Any, origin: Tuple[float, float], destination: Tuple[float, float]) -> List[int]:
    """
    Get the nearest network nodes to the specified origin and destination coordinates.

    Parameters
    ----------
    G : networkx.MultiDiGraph
        The street network graph.
    origin : tuple of float
        The (latitude, longitude) for the origin.
    destination : tuple of float
        The (latitude, longitude) for the destination.

    Returns
    -------
    list of int
        The nearest node IDs for origin and destination.
    """
    orig = ox.distance.nearest_nodes(G, Y=origin[0], X=origin[1])
    dest = ox.distance.nearest_nodes(G, Y=destination[0], X=destination[1])
    return [orig, dest]

def get_shortest_path(G: Any, orig: Tuple[float, float], dest: Tuple[float, float], weight: str = "travel_time") -> List[int]:
    """
    Calculate the shortest path between two locations by minimizing the specified weight.

    # NOTE: A modification is to use a scenario-based approach for autonomous vehicles, instead of 'shortest travel time' or 'shortest distance'.

    In this approach,  we express a route in terms ISO 34504:2024 scenarios. 
    Based on the capabilities of the vehicle, we 'maximize' the expected value the vehicle can properly drive the route. 
    Other parameters could include, 'safety', e.g., to avoid mixed-traffic situations. 

    This approach is currently in the concept-phase. All edges/nodes should reflect these scenario, and the 'weight' parameter might be used. 
    It is further developed in a seperate project, ask b.gerrits@distribute.company for more information. 

    Parameters
    ----------
    G : networkx.MultiDiGraph
        The street network graph.
    orig : tuple of float
        The (latitude, longitude) for the origin.
    dest : tuple of float
        The (latitude, longitude) for the destination.
    weight : str, optional
        The edge attribute to minimize (default is "travel_time").

    Returns
    -------
    list of int
        A list of node IDs representing the shortest path.
    """
    nodes = get_nearest_nodes(G, orig, dest)
    route = ox.shortest_path(G, nodes[0], nodes[1], weight=weight)
    return route

def get_route_length(G: Any, route: List[int]) -> int:
    """
    Calculate the total length of a route in meters.

    Parameters
    ----------
    G : networkx.MultiDiGraph
        The street network graph.
    route : list of int
        A list of node IDs representing the route.

    Returns
    -------
    int
        The total route length (rounded to the nearest meter).
    """
    edge_lengths = ox.routing.route_to_gdf(G, route)["length"]
    return round(sum(edge_lengths))

def get_coordinates(G: Any, nodes: List[int]) -> List[Tuple[float, float]]:
    """
    Get the (latitude, longitude) coordinates for a list of nodes.

    Parameters
    ----------
    G : networkx.MultiDiGraph
        The street network graph.
    nodes : list of int
        A list of node IDs.

    Returns
    -------
    list of tuple of float
        A list of (latitude, longitude) tuples.
    """
    return [(G.nodes[node]['y'], G.nodes[node]['x']) for node in nodes]

def haversine(coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
    """
    Calculate the great-circle distance between two points on Earth.

    Parameters
    ----------
    coord1 : tuple of float
        The (latitude, longitude) of the first point.
    coord2 : tuple of float
        The (latitude, longitude) of the second point.

    Returns
    -------
    float
        The distance between the two points in meters.
    """
    R = 6371000  # Earth's radius in meters
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def get_interpolated_position(polyline: List[Tuple[float, float]], progress: float) -> Tuple[float, float]:
    """
    Compute the interpolated position along a polyline based on a progress percentage.

    Parameters
    ----------
    polyline : list of tuple of float
        A list of (latitude, longitude) tuples describing the polyline.
    progress : float
        The progress percentage (0 to 100) along the polyline.

    Returns
    -------
    tuple of float
        The interpolated (latitude, longitude) position along the polyline.
    """
    if progress >= 100:
        return polyline[-1]

    total_length = sum(haversine(polyline[i], polyline[i + 1]) for i in range(len(polyline) - 1))
    target_distance = total_length * (progress / 100)
    distance_covered = 0.0

    for i in range(len(polyline) - 1):
        segment_length = haversine(polyline[i], polyline[i + 1])
        if distance_covered + segment_length >= target_distance:
            segment_progress = (target_distance - distance_covered) / segment_length
            lat = polyline[i][0] + segment_progress * (polyline[i + 1][0] - polyline[i][0])
            lon = polyline[i][1] + segment_progress * (polyline[i + 1][1] - polyline[i][1])
            return (lat, lon)
        distance_covered += segment_length

    return polyline[-1]
