import math

def Georeference(drone_latitude, drone_longitude, drone_altitude, drone_yaw, target_pixel_coordinates):
    # Constants
    pixel_resolution = (6000, 4000)
    
    # Camera field of view = 2*arctan(sensor_size/(2*focal_length))
    horizontal_fov = 27.0 # degrees
    vertical_fov = 18.0 # degrees

    # Image real-world dimensions
    image_width = 2 * drone_altitude * math.tan(math.radians(horizontal_fov / 2))
    image_height = 2 * drone_altitude * math.tan(math.radians(vertical_fov / 2))

    # Drone orientation
    drone_yaw_rad = math.radians(drone_yaw)

    # Target pixel coordinates
    target_pixel_x, target_pixel_y = target_pixel_coordinates

    # Image center coordinates
    image_center_x = pixel_resolution[0] / 2
    image_center_y = pixel_resolution[1] / 2

    # Calculate distance from image center to target pixel
    delta_x = target_pixel_x - image_center_x
    delta_y = target_pixel_y - image_center_y

    # Calculate distance from image center to target pixel after correction
    corrected_delta_x = delta_x * math.cos(drone_yaw_rad) - delta_y * math.sin(drone_yaw_rad)
    corrected_delta_y = delta_x * math.sin(drone_yaw_rad) + delta_y * math.cos(drone_yaw_rad)

    # Calculate new target pixel coordinates after adjustment
    corrected_target_pixel_x = image_center_x + corrected_delta_x
    corrected_target_pixel_y = image_center_y + corrected_delta_y

    # Calculate target coordinates in meters (assuming linear relationship)
    x_meters = (corrected_target_pixel_x - image_center_x) * image_width / pixel_resolution[0]
    y_meters = (corrected_target_pixel_y - image_center_y) * image_height / pixel_resolution[1]

    # Convert drone-centric coordinates to global coordinates
    target_latitude = drone_latitude + (y_meters / 111319.944)
    target_longitude = drone_longitude + (x_meters / (111319.944 * math.cos(math.radians(drone_latitude))))

    return abs(target_latitude), abs(target_longitude)*-1

#Return Distance Between Two GPS points in meters
def haversine(lat1, lon1, lat2, lon2):

    # convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    radius = 6371 # Radius of earth in kilometers. Use 3956 for miles
    distance = radius * c * 1000 # Convert to meters

    return distance