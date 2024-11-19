import osmnx as ox
import math

def get_graph_from_place(q,network_type="drive"):
    # download/model a street network 
    G = ox.graph_from_place(q, network_type=network_type)

    # impute missing edge speeds and calculate edge travel times with the speed module
    G = ox.routing.add_edge_speeds(G)
    G = ox.routing.add_edge_travel_times(G)
    return G

def get_nearest_nodes(G,origin, destination):
    # get the nearest network nodes to two lat/lng points with the distance module
    orig = ox.distance.nearest_nodes(G, Y=origin[0], X=origin[1])
    dest = ox.distance.nearest_nodes(G, Y=destination[0], X=destination[1])

    return [orig, dest]

# find the shortest path between two Locations by minimizing travel time
def get_shortest_path(G,orig,dest,weight="travel_time"):

    # Convert orig and dest to nodes known to OSM
    nodes = get_nearest_nodes(G,orig,dest)

    # Calculate route
    route = ox.shortest_path(G, nodes[0], nodes[1], weight=weight)

    return route


def get_route_length(G,route):
    # how long is our route in meters?
    edge_lengths = ox.routing.route_to_gdf(G, route)["length"]
    return round(sum(edge_lengths))

def get_coordinates(G,nodes):
    latitudes = []
    longitudes = []
    for node in nodes:
        # Get the node's data
        node_data = G.nodes[node]
        
        # Extract the coordinates
        latitude = node_data['y']
        longitude = node_data['x']
        latitudes.append(latitude)
        longitudes.append(longitude)


    return [(point[0], point[1]) for point in zip(latitudes,longitudes)]

def haversine(coord1, coord2):
    R = 6371000  # radius of Earth in meters
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    phi_1 = math.radians(lat1)
    phi_2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi_1) * math.cos(phi_2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    meters = R * c  # output distance in meters
    return meters

# Function to get the interpolated position along the polyline
def get_interpolated_position(polyline, progress):
    if progress >= 100:
        return polyline[-1]
    
    total_length = sum(haversine(polyline[i], polyline[i + 1]) for i in range(len(polyline) - 1))
    target_distance = total_length * progress/100
    distance_covered = 0

    for i in range(len(polyline) - 1):
        segment_length = haversine(polyline[i], polyline[i + 1])
        if distance_covered + segment_length >= target_distance:
            segment_progress = (target_distance - distance_covered) / segment_length
            lat = polyline[i][0] + segment_progress * (polyline[i + 1][0] - polyline[i][0])
            lon = polyline[i][1] + segment_progress * (polyline[i + 1][1] - polyline[i][1])
            return (lat, lon)
        distance_covered += segment_length
    
    return polyline[-1]