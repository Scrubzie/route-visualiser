"""
Driver code to visualise routing data for testing purposes

Arguments
---------
1. The name of the JSON file in src/data containing RouteInput data
2. the name of the JSON file in src/data containing the optimal routes per vehicle

Example:

When in src directory (cd src), assuming you have a src/data folder containing all the objects, call
- python main.py "Locations.json" "Locations_route.json"
"""

import json
import sys
import os
import numpy as np
import matplotlib.pyplot as plt
import er_projection as erp

from pydantic_models import RouteInput

def plot_graph() -> None:
    """
    Visualise locations and routes

    Arguments
    ---------
    1. The name of the JSON file in src/data containing RouteInput data
    2. the name of the JSON file in src/data containing the optimal routes per vehicle

    Example:

    When in src directory (cd src), assuming you have a src/data folder containing all the objects, call
    - python3 visualise_deliveries.py "Locations.json" "Locations_route.json"
    """
    locations_path = os.path.join("data", sys.argv[1])
    routes_path = os.path.join("data", sys.argv[2])

    lats, longs, orders, routes = reformat(locations_path,routes_path)

    plt.figure(figsize=(10, 6))
    plt.scatter(longs, lats, color='blue', marker='o')
    __add_lines(routes, orders)
    plt.title('Equirectangular Projection Scatter Plot')
    plt.xlabel('Longitude (km)')
    plt.ylabel('Latitude (km)')
    plt.grid(True)
    plt.show()

def reformat(locations_path: str, routes_path: str) -> tuple[np.array, np.array, dict[int, dict[str, float]], list[list[int]]]:
    """
    Extracts the latitudes, longitudes, locations and routes
    from the JSON files

    Parameters
    ----------
    locations_path : str
        The name of the locations file at src/data
        The file should be in the format of RouteInput
    routes_path : routes
        the name of the routes file at src/data
        The file should be a list of lists containing ordered Order_ids

    Returns
    -------
    lats : np.array
        List of latitudes for orders 
    longs : np.array
        List of latitudes for orders
    orders : dict[int, dict[str,float]]
        Key represents order_id
        Value (inner dictionary) is in the format of:
            lat: float
            lon: float
        Example: {16: {'lat': -31.899364, 'lon': 115.801288}
    routes : list[list[int]]
        Contains a list of lists of routes in sorted order
        Outer lists contains the list of routes
        Inner list contains the orders in sorted order
    """
    with open(locations_path, 'r', encoding='utf-8') as file:
        locations = json.load(file)
    with open(routes_path, 'r', encoding='utf-8') as file:
        routes = json.load(file)

    locations = RouteInput(**locations)
    lats = [location.lat for location in locations.orders]
    longs = [location.lon for location in locations.orders]
    lats, longs = erp.equi_rect_project(lats, longs)
    orders = {order.order_id: {'lat': order.lat, 'lon': order.lon} for order in locations.orders}

    return lats, longs, orders, routes

def __add_lines(routes: list[list[int]], orders_dict: dict[int, dict[str, float]]) -> None:
    """
    Adds arrows for each edge in routes list

    Parameters
    ----------
    routes : list[list[int]]
        Contains a list of lists of routes in sorted order
        Outer lists contains the list of routes
        Inner list contains the orders in sorted order
    orders_dict : dict[int, dict[str,float]]
        Key represents order_id
        Value (inner dictionary) is in the format of:
            lat: float
            lon: float
        Example: {16: {'lat': -31.899364, 'lon': 115.801288}
    """
    start_longs = []
    start_lat = []
    end_longs = []
    end_lats = []
    for route in routes:
        for i in range(len(route) - 1):
            start_id = route[i]
            end_id = route[i + 1]

            start_longs.append(orders_dict[start_id]['lon'])
            start_lat.append(orders_dict[start_id]['lat'])
            end_longs.append(orders_dict[end_id]['lon'])
            end_lats.append(orders_dict[end_id]['lat'])

    start_lats, start_longs = erp.equi_rect_project(start_lat, start_longs)
    end_lats, end_longs = erp.equi_rect_project(end_lats, end_longs)

    for i in range(len(start_lats)):
        plt.annotate('', xy=(end_longs[i], end_lats[i]), xytext=(start_longs[i], start_lats[i]),
                 arrowprops=dict(facecolor='red', shrink=0.15, headlength=7, headwidth=7, width=3))

if __name__ == "__main__":
    plot_graph()
