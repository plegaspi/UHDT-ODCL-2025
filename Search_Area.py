import math
from shapely.geometry import Polygon, Point
from pyproj import Transformer
import offline_folium
import folium
import json
import math


def haversine_distance(point1, point2):
    # Earth radius in meters
    R = 6371000

    lat1, lon1 = point1
    lat2, lon2 = point2

    # Convert latitude and longitude from degrees to radians.
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2) ** 2 +
         math.cos(phi1) * math.cos(phi2) *
         math.sin(delta_lambda / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c
    return distance

def calculate_total_distance(waypoints):
    total_distance = 0.0
    if len(waypoints) < 2:
        return total_distance  # No distance if fewer than 2 points.
    
    for i in range(1, len(waypoints)):
        total_distance += haversine_distance(waypoints[i-1], waypoints[i])
    
    return total_distance

def rotate_point_local(point, angle):
    x, y = point
    return (x * math.cos(angle) - y * math.sin(angle),
            x * math.sin(angle) + y * math.cos(angle))


def plan_mission(airdrop_coords, photo_width_px, photo_height_px,
                                                horizontal_fov_deg, vertical_fov_deg, overlap_percent,
                                                altitude=100):
    h_fov_rad = math.radians(horizontal_fov_deg)
    v_fov_rad = math.radians(vertical_fov_deg)
    ground_width = 2 * altitude * math.tan(h_fov_rad / 2)    # meters
    ground_height = 2 * altitude * math.tan(v_fov_rad / 2)     # meters
    print(ground_width, ground_height)
    
    step_x = ground_width * (1 - overlap_percent / 100.0)
    step_y = ground_height * (1 - overlap_percent / 100.0)
    

    airdrop_coords_lonlat = [(lon, lat) for lat, lon in airdrop_coords]
    area_polygon = Polygon(airdrop_coords_lonlat)
    centroid = area_polygon.centroid
    lon0, lat0 = centroid.x, centroid.y
    utm_zone = math.floor((lon0 + 180) / 6) + 1
    is_northern = (lat0 >= 0)
    proj_str = (f"+proj=utm +zone={utm_zone} +{'north' if is_northern else 'south'} "
                "+ellps=WGS84 +datum=WGS84 +units=m +no_defs")
    transformer_to_utm = Transformer.from_crs("epsg:4326", proj_str, always_xy=True)
    transformer_from_utm = Transformer.from_crs(proj_str, "epsg:4326", always_xy=True)
    
    utm_polygon_coords = [transformer_to_utm.transform(lon, lat) for lon, lat in airdrop_coords_lonlat]
    utm_polygon = Polygon(utm_polygon_coords)
    print(f"Airdrop Area: {utm_polygon.area}")
    

    min_rect = utm_polygon.minimum_rotated_rectangle
    rect_points = list(min_rect.exterior.coords)[:4]  # 4 distinct corners
    
    
    max_length = 0
    angle = 0
    for i in range(4):
        p1 = rect_points[i]
        p2 = rect_points[(i+1)%4]
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        length = math.hypot(dx, dy)
        if length > max_length:
            max_length = length
            angle = math.atan2(dy, dx)

    def rotate(point, angle, origin=(0, 0)):
        ox, oy = origin
        px, py = point
        qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
        qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
        return (qx, qy)
    

    rect_centroid = Polygon(rect_points).centroid.coords[0]
    

    utm_polygon_rot = [rotate(p, -angle, origin=rect_centroid) for p in utm_polygon_coords]
    polygon_rot = Polygon(utm_polygon_rot)
    min_x, min_y, max_x, max_y = polygon_rot.bounds
    

    half_w = ground_width / 2.0
    half_h = ground_height / 2.0
    start_x_center = min_x + half_w
    start_y_center = min_y + half_h
    
    width_rot = max_x - min_x
    if width_rot <= ground_width:
        n_cols = 1
    else:
        n_cols = math.ceil((width_rot - ground_width) / step_x) + 1
        
    height_rot = max_y - min_y
    if height_rot <= ground_height:
        n_rows = 1
    else:
        n_rows = math.ceil((height_rot - ground_height) / step_y) + 1
    
    grid_cols = []
    for i in range(n_cols):
        col = []
        for j in range(n_rows):
            x = start_x_center + i * step_x
            y = start_y_center + j * step_y
            col.append((x, y))

        if i % 2 == 1:
            col.reverse()
        grid_cols.append(col)
    
    grid_points_rot = [pt for col in grid_cols for pt in col]
    
   
    grid_points_utm = [rotate(pt, angle, origin=rect_centroid) for pt in grid_points_rot]
    gps_waypoints = []
    for (xx, yy) in grid_points_utm:
        lon, lat = transformer_from_utm.transform(xx, yy)
        gps_waypoints.append((lat, lon))
    
    return (gps_waypoints, angle, rect_centroid, transformer_to_utm,
            transformer_from_utm, ground_width, ground_height, n_cols, n_rows)

def save_to_mission_planner_file(waypoints, altitude, filename="mission.waypoints", reverse=False):
    if reverse:
        waypoints = list(reversed(waypoints))
    
    with open(filename, 'w') as f:
        f.write("QGC WPL 110\n")
        for i, (lat, lon) in enumerate(waypoints):
            f.write(f"{i}\t0\t3\t16\t0\t0\t0\t0\t{lat:.7f}\t{lon:.7f}\t{altitude:.2f}\t1\n")
    
    print(f"Saved Mission Planner file as '{filename}' ({'reversed' if reverse else 'normal'} order)")

def export_search_area_waypoints(search_waypoints, filepath):

    search_waypoint_object = {
        "search_waypoints": search_waypoints
    }

    with open(filepath, "w") as f:
        json.dump(search_waypoint_object, f, indent=4)
    
    print(f"Saved waypoints to {filepath}")

def export_map(map_file_path, boundary_coords, drone_waypoints, flight_altitude, angle, rect_centroid, transformer_to_utm, transformer_from_utm, ground_width, ground_height, n_cols, n_rows, is_reversed):
    center_lat = sum(pt[0] for pt in boundary_coords) / len(boundary_coords)
    center_lon = sum(pt[1] for pt in boundary_coords) / len(boundary_coords)

    print(f"Grid: {n_cols} columns, {n_rows} rows")
    print(f"Total waypoints: {len(drone_waypoints)}")
    total = calculate_total_distance(drone_waypoints)
    print(f"Total distance traveled: {total:.2f} meters")


    mission_map = folium.Map(location=[center_lat, center_lon], zoom_start=18)


    folium.PolyLine(locations=boundary_coords, color='red', weight=2.5, opacity=1).add_to(mission_map)
    for coord in boundary_coords:
        folium.CircleMarker(location=coord, radius=4, color='red', fill=True).add_to(mission_map)

    if (is_reversed):
        drone_waypoints = list(reversed(drone_waypoints))
    for idx, wp in enumerate(drone_waypoints):
        print(f"({wp[0]}, {wp[1]}, {flight_altitude}),")
        folium.Marker(location=wp, popup=f"WP {idx+1}",
                    icon=folium.Icon(color='blue', icon='info-sign')).add_to(mission_map)
        

    folium.PolyLine(locations=drone_waypoints, color='blue', weight=2.5, opacity=1).add_to(mission_map)


    half_width_val = ground_width / 2.0
    half_height_val = ground_height / 2.0
    local_corners = [
        (-half_width_val, -half_height_val),
        ( half_width_val, -half_height_val),
        ( half_width_val,  half_height_val),
        (-half_width_val,  half_height_val)
    ]

    for wp in drone_waypoints:
        wp_utm = transformer_to_utm.transform(wp[1], wp[0])
        footprint_utm = []
        for corner in local_corners:
            rotated = rotate_point_local(corner, angle)
            corner_utm = (wp_utm[0] + rotated[0], wp_utm[1] + rotated[1])
            footprint_utm.append(corner_utm)
        footprint_utm.append(footprint_utm[0])
        
        footprint_gps = []
        for x, y in footprint_utm:
            lon, lat = transformer_from_utm.transform(x, y)
            footprint_gps.append((lat, lon))
        
        folium.Polygon(locations=footprint_gps, color='green', weight=1.5,
                    opacity=0.8, fill=True, fill_opacity=0.2).add_to(mission_map)


    save_to_mission_planner_file(drone_waypoints, flight_altitude)
    mission_map.save(map_file_path)
    print(f"Map saved as 'f{map_file_path}'.")

if __name__ == "__main__":
    from Config import Config
    from OPM2 import calculate_default_drop_coordinates, sort_coordinates
    config = Config("config/config.yaml")

    bound1 = config.params["airdrop"]["boundary"]["bound_1"]
    bound2 = config.params["airdrop"]["boundary"]["bound_2"]
    bound3 = config.params["airdrop"]["boundary"]["bound_3"]
    bound4 = config.params["airdrop"]["boundary"]["bound_4"]
    default_drop_coordinates = calculate_default_drop_coordinates(sort_coordinates([bound1, bound2, bound3, bound4]))


    # Mission parameters:
    photo_width = 7728       # pixels 
    photo_height = 5152      # pixels 
    horizontal_fov = 30.493403035878764  # degrees
    vertical_fov = 20.469605526846422     # degrees
    overlap = 20              # % overlap
    flight_altitude = 22.5   # meters
    is_reversed = True
    waypoint_save_path = "/home/uhdt/ws2_livox/waypoints.json"


    boundary_coords = [bound1, bound2, bound3, bound4, bound1]

    center_lat = sum(pt[0] for pt in boundary_coords) / len(boundary_coords)
    center_lon = sum(pt[1] for pt in boundary_coords) / len(boundary_coords)

    (drone_waypoints, angle, rect_centroid, transformer_to_utm, transformer_from_utm,
    ground_width, ground_height, n_cols, n_rows) = plan_mission(
        boundary_coords, photo_width, photo_height, horizontal_fov, vertical_fov, overlap,
        altitude=flight_altitude
    )

    print(f"Grid: {n_cols} columns, {n_rows} rows")
    print(f"Total waypoints: {len(drone_waypoints)}")
    total = calculate_total_distance(drone_waypoints)
    print(f"Total distance traveled: {total:.2f} meters")


    mission_map = folium.Map(location=[center_lat, center_lon], zoom_start=18)


    folium.PolyLine(locations=boundary_coords, color='red', weight=2.5, opacity=1).add_to(mission_map)
    for coord in boundary_coords:
        folium.CircleMarker(location=coord, radius=4, color='red', fill=True).add_to(mission_map)

    if (is_reversed):
        drone_waypoints = list(reversed(drone_waypoints))
    for idx, wp in enumerate(drone_waypoints):
        print(f"({wp[0]}, {wp[1]}, {flight_altitude}),")
        folium.Marker(location=wp, popup=f"WP {idx+1}",
                    icon=folium.Icon(color='blue', icon='info-sign')).add_to(mission_map)
        

    folium.PolyLine(locations=drone_waypoints, color='blue', weight=2.5, opacity=1).add_to(mission_map)


    half_width_val = ground_width / 2.0
    half_height_val = ground_height / 2.0
    local_corners = [
        (-half_width_val, -half_height_val),
        ( half_width_val, -half_height_val),
        ( half_width_val,  half_height_val),
        (-half_width_val,  half_height_val)
    ]

    for wp in drone_waypoints:
        wp_utm = transformer_to_utm.transform(wp[1], wp[0])
        footprint_utm = []
        for corner in local_corners:
            rotated = rotate_point_local(corner, angle)
            corner_utm = (wp_utm[0] + rotated[0], wp_utm[1] + rotated[1])
            footprint_utm.append(corner_utm)
        footprint_utm.append(footprint_utm[0])
        
        footprint_gps = []
        for x, y in footprint_utm:
            lon, lat = transformer_from_utm.transform(x, y)
            footprint_gps.append((lat, lon))
        
        folium.Polygon(locations=footprint_gps, color='green', weight=1.5,
                    opacity=0.8, fill=True, fill_opacity=0.2).add_to(mission_map)

    # Call this function using your drone waypoints
    save_to_mission_planner_file(drone_waypoints, flight_altitude)
    mission_map.save('mission_waypoints.html')
    export_search_area_waypoints(drone_waypoints, waypoint_save_path)
    print("Map saved as 'mission_waypoints.html'.")